import json
from urllib.parse import urlparse

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from core.upload import upload_image
from .models import Product, ProductCategory, ProductImage, ProductVariant
from .serializers.category import ProductCategorySerializer
from .serializers.category_tree import CategoryTreeSerializer
from .serializers.product_create import ProductCreateSerializer
from .serializers.product_detail import ProductDetailSerializer
from .serializers.product_update import ProductUpdateSerializer


def normalize_media_path(url: str) -> str:
    """
    Convert a full URL to a local relative media path.
    Mainly used when deleting local files in development.
    """
    if not url:
        return url
    parsed = urlparse(url)
    path = parsed.path
    if path.startswith(settings.MEDIA_URL):
        return path.replace(settings.MEDIA_URL, "", 1)
    return path.lstrip("/")


class AdminProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-is_featured", "featured_order", "id")
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ProductDetailSerializer
        if self.action in ["update", "partial_update"]:
            return ProductUpdateSerializer
        return ProductCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        cover_file = request.FILES.get("cover")
        if cover_file:
            if settings.DEBUG:
                path = default_storage.save(f"products/covers/{cover_file.name}", cover_file)
                product.cover = path
            else:
                product.cover = upload_image(cover_file, "products/covers")
            product.save(update_fields=["cover"])

        for img in request.FILES.getlist("uploaded_images"):
            if settings.DEBUG:
                path = default_storage.save(f"products/details/{img.name}", img)
                ProductImage.objects.create(product=product, image=path)
            else:
                url = upload_image(img, "products/details")
                ProductImage.objects.create(product=product, image=url)

        variants_raw = request.data.get("uploaded_variants")
        if variants_raw:
            try:
                variants_data = json.loads(variants_raw)
            except json.JSONDecodeError:
                return Response(
                    {"detail": "Invalid uploaded_variants payload"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            for variant in variants_data:
                uid = variant.get("uid")
                image_file = request.FILES.get(f"uploaded_variants_images_{uid}")
                style_image = None

                if settings.DEBUG and image_file:
                    style_image = default_storage.save(
                        f"products/variants/{image_file.name}", image_file
                    )
                elif image_file:
                    style_image = upload_image(image_file, "products/variants")

                ProductVariant.objects.create(
                    product=product,
                    style_name=variant.get("style_name", ""),
                    spec=variant.get("spec", ""),
                    stock=int(variant.get("stock", 0)),
                    style_image=style_image,
                )

        return Response({"id": product.id, "message": "Product created"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="reorder")
    @transaction.atomic
    def reorder(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({"detail": "Request data must be a list"}, status=400)

        for item in data:
            pid = int(item.get("id"))
            order = int(item.get("featured_order", 0))
            Product.objects.filter(id=pid).update(featured_order=order)

        return Response({"message": "Reorder saved"}, status=200)

    def update(self, request, *args, **kwargs):
        product = self.get_object()

        serializer = self.get_serializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        cover_file = request.FILES.get("cover")
        if cover_file:
            if settings.DEBUG:
                path = default_storage.save(f"products/covers/{cover_file.name}", cover_file)
                product.cover = path
            else:
                product.cover = upload_image(cover_file, "products/covers")
            product.save(update_fields=["cover"])
        elif request.data.get("cover") == "":
            product.cover = None
            product.save(update_fields=["cover"])

        removed_images_raw = request.data.get("removed_detail_images", "[]")
        try:
            removed_images = json.loads(removed_images_raw)
        except json.JSONDecodeError:
            removed_images = []

        if removed_images:
            for url in removed_images:
                normalized = normalize_media_path(url)
                img_obj = ProductImage.objects.filter(product=product, image=normalized).first()

                if not img_obj:
                    continue

                if settings.DEBUG and img_obj.image:
                    default_storage.delete(img_obj.image)

                img_obj.delete()

        for img in request.FILES.getlist("uploaded_images"):
            if settings.DEBUG:
                path = default_storage.save(f"products/details/{img.name}", img)
                ProductImage.objects.create(product=product, image=path)
            else:
                url = upload_image(img, "products/details")
                ProductImage.objects.create(product=product, image=url)

        variants_raw = request.data.get("uploaded_variants")
        if variants_raw:
            try:
                variants_data = json.loads(variants_raw)
            except json.JSONDecodeError:
                return Response(
                    {"detail": "Invalid uploaded_variants payload"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            keep_ids = []

            for variant in variants_data:
                vid = variant.get("id")
                uid = variant.get("uid")
                remove_image = variant.get("remove_image", False)
                image_file = request.FILES.get(f"uploaded_variants_images_{uid}")
                style_image = None

                if vid:
                    obj = ProductVariant.objects.get(id=vid, product=product)
                    obj.style_name = variant.get("style_name", "")
                    obj.spec = variant.get("spec", "")
                    obj.stock = int(variant.get("stock", 0))

                    if remove_image:
                        obj.style_image = None

                    if image_file:
                        if settings.DEBUG:
                            style_image = default_storage.save(
                                f"products/variants/{image_file.name}", image_file
                            )
                        else:
                            style_image = upload_image(image_file, "products/variants")
                        obj.style_image = style_image

                    obj.save(update_fields=["style_name", "spec", "stock", "style_image"])
                    keep_ids.append(obj.id)
                else:
                    if settings.DEBUG and image_file:
                        style_image = default_storage.save(
                            f"products/variants/{image_file.name}", image_file
                        )
                    elif image_file:
                        style_image = upload_image(image_file, "products/variants")

                    obj = ProductVariant.objects.create(
                        product=product,
                        style_name=variant.get("style_name", ""),
                        spec=variant.get("spec", ""),
                        stock=int(variant.get("stock", 0)),
                        style_image=style_image,
                    )
                    keep_ids.append(obj.id)

            to_delete = ProductVariant.objects.filter(product=product).exclude(id__in=keep_ids)
            for variant in to_delete:
                if settings.DEBUG and variant.style_image:
                    default_storage.delete(variant.style_image)
                variant.delete()

        product = Product.objects.prefetch_related("detail_images", "variants").get(id=product.id)
        serializer = ProductDetailSerializer(product, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        roots = ProductCategory.objects.filter(parent__isnull=True)
        serializer = CategoryTreeSerializer(roots, many=True)
        return Response(serializer.data)
