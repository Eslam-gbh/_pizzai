import factory
from pizzai.users.test.factories import UserFactory
from pizzai.orders.models import OrderedItem


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

    @factory.post_generation
    def product_variants(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for index, (ordered_item, amount) in enumerate(extracted):
                OrderedItem.objects.create(
                    item_number=index,
                    order=self,
                    product_variant=ordered_item,
                    amount=amount,
                )
