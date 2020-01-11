from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import DecimalField, Sum, F
from ool import VersionField, VersionedMixin


class BaseModel(VersionedMixin, models.Model):
    version = VersionField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Order(BaseModel):
    PLACED = 'placed'
    READY = 'ready'
    DELIVERED = 'delivered'
    STATUS_CHOICES = (
        (PLACED, _('PLACED')),
        (READY, _('READY')),
        (DELIVERED, _('DELIVERED')),
    )

    customer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=PLACED,
    )
    product_variants = models.ManyToManyField(
        'ProductVariant',
        through='OrderedItem',
        related_name='orders',
    )

    @property
    def total_price(self):
        return self.ordereditem_set.aggregate(total=Sum(
            F('amount') * F('product_variant__price'),
            output_field=DecimalField(),
        ))['total']

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f'Order for customer {self.customer_id}'


class OrderedItem(BaseModel):
    class Meta:
        verbose_name = "Ordered Item"
        verbose_name_plural = "Ordered Items"
        unique_together = (('item_number', 'order'), )

    item_number = models.PositiveSmallIntegerField()

    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
    )

    product_variant = models.ForeignKey(
        'ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
    )

    amount = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"Ordered Item {self.item_number}"


class Size(BaseModel):
    class Meta:
        verbose_name = "Size"
        verbose_name_plural = "Sizes"

    serial = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=15, primary_key=True)

    def __str__(self):
        return f"Size {self.name} with serial {self.serial}"


class Category(BaseModel):
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    id = models.CharField(max_length=8, primary_key=True)
    sequence_num = models.PositiveIntegerField()
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"Category {self.id} with Verbose Name {self.name} and sequence_num {self.sequence_num}"


class Product(BaseModel):
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    id = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        return f"Product {self.name} with ID {self.pk}"


class ProductVariant(BaseModel):
    class Meta:
        verbose_name = "ProductVariant"
        verbose_name_plural = "ProductVariants"
        unique_together = (('product', 'size'), )

    product = models.ForeignKey(
        'Product',
        on_delete=models.SET_NULL,
        null=True,
    )
    size = models.ForeignKey(
        'Size',
        on_delete=models.SET_NULL,
        null=True,
    )
    price = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"Product {self.product_id} with size {self.size_id} and price {self.price}"
