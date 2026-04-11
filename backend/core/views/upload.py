from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.upload import upload_image


class UploadView(APIView):
    """通用上传接口，供后台富文本和其他图片上传流程复用。"""

    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # 测试免登录模式下允许匿名上传，方便本地调试富文本和图片流程。
        if bool(getattr(settings, "TEST_BYPASS_USER_AUTH", False)):
            return [AllowAny()]
        return [IsAuthenticated()]

    def post(self, request):
        """保存单个文件，并返回前端可直接使用的访问地址。"""
        file = request.FILES.get("file")
        folder = request.data.get("folder", "general")

        if not file:
            return Response(
                {"detail": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = upload_image(file, folder)
        return Response({"url": url})
