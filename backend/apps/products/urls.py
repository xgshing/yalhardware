from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryTreeAPIView, ProductDetailAPIView, ProductListAPIView
from .views_admin import AdminProductViewSet, ProductCategoryViewSet

# 后台路由统一挂在 /api/admin/ 下，便于前后端约定接口前缀。
admin_router = DefaultRouter()
admin_router.register(
    r"products",
    AdminProductViewSet,
    basename="admin-products",
)
admin_router.register(
    r"categories",
    ProductCategoryViewSet,
    basename="admin-categories",
)

urlpatterns = [
    # 前台只读接口。
    path("products/", ProductListAPIView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailAPIView.as_view(), name="product-detail"),
    path("categories/", CategoryTreeAPIView.as_view(), name="category-tree"),
    # 后台管理接口。
    path("admin/", include(admin_router.urls)),
]
