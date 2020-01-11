from django.test import TestCase
# from django.forms.models import model_to_dict
from nose.tools import eq_, ok_

from pizzai.users.test.factories import UserFactory
from .factories import ProductVariantFactory
from ..serializers import OrderSerializer


class TestOrderSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = UserFactory()
        product_variant = ProductVariantFactory()
        cls.order_data = {
            "ordered_items": [
                {
                    "amount": 3,
                    "product": {
                        "product_id": product_variant.product_id,
                        "size": product_variant.size_id,
                    }
                },
            ],
            "status": "placed",
            "customer": user.id,
        }

    def test_serializer_with_empty_data(self):
        serializer = OrderSerializer(data={})
        eq_(serializer.is_valid(), False)

    def test_serializer_with_valid_data(self):
        serializer = OrderSerializer(data=self.order_data)
        ok_(serializer.is_valid())

    def test_serializer_with_invalid_data(self):
        invalid_data = self.order_data.copy()
        invalid_data.pop("customer")
        serializer = OrderSerializer(data=invalid_data)
        eq_(serializer.is_valid(), False)

