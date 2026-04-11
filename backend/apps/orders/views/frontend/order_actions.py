# 订单行为接口（取消 / 支付 / 确认收货）
# apps/orders/views/frontend/order_actions.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.orders.models import Order
from apps.orders.services.order_state_service import OrderStateService
from .auth_helpers import frontend_order_permissions, resolve_order_user


class OrderCancelView(APIView):
    def get_permissions(self):
        return frontend_order_permissions()

    def post(self, request, order_id):
        user = resolve_order_user(request)
        order = get_object_or_404(Order, id=order_id, user=user)
        OrderStateService.cancel(order)
        return Response({"status": "ok"})


class OrderPayView(APIView):
    def get_permissions(self):
        return frontend_order_permissions()

    def post(self, request, order_id):
        user = resolve_order_user(request)
        order = get_object_or_404(Order, id=order_id, user=user)
        OrderStateService.pay(order)
        return Response({"status": "paid"})


class OrderConfirmView(APIView):
    def get_permissions(self):
        return frontend_order_permissions()

    def post(self, request, order_id):
        user = resolve_order_user(request)
        order = get_object_or_404(Order, id=order_id, user=user)
        OrderStateService.confirm(order)
        return Response({"status": "completed"})
