from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from core.upload import upload_image
from ..models.rich_image import RichTextImage


class IsAuthenticatedOrBypass(BasePermission):
    def has_permission(self, request, view):
        if bool(getattr(settings, "TEST_BYPASS_USER_AUTH", False)):
            return True
        return bool(request.user and request.user.is_authenticated)


@api_view(["POST"])
@permission_classes([IsAuthenticatedOrBypass])
def upload_rich_image(request):
    """
    Upload an image for rich text content.
    - Local development stores files under media/richtext/
    - Production stores files in COS
    - Response format: {"url": "..."}
    """
    file = request.FILES.get("image") or request.FILES.get("file")

    if not file:
        return Response({"detail": "No image uploaded"}, status=400)

    if not settings.DATABASES["default"]["ENGINE"].endswith("sqlite3"):
        image_url = upload_image(file, folder="richtext")
        RichTextImage.objects.create(image=image_url)
    else:
        rich_image = RichTextImage.objects.create(image=file)
        image_url = request.build_absolute_uri(rich_image.image.url)

    return Response({"url": image_url})
