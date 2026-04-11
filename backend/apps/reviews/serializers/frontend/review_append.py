# 追评 Serializer
from django.utils import timezone
from rest_framework import serializers

from apps.orders.views.frontend.auth_helpers import resolve_order_user
from apps.reviews.models import Review


class ReviewAppendSerializer(serializers.Serializer):
    review_id = serializers.IntegerField()
    content = serializers.CharField()

    def validate_review_id(self, value):
        user = resolve_order_user(self.context["request"])

        try:
            review = Review.objects.get(id=value)
        except Review.DoesNotExist:
            raise serializers.ValidationError("Review does not exist.")

        if review.user != user:
            raise serializers.ValidationError("You do not have permission to append this review.")

        if review.append_content:
            raise serializers.ValidationError("An additional review has already been submitted.")

        return value

    def save(self):
        review = Review.objects.get(id=self.validated_data["review_id"])
        review.append_content = self.validated_data["content"]
        review.append_at = timezone.now()
        review.save()
        return review
