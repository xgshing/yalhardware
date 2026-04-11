# 前台用户订单列表 API
# apps/orders/views/frontend/order_list.py
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.orders.models import Order
from apps.orders.serializers.frontend.order_list import OrderListSerializer
from .auth_helpers import frontend_order_permissions, resolve_order_user


class OrderListView(APIView):
    def get_permissions(self):
        return frontend_order_permissions()

    def get(self, request):
        """
        我的订单列表
        """
        user = resolve_order_user(request)
        qs = (
            Order.objects.filter(user=user)
            .prefetch_related(
                "items",
                "items__review",
                "items__review__reply",
            )
            .order_by("-created_at")
        )

        serializer = OrderListSerializer(
            qs,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)
