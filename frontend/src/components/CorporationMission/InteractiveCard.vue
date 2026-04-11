<template>
  <!--
    可交互卡片容器：
    1) 通过 is-hovered 切换悬停样式
    2) 监听鼠标进入/离开并向父组件抛出事件
  -->
  <article
    class="interactive-card"
    :class="{ 'is-hovered': isHovered }"
    @mouseenter="emit('mouseenter')"
    @mouseleave="emit('mouseleave')"
    role="article"
    aria-labelledby="interactive-title"
  >
    <!-- 左上角圆形区域：未悬停显示图标，悬停显示序号 -->
    <div
      class="corner-circle"
      aria-hidden="false"
    >
      <div class="circle-inner">
        <img
          v-if="!isHovered"
          :src="imageUrl"
          :alt="`${number} icon`"
          class="circle-icon"
        />
        <span class="circle-number">{{ number }}</span>
      </div>
    </div>

    <!-- 背景图层：悬停时淡入 -->
    <div class="card-background">
      <img
        :src="imageUrl"
        :alt="title"
        class="background-image"
        :class="{ visible: isHovered }"
        loading="lazy"
      />
    </div>

    <!-- 文案内容区 -->
    <div class="card-content">
      <h3
        class="card-title"
        id="interactive-title"
      >
        {{ title }}
      </h3>
      <p class="card-description">{{ description }}</p>
    </div>
  </article>
</template>

<script setup lang="ts">
  interface Props {
    id: number
    title: string
    description: string
    imageUrl: string
    number: number
    isHovered: boolean
  }

  interface Emits {
    (e: 'mouseenter'): void
    (e: 'mouseleave'): void
  }

  defineProps<Props>()
  const emit = defineEmits<Emits>()
</script>

<style lang="scss" scoped>
  /* 卡片基础样式 */
  .interactive-card {
    position: relative;
    background: #eee9e9;
    border-radius: 8px;
    overflow: hidden;
    padding: 35px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
    }

    /* 悬停态：背景变暗、文字变白、圆圈边框变白 */
    &.is-hovered {
      background: rgba(0, 0, 0, 0.7);

      .card-title {
        color: #ffffff;
      }

      .card-description {
        color: #ffffff;
      }

      .corner-circle .circle-inner {
        background: transparent;
        border: 2px solid #ffffff;
      }
    }
  }

  /* 左上角圆形区域 */
  .corner-circle {
    position: absolute;
    top: 20px;
    left: 20px;
    z-index: 2;

    .circle-inner {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      background: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

      .circle-icon {
        width: 100%;
        object-fit: cover;
        z-index: 1;
      }

      .circle-number {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 2.5rem;
        color: white;
        transition: color 0.3s ease;
        z-index: 5;
      }
    }
  }

  /* 背景图层 */
  .card-background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;

    .background-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
      opacity: 0;
      transform: scale(1.1);
      transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);

      &.visible {
        opacity: 0.9;
        transform: scale(1);
      }
    }
  }

  /* 内容区：底部对齐，悬停时通过 transform/opacity 过渡，避免布局跳动 */
  .card-content {
    position: relative;
    z-index: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;

    .card-title {
      font-size: 1.75rem;
      font-weight: 600;
      margin-bottom: 15px;
      color: #2c3e50;
      transition:
        color 0.3s ease,
        transform 0.45s ease;
      line-height: 1.3;
    }

    .card-description {
      font-size: 1rem;
      line-height: 1.6;
      color: #5d6d7e;
      margin: 0;
      overflow: hidden;
      opacity: 0;
      transform: translateY(12px);
      transition:
        color 0.3s ease,
        opacity 0.45s ease,
        transform 0.45s ease;

      .is-hovered & {
        opacity: 1;
        transform: translateY(0);
      }
    }
  }

  /* 标题轻微上移，不改字号，避免“上移后再跳一下” */
  .interactive-card.is-hovered .card-content .card-title {
    transform: translateY(-6px);
  }

  /* 移动端样式 */
  @media (max-width: 768px) {
    .interactive-card {
      height: 350px;
      padding: 20px;
    }

    .card-title {
      font-size: 1.5rem;
    }

    .corner-circle .circle-inner {
      width: 45px;
      height: 45px;

      .circle-icon {
        width: 100%;
      }
    }
  }
</style>
