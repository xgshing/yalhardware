from django.db.models import Avg, Count, IntegerField, Q, Sum, Value
from django.db.models.functions import Coalesce
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import AllowAny

from .models import Product, ProductCategory
from .serializers.category_tree import CategoryTreeSerializer
from .serializers.product_create import ProductCreateSerializer
from .serializers.product_detail import ProductDetailSerializer
from .serializers.product_update import ProductUpdateSerializer


class ProductListAPIView(ListAPIView):
    """
    前台产品列表接口。

    支持关键词筛选，以及导航搜索建议使用的 limit 截断。
    """

    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer

    @staticmethod
    def with_metrics(queryset):
        return queryset.annotate(
            rating=Avg("order_items__review__rating"),
            review_count=Count("order_items__review", distinct=True),
            salesVolume=Coalesce(
                Sum(
                    "order_items__quantity",
                    filter=Q(
                        order_items__order__status__in=["PAID", "SHIPPED", "COMPLETED"]
                    ),
                ),
                Value(0),
                output_field=IntegerField(),
            ),
        )

    def get_queryset(self):
        queryset = self.with_metrics(Product.objects.filter(is_active=True)).order_by(
            "-created_at"
        )

        q = (self.request.query_params.get("q") or "").strip()
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q)
                | Q(category__name__icontains=q)
                | Q(description__icontains=q)
                | Q(specifications__icontains=q)
            )

        limit_raw = self.request.query_params.get("limit")
        if limit_raw:
            try:
                limit = max(1, int(limit_raw))
                queryset = queryset[:limit]
            except (TypeError, ValueError):
                pass

        return queryset


class ProductDetailAPIView(RetrieveAPIView):
    """前台产品详情接口，只返回启用中的产品。"""

    permission_classes = [AllowAny]
    queryset = ProductListAPIView.with_metrics(Product.objects.filter(is_active=True))
    serializer_class = ProductDetailSerializer


class ProductCreateAPIView(CreateAPIView):
    """后台产品创建接口，保留给非 ViewSet 的创建流程使用。"""

    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer


class ProductUpdateAPIView(UpdateAPIView):
    """后台产品更新接口，保留给非 ViewSet 的编辑流程使用。"""

    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer


class CategoryTreeAPIView(ListAPIView):
    """前台分类树接口，供导航菜单和分类页使用。"""

    permission_classes = [AllowAny]
    serializer_class = CategoryTreeSerializer

    def get_queryset(self):
        # 这里只返回顶级分类，子分类由序列化器递归展开。
        return ProductCategory.objects.filter(parent__isnull=True)
