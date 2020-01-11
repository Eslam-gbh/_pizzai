# from rest_framework import exceptions
from rest_framework import serializers
from .models import Order, OrderedItem, ProductVariant
from pizzai.users.serializers import UserSerializer
from django.db import transaction
from django.conf import settings


class ProductVariantSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_id = serializers.CharField(source='product.pk')
    size = serializers.CharField(source='size.pk')

    class Meta:
        model = ProductVariant
        fields = ['product_id', "product_name", "price", "size"]
        read_only_fields = ['price']


class OrderedItemSerializer(serializers.ModelSerializer):
    product = ProductVariantSerializer(
        source='product_variant',
        many=False,
        required=True,
    )

    class Meta:
        model = OrderedItem
        fields = ['amount', 'product']


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderedItemSerializer(
        source='ordereditem_set',
        read_only=False,
        many=True,
    )
    customer_info = UserSerializer(
        source='customer',
        read_only=True,
        many=False,
    )
    total_price = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        coerce_to_string=False,
        read_only=True,
    )

    def validate_before_update(self, order):
        if order.status in settings.RESTRICTED_STATUSES:
            raise serializers.ValidationError(
                f"Can not update after statuses {settings.RESTRICTED_STATUSES}"
            )
        return True

    def create(self, validated_data):
        ordered_items = validated_data.pop('ordereditem_set')
        with transaction.atomic():
            order = super().create(validated_data)
            self.create_ordered_items(order, ordered_items)

        return order

    def update(self, order, validated_data):
        self.validate_before_update(order)
        ordered_items = validated_data.pop('ordereditem_set', [])
        with transaction.atomic():
            if ordered_items:
                order.ordereditem_set.all().delete()
                self.create_ordered_items(order, ordered_items)
            return super().update(order, validated_data)

    def create_ordered_items(self, order, ordered_items):
        ordered_items_objects = []
        for index, item in enumerate(ordered_items, 1):
            product_variant = ProductVariant.objects.get(
                product_id=item['product_variant']['product']['pk'],
                size_id=item['product_variant']['size']['pk'],
            )
            ordered_items_objects.append(
                OrderedItem(
                    order=order,
                    item_number=index,
                    product_variant=product_variant,
                    amount=item['amount'],
                ))

        OrderedItem.objects.bulk_create(ordered_items_objects)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['total_price']
