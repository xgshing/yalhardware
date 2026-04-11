from django.conf import settings
from rest_framework import serializers

from apps.orders.models import OrderItem
from apps.orders.views.frontend.auth_helpers import resolve_order_user
from apps.reviews.models import Review
from apps.reviews.serializers.frontend.review_read import ReviewReadSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    review = serializers.SerializerMethodField()
    can_review = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_id",
            "product_title",
            "sku_title",
            "price",
            "quantity",
            "review",
            "can_review",
            "product_image",
        ]

    def get_product_image(self, obj):
        image = obj.product_image
        if not image:
            return None

        if image.startswith("http://") or image.startswith("https://"):
            return image

        media_url = settings.MEDIA_URL.rstrip("/")
        path = f"{media_url}/{image}".replace("//", "/")

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(path)

        return path

    def get_review(self, obj):
        try:
            review = obj.review
        except Review.DoesNotExist:
            return None

        return ReviewReadSerializer(review, context=self.context).data

    def get_can_review(self, obj):
        request = self.context.get("request")
        user = resolve_order_user(request)

        if obj.order.user != user:
            return False

        if obj.order.status != obj.order.Status.COMPLETED:
            return False

        if hasattr(obj, "review"):
            return False

        return True
