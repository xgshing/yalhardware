from rest_framework import serializers
from urllib.parse import urlparse

from apps.reviews.models import Review, ReviewReply
from apps.reviews.services.insights import generate_review_title
from apps.users.utils.mask import mask_username


class ReviewReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = [
            "merchant_reply",
            "merchant_replied_at",
        ]


class ReviewReadSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    reply = serializers.SerializerMethodField()
    can_append = serializers.SerializerMethodField()
    user_display_name = serializers.SerializerMethodField()
    ai_title = serializers.SerializerMethodField()
    has_media = serializers.SerializerMethodField()
    has_followup = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "rating",
            "content",
            "images",
            "created_at",
            "append_content",
            "append_at",
            "reply",
            "can_append",
            "user_display_name",
            "ai_title",
            "has_media",
            "has_followup",
        ]

    def get_reply(self, obj):
        try:
            return ReviewReplySerializer(obj.reply).data
        except ReviewReply.DoesNotExist:
            return None

    def get_images(self, obj):
        request = self.context.get("request")
        images = obj.images or []
        normalized: list[str] = []

        for image in images:
            url = (image or "").strip()
            if not url:
                continue

            parsed = urlparse(url)
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                normalized.append(url)
                continue

            # Convert site-relative or bare relative paths to absolute URLs when possible.
            if request:
                absolute_target = url if url.startswith("/") else f"/{url}"
                normalized.append(request.build_absolute_uri(absolute_target))
            else:
                normalized.append(url)

        return normalized

    def get_can_append(self, obj):
        return obj.append_content == ""

    def get_user_display_name(self, obj):
        user = getattr(obj, "user", None)
        if not user:
            return "Verified Buyer"

        first_name = (getattr(user, "first_name", "") or "").strip()
        last_name = (getattr(user, "last_name", "") or "").strip()
        full_name = f"{first_name} {last_name}".strip()

        if not full_name:
            username = (getattr(user, "username", "") or "").strip()
            full_name = username.split("@")[0] if "@" in username else username

        masked = mask_username(full_name).strip()
        return masked or "Verified Buyer"

    def get_ai_title(self, obj):
        return generate_review_title(obj.content, obj.rating)

    def get_has_media(self, obj):
        return bool(obj.images)

    def get_has_followup(self, obj):
        return bool((obj.append_content or "").strip())
