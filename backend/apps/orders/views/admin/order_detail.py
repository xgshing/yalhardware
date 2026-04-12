# 后台订单详情API
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.orders.models import Order
from apps.orders.serializers.admin.order_detail import AdminOrderDetailSerializer
from apps.users.permissions import IsAdminUser as CustomIsAdminUser


class AdminOrderDetailView(APIView):
    permission_classes = [CustomIsAdminUser]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = AdminOrderDetailSerializer(order)
        return Response(serializer.data)
