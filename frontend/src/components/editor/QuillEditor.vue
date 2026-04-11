<!-- Quill 富文本图片上传 -->
<!-- src/components/editor/QuillEditor.vue -->
<template>
  <div
    ref="editorRef"
    class="quill-container"
  ></div>

  <teleport to="body">
    <div
      v-if="sizeDialogVisible"
      class="image-size-dialog-backdrop"
      @click="closeImageSizeDialog"
    >
      <div
        class="image-size-dialog"
        @click.stop
      >
        <div class="image-size-dialog-title">Image size</div>

        <div class="image-size-mode-group">
          <button
            type="button"
            class="image-size-mode-btn"
            :class="{ active: sizeDialogMode === 'width' }"
            @click="sizeDialogMode = 'width'"
          >
            Width
          </button>
          <button
            type="button"
            class="image-size-mode-btn"
            :class="{ active: sizeDialogMode === 'height' }"
            @click="sizeDialogMode = 'height'"
          >
            Height
          </button>
        </div>

        <input
          v-model="sizeDialogValue"
          class="image-size-input"
          :placeholder="
            sizeDialogMode === 'width'
              ? 'Enter width: 300 / 300px / auto'
              : 'Enter height: 200 / 200px / auto'
          "
          @keydown.enter.prevent="submitImageSizeDialog"
        />

        <div
          v-if="sizeDialogError"
          class="image-size-error"
        >
          {{ sizeDialogError }}
        </div>

        <div class="image-size-actions">
          <button
            type="button"
            class="image-size-action ghost"
            @click="closeImageSizeDialog"
          >
            Cancel
          </button>
          <button
            type="button"
            class="image-size-action primary"
            @click="submitImageSizeDialog"
          >
            Apply
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
  import { uploadRichImage } from '@/services/admin/company'
  import Quill from 'quill'
  import { ImageResize } from 'quill-image-resize-module-ts'
  import 'quill/dist/quill.snow.css'
  import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

  interface Props {
    modelValue: string
    modules?: any
  }
  const props = defineProps<Props>()

  const emit = defineEmits<{
    (e: 'update:modelValue', v: string): void
  }>()

  const editorRef = ref<HTMLDivElement | null>(null)
  let quill: InstanceType<typeof Quill> | null = null
  let editorHost: HTMLDivElement | null = null
  let imageResizeRegistered = false
  let pendingImageEdit: HTMLImageElement | null = null
  let pendingImageEditAt = 0
  let activeSizeDialogImage: HTMLImageElement | null = null
  const sizeDialogVisible = ref(false)
  const sizeDialogMode = ref<'width' | 'height'>('width')
  const sizeDialogValue = ref('')
  const sizeDialogError = ref('')

  const parseImageSizeInput = (value: string): number | 'auto' | null => {
    const raw = value.trim().toLowerCase()
    if (!raw) return null
    if (raw === 'auto') return 'auto'
    const pxMatch = raw.match(/^(\d+(\.\d+)?)(px)?$/)
    if (!pxMatch) return null
    return Number(pxMatch[1])
  }

  const resetImageSize = (img: HTMLImageElement) => {
    img.removeAttribute('width')
    img.removeAttribute('height')
    img.style.maxWidth = '100%'
  }

  const applyImageSize = (img: HTMLImageElement, widthInput: string, heightInput: string) => {
    const normalizedWidth = parseImageSizeInput(widthInput)
    const normalizedHeight = parseImageSizeInput(heightInput)

    if ((widthInput.trim() && normalizedWidth === null) || (heightInput.trim() && normalizedHeight === null)) {
      return false
    }

    const widthProvided = normalizedWidth !== null
    const heightProvided = normalizedHeight !== null

    if (!widthProvided && !heightProvided) {
      return true
    }

    if (widthProvided && heightProvided) {
      return false
    }

    if (normalizedWidth === 'auto' || normalizedHeight === 'auto') {
      resetImageSize(img)
      return true
    }

    const naturalWidth = img.naturalWidth || img.width
    const naturalHeight = img.naturalHeight || img.height
    if (!naturalWidth || !naturalHeight) return false

    if (typeof normalizedWidth === 'number') {
      img.setAttribute('width', String(Math.round(normalizedWidth)))
      img.removeAttribute('height')
    } else if (typeof normalizedHeight === 'number') {
      const proportionalWidth = (naturalWidth / naturalHeight) * normalizedHeight
      img.setAttribute('width', String(Math.round(proportionalWidth)))
      img.removeAttribute('height')
    }

    img.style.maxWidth = '100%'
    return true
  }

  const bindImageInteractions = () => {
    if (!quill) return
    const imgs: NodeListOf<HTMLImageElement> = quill.root.querySelectorAll('img')
    imgs.forEach((img) => {
      img.style.maxWidth = '100%'
      img.title = 'Double-click to set image size'

      const hasAlignment =
        img.classList.contains('quill-align-left') ||
        img.classList.contains('quill-align-center') ||
        img.classList.contains('quill-align-right') ||
        img.classList.contains('ql-align-left') ||
        img.classList.contains('ql-align-center') ||
        img.classList.contains('ql-align-right') ||
        img.style.float === 'left' ||
        img.style.float === 'right'

      if (hasAlignment) return

      img.style.display = 'inline-block'
      img.style.verticalAlign = 'middle'
      img.style.margin = '0 4px'
    })
  }

  const resolveImageFromEvent = (event: MouseEvent) => {
    const target = event.target as HTMLElement | null
    if (!target || !quill) return null

    const directImage = target.closest('img') as HTMLImageElement | null
    if (directImage && quill.root.contains(directImage)) {
      return directImage
    }

    if (
      pendingImageEdit &&
      quill.root.contains(pendingImageEdit) &&
      Date.now() - pendingImageEditAt < 1500
    ) {
      return pendingImageEdit
    }

    return null
  }

  const openImageSizeDialog = (img: HTMLImageElement) => {
    activeSizeDialogImage = img
    sizeDialogError.value = ''
    sizeDialogMode.value = 'width'
    sizeDialogValue.value = img.getAttribute('width') || ''
    sizeDialogVisible.value = true
  }

  const closeImageSizeDialog = () => {
    sizeDialogVisible.value = false
    sizeDialogError.value = ''
    sizeDialogValue.value = ''
    activeSizeDialogImage = null
  }

  const submitImageSizeDialog = () => {
    if (!activeSizeDialogImage) return

    const value = sizeDialogValue.value.trim()
    const widthInput = sizeDialogMode.value === 'width' ? value : ''
    const heightInput = sizeDialogMode.value === 'height' ? value : ''

    if (!value) {
      sizeDialogError.value = 'Enter a size or auto.'
      return
    }

    if (!applyImageSize(activeSizeDialogImage, widthInput, heightInput)) {
      sizeDialogError.value = 'Use 300, 300px, or auto.'
      return
    }

    closeImageSizeDialog()
  }

  const handleEditorClick = (event: MouseEvent) => {
    const target = event.target as HTMLElement | null
    if (!target || !quill) return

    const img = target.closest('img') as HTMLImageElement | null
    if (img && quill.root.contains(img)) {
      pendingImageEdit = img
      pendingImageEditAt = Date.now()
      return
    }
  }

  const handleEditorDblClick = (event: MouseEvent) => {
    const img = resolveImageFromEvent(event)
    if (!img) return

    event.preventDefault()
    event.stopPropagation()
    openImageSizeDialog(img)
  }

  const uploadImage = async (file: File): Promise<string> => {
    const res = await uploadRichImage(file)

    const url = res?.data?.url || res?.data?.data?.url
    if (!url) throw new Error('Image URL missing in upload response')
    return url
  }

  const insertImageByUpload = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.click()

    input.onchange = async () => {
      const file = input.files?.[0]
      if (!file || !quill) return

      try {
        const range = quill.getSelection(true)
        const index =
          range && Number.isFinite(range.index) ? range.index : quill.getLength()
        const imageUrl = await uploadImage(file)
        quill.insertEmbed(index, 'image', imageUrl)
        quill.setSelection(index + 1)

        setTimeout(() => {
          bindImageInteractions()
        }, 50)
      } catch (error: any) {
        const message =
          error?.response?.data?.detail ||
          error?.message ||
          'Image upload failed'
        window.alert(message)
      }
    }
  }

  onMounted(() => {
    if (!editorRef.value) return

    if (!imageResizeRegistered) {
      Quill.register('modules/imageResize', ImageResize)
      imageResizeRegistered = true
    }

    const defaultToolbar = [
      ['bold', 'italic', 'underline', 'strike'],
      [{ header: [1, 2, 3, false] }],
      [{ list: 'ordered' }, { list: 'bullet' }],
      [{ align: [] }],
      ['link', 'image'],
      ['clean'],
    ]

    const incomingModules = props.modules ? { ...props.modules } : {}
    const incomingToolbar = (incomingModules as any).toolbar
    let toolbarConfig: any

    if (Array.isArray(incomingToolbar)) {
      toolbarConfig = { container: incomingToolbar }
    } else if (incomingToolbar && typeof incomingToolbar === 'object') {
      toolbarConfig = { ...incomingToolbar }
    } else {
      toolbarConfig = { container: defaultToolbar }
    }

    toolbarConfig.handlers = {
      ...(toolbarConfig.handlers || {}),
      image: insertImageByUpload,
    }

    const modules = {
      ...incomingModules,
      toolbar: toolbarConfig,
      imageResize: (incomingModules as any).imageResize || {
        modules: ['Resize', 'DisplaySize', 'Toolbar'],
      },
    }

    quill = new Quill(editorRef.value, {
      theme: 'snow',
      modules,
    })
    editorHost = editorRef.value.parentElement as HTMLDivElement | null
    editorHost?.addEventListener('click', handleEditorClick, true)
    editorHost?.addEventListener('dblclick', handleEditorDblClick, true)

    quill.root.innerHTML = props.modelValue || ''
    bindImageInteractions()

    quill.on('text-change', () => {
      emit('update:modelValue', quill!.root.innerHTML)
      bindImageInteractions()
    })
  })

  watch(
    () => props.modelValue,
    (v) => {
      if (quill && quill.root.innerHTML !== v) {
        quill.root.innerHTML = v || ''
        bindImageInteractions()
      }
    }
  )

  onBeforeUnmount(() => {
    editorHost?.removeEventListener('click', handleEditorClick, true)
    editorHost?.removeEventListener('dblclick', handleEditorDblClick, true)
    pendingImageEdit = null
    quill = null
    editorHost = null
  })
</script>

<style scoped>
  .quill-container {
    width: 100%;
    min-height: 300px;
    max-width: 100%;
    overflow-x: hidden;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    box-sizing: border-box;
  }

  .quill-container :deep(.ql-toolbar.ql-snow) {
    border: 0;
    border-bottom: 0;
    border-radius: 0;
    border-bottom: 1px solid #dcdfe6;
  }

  .quill-container :deep(.ql-container.ql-snow) {
    width: 100%;
    border: 0;
    border-radius: 0;
    box-sizing: border-box;
  }

  .quill-container :deep(.ql-editor) {
    min-height: 240px;
  }

  .quill-container .ql-editor img {
    max-width: 100% !important;
    cursor: pointer;
  }

  .quill-container :deep(.ql-editor img.quill-align-left),
  .quill-container :deep(.ql-editor img.ql-align-left) {
    margin: 0 1em 1em 0;
  }

  .quill-container :deep(.ql-editor img.quill-align-right),
  .quill-container :deep(.ql-editor img.ql-align-right) {
    margin: 0 0 1em 1em;
  }

  .quill-container :deep(.ql-editor img.quill-align-center),
  .quill-container :deep(.ql-editor img.ql-align-center) {
    display: block;
    margin-left: auto;
    margin-right: auto;
  }

  .image-size-dialog-backdrop {
    position: fixed;
    inset: 0;
    z-index: 3000;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(15, 23, 42, 0.28);
    backdrop-filter: blur(4px);
  }

  .image-size-dialog {
    width: min(420px, calc(100vw - 32px));
    padding: 24px;
    border-radius: 18px;
    background: #ffffff;
    box-shadow: 0 24px 80px rgba(15, 23, 42, 0.16);
  }

  .image-size-dialog-title {
    margin-bottom: 18px;
    font-size: 20px;
    font-weight: 600;
    color: #111827;
  }

  .image-size-mode-group {
    display: flex;
    gap: 10px;
    margin-bottom: 16px;
  }

  .image-size-mode-btn {
    flex: 1;
    height: 42px;
    border: 1px solid #d1d5db;
    border-radius: 999px;
    background: #fff;
    color: #374151;
    font-size: 14px;
    cursor: pointer;
    transition:
      border-color 0.18s ease,
      background-color 0.18s ease,
      color 0.18s ease;
  }

  .image-size-mode-btn.active {
    border-color: #111827;
    background: #111827;
    color: #fff;
  }

  .image-size-input {
    width: 100%;
    height: 46px;
    padding: 0 14px;
    border: 1px solid #d1d5db;
    border-radius: 12px;
    outline: none;
    font-size: 14px;
    box-sizing: border-box;
  }

  .image-size-input:focus {
    border-color: #111827;
  }

  .image-size-error {
    margin-top: 10px;
    font-size: 13px;
    color: #b91c1c;
  }

  .image-size-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 18px;
  }

  .image-size-action {
    min-width: 92px;
    height: 40px;
    padding: 0 18px;
    border-radius: 999px;
    font-size: 14px;
    cursor: pointer;
  }

  .image-size-action.ghost {
    border: 1px solid #d1d5db;
    background: #fff;
    color: #374151;
  }

  .image-size-action.primary {
    border: 1px solid #111827;
    background: #111827;
    color: #fff;
  }
</style>
