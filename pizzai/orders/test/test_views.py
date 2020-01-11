import json
from django.urls import reverse
from django.forms.models import model_to_dict
from nose.tools import eq_
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
from pizzai.orders.models import Order
from pizzai.users.test.factories import UserFactory
from .factories import ProductVariantFactory, OrderFactory, OrderedItemFactory
fake = Faker()


class TestOrderListTestCase(APITestCase):
    """
    Tests /order list operations.
    """
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('order-list')
        customer = UserFactory()
        cls.product_variant1 = ProductVariantFactory()
        cls.product_variant2 = ProductVariantFactory()
        cls.order_post_data = {
            "ordered_items": [
                {
                    "amount": 3,
                    "product": {
                        "product_id": cls.product_variant1.product_id,
                        "size": cls.product_variant1.size_id,
                    }
                },
                {
                    "amount": 2,
                    "product": {
                        "product_id": cls.product_variant2.product_id,
                        "size": cls.product_variant2.size_id,
                    }
                },
            ],
            "status":
            "placed",
            "customer":
            customer.id,
        }

    def test_post_request_with_no_data_fails(self):
        response = self.client.post(self.url, {})
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_request_with_valid_data_succeeds(self):
        response = self.client.post(
            self.url,
            content_type='application/json',
            data=json.dumps(self.order_post_data),
        )
        eq_(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(pk=response.data.get('id'))
        expected_total_price = 3 * self.product_variant1.price + 2 * self.product_variant2.price
        eq_(order.total_price, expected_total_price)
        eq_(
            2,
            len(response.data.get("ordered_items")),
        )

    def test_duplicate_requests_fails(self):
        response = self.client.post(
            self.url,
            content_type='application/json',
            data=json.dumps(self.order_post_data),
            HTTP_X_IDEMPOTENCY_KEY='123',
        )
        eq_(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(self.url,
                                    content_type='application/json',
                                    data=json.dumps(self.order_post_data),
                                    HTTP_X_IDEMPOTENCY_KEY='123')
        eq_(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestOrderDetailTestCase(APITestCase):
    """
    Tests /order detail operations.
    """
    @classmethod
    def setUpTestData(cls):
        cls.customer = UserFactory()
        cls.order = OrderFactory.create(customer=cls.customer, )
        cls.ordered_item1 = OrderedItemFactory(item_number=1, order=cls.order)
        cls.ordered_item2 = OrderedItemFactory(item_number=2, order=cls.order)
        cls.url = reverse('order-detail', kwargs={'pk': cls.order.pk})

    def test_get_request_returns_a_given_user(self):
        response = self.client.get(self.url)
        eq_(response.status_code, status.HTTP_200_OK)
        expected_total_price = (self.ordered_item1.product_variant.price +
                                self.ordered_item2.product_variant.price)
        eq_(self.order.total_price, expected_total_price)
        eq_(
            2,
            len(response.data.get("ordered_items")),
        )
        eq_(
            self.order.customer.username,
            response.data["customer_info"]['username'],
        )

    def test_put_request_updates_a_user(self):
        fake_amount = fake.pyint(max_value=9)
        payload = {
            'ordered_items': [{
                "amount": fake_amount,
                "product": {
                    "product_id": self.ordered_item2.product_variant.product_id,
                    "size": self.ordered_item2.product_variant.size_id,
                }
            }]
        }
        response = self.client.patch(
            self.url,
            content_type='application/json',
            data=json.dumps(payload),
        )
        eq_(response.status_code, status.HTTP_200_OK)
        expected_total_price = fake_amount * self.ordered_item2.product_variant.price
        eq_(self.order.total_price, expected_total_price)
