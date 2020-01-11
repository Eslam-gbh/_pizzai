import logging

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Order
from .serializers import (
    OrderSerializer, )

logging.basicConfig()
logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    """
    Updates and retrieves Orders
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (AllowAny, )
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'customer_id']
