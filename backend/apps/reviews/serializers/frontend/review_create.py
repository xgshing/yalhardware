# 创建评论
# apps/reviews/serializers/frontend/review_create.py
from rest_framework import serializers
from urllib.parse import urlparse

from apps.orders.models import OrderItem
from apps.orders.views.frontend.auth_helpers import resolve_order_user
from apps.reviews.models import Review


class ReviewCreateSerializer(serializers.Serializer):
    order_item_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    content = serializers.CharField()
    images = serializers.ListField(child=serializers.CharField(), required=False)

    def validate_images(self, value):
        cleaned: list[str] = []
        for image in value:
            url = (image or "").strip()
            if not url:
                continue

            # Accept absolute URLs and site-relative media paths like /media/xxx.jpg.
            if url.startswith("/"):
                cleaned.append(url)
                continue

            parsed = urlparse(url)
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                cleaned.append(url)
                continue

            raise serializers.ValidationError("Invalid image URL.")

        return cleaned

    def validate_order_item_id(self, value):
        user = resolve_order_user(self.context["request"])
        try:
            item = OrderItem.objects.select_related("order").get(id=value)
        except OrderItem.DoesNotExist:
            raise serializers.ValidationError("Order item does not exist.")

        if item.order.user != user:
            raise serializers.ValidationError("You do not have permission to review this order.")

        if item.order.status != item.order.Status.COMPLETED:
            raise serializers.ValidationError("The order is not completed and cannot be reviewed.")

        if hasattr(item, "review"):
            raise serializers.ValidationError("This item has already been reviewed.")

        return value

    def create(self, validated_data):
        order_item = OrderItem.objects.get(id=validated_data["order_item_id"])
        user = resolve_order_user(self.context["request"])
        return Review.objects.create(
            order_item=order_item,
            user=user,
            rating=validated_data["rating"],
            content=validated_data["content"],
            images=validated_data.get("images", []),
        )
