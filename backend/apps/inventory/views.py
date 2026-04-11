from rest_framework import permissions, viewsets

from .models import InventoryRecord
from .serializers import InventoryRecordSerializer


class InventoryRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """后台库存流水只读接口，用于查看库存变动记录。"""

    queryset = InventoryRecord.objects.select_related(
        "variant", "variant_product"
    ).order_by("-created_at")
    serializer_class = InventoryRecordSerializer
    permission_classes = [permissions.IsAdminUser]
