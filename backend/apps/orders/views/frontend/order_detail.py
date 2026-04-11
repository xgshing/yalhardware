# 订单详情接口
# apps/orders/views/frontend/order_detail.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.orders.models import Order
from apps.orders.serializers.frontend.order_detail import OrderDetailSerializer
from .auth_helpers import frontend_order_permissions, resolve_order_user


class OrderDetailView(APIView):
    def get_permissions(self):
        return frontend_order_permissions()

    def get(self, request, order_id):
        """
        订单详情
        """
        user = resolve_order_user(request)
        order = get_object_or_404(
            Order.objects.prefetch_related(
                "items",
                "items__review",
                "items__review__reply",
            ),
            id=order_id,
            user=user,
        )

        serializer = OrderDetailSerializer(
            order,
            context={"request": request},
        )
        return Response(serializer.data)
