import sys
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.urls import reverse
from django.utils import timezone

User = get_user_model()

def get_product_url(obj, viewname):
    return reverse(viewname, kwargs={'slug': obj.slug})

# Create your models here.

class LatestProductManager:

    @staticmethod
    def get_products_for_models(*args):
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        return products

class LatestProducts:
    object = LatestProductManager()

class CategoryManager(models.Manager):

    CATEGORY_NAME_COUNT_NAME = {
        'Ноутбуки': 'notebook__count',
        'Смартфоны': 'smartphone__count'
    }
    def get_queryset(self):
        return super().get_queryset()


class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Product (models.Model):

    class Meta:
        abstract = True

    category = models.ForeignKey (Category, on_delete=models.CASCADE, verbose_name="Категория товара")
    title = models.CharField(max_length=255, verbose_name="Наименование товара")
    slug = models.SlugField(unique=True)
    seller_id = models.ForeignKey ("Seller", verbose_name="Продавец товара", on_delete=models.CASCADE)
    image = models.ImageField(verbose_name="Фото товара")
    descriptions = models.TextField(verbose_name="Описание товара", null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Цена до скидки")
    sale_price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Цена продажи")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)
        new_img = img.convert('RGB')
        resize = new_img.resize((400,400), Image.ANTIALIAS)
        filestream = BytesIO()
        resize.save(filestream, 'JPEG',quality = 90)
        filestream.seek(0)
        name = '{}.{}'.format(*self.image.name.split('.'))
        self.image = InMemoryUploadedFile(
            filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None
        )
        super().save(*args, **kwargs)

class Notebook (Product):
    diagonal = models.CharField(max_length=255, verbose_name="Диагональ экрана")
    display = models.CharField(max_length=255, verbose_name="Тип экрана")
    ram = models.CharField(max_length=255, verbose_name="Оперативная память")
    video = models.CharField(max_length=255, verbose_name="Видеокарта")
    hdd = models.CharField(max_length=255, verbose_name="Жесткий диск")

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'notebook_detail')

class Smartphone (Product):
    diagonal = models.CharField(max_length=255, verbose_name="Диагональ экрана")
    display = models.CharField(max_length=255, verbose_name="Тип экрана")
    accum = models.CharField(max_length=255, verbose_name="ОБъем батареи")
    sd = models.BooleanField(default=True, verbose_name="Наличие карты памяти")
    hdd = models.CharField(max_length=255, verbose_name="Жесткий диск")
    cam = models.CharField(max_length=255, verbose_name="Разрешение камеры")

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)


    def get_absolute_url(self):
        return get_product_url(self, 'smartphone_detail')

class Seller (models.Model):
    name = models.CharField(max_length=255, verbose_name="Название продавца")
    money = models.PositiveIntegerField(default=0)

class CartProduct (models.Model):
    user = models.ForeignKey('Customer', verbose_name="Покупатель", on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name="Корзина", on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    amount = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(default=0, max_digits=5, decimal_places=2, verbose_name="Итоговая цена")

    def __str__(self):
        return "Продукт {} (для корзины)".format(self.content_object.title)

    def save(self, *args, **kwargs):
        self.final_price = self.amount * self.content_object.sale_price
        super().save(*args, **kwargs)




class Cart (models.Model):
    owner = models.ForeignKey("Customer", verbose_name="Владелец", on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank= True, related_name="related_cart")
    total_product = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(default=0, max_digits=5, decimal_places=2, verbose_name="Итоговая цена")
    in_order = models.BooleanField(default=False)
    for_anon_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

class Customer (models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)
    phone = models.CharField(max_length=255)
    Address = models.CharField(max_length=255)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_order')

    def __str__(self):
        return "Покупатель {} {}".format(self.user.first_name, self.user.last_name)

class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель', related_name='related_orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(
        max_length=100,
        verbose_name='Статус заказ',
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    buying_type = models.CharField(
        max_length=100,
        verbose_name='Тип заказа',
        choices=BUYING_TYPE_CHOICES,
        default=BUYING_TYPE_SELF
    )
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)
