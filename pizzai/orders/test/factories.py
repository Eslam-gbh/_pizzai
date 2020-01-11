import factory
from pizzai.users.test.factories import UserFactory


class SizeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'orders.Size'

    serial = factory.Faker('pystr', min_chars=1, max_chars=8)
    name = factory.Faker('pystr', min_chars=1, max_chars=15)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'orders.Category'

    id = factory.Faker('pystr', min_chars=1, max_chars=8)
    name = factory.Faker('word')
    sequence_num = factory.Faker('pyint')


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'orders.Product'

    id = factory.Faker('pystr', min_chars=1, max_chars=8)
    name = factory.Faker('word')
    description = factory.Faker('word')
    category = factory.SubFactory(CategoryFactory)


class ProductVariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'orders.ProductVariant'

    id = factory.Faker('pyint')
    product = factory.SubFactory(ProductFactory)
    size = factory.SubFactory(SizeFactory)
    price = factory.Faker(
        "pydecimal",
        left_digits=2,
        right_digits=2,
        positive=True,
        min_value=None,
        max_value=None,
    )


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'orders.Order'

    id = factory.Faker('pyint')
    customer = factory.SubFactory(UserFactory)
    status = 'placed'


class OrderedItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'orders.OrderedItem'

    item_number = factory.Faker('pyint')
    order = factory.SubFactory(OrderFactory)
    product_variant = factory.SubFactory(ProductVariantFactory)
    amount = 1
