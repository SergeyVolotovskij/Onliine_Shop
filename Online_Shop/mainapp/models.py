from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model() #мы хотим использовать Юзера, который создан в settings.AUTH.USER_MODEL

#
class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(self, *args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                # ct_model = ct_model.first()
                if with_respect_to in args:
                    return sorted(products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True)
        return products

class LatestProducts:
    objects = LatestProductsManager()


#Прикинем какие модели должны у нас быть в приложении:

#****************
#1 Category (Категория)
#2 Product (Продукт)
#3 CartProduct (Продукт в корзине)
#4 Cart (Сама корзина)
#5 Order (Заказ)
#****************

#6 Customer (Покупатель)
#7 Specifications (Характеристики продукта)

class Category(models.Model): #Категория
    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True) #конечная точка -> .../notebook

    #представление категорий в админке
    def __str__(self):
        return self.name

class Product(models.Model): #Продукт

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE) #категория, к которой товар и принадлежит
    title = models.CharField(max_length=255, verbose_name='Наименование продукта') #наименование продукта
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание', null=True) #описание, null=True - может быть пустым
    # max_digits=9 - кол-во цифр в цене, decimal_places=2 - количество цифр после запятой
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена продукта') #цена

    # представление категорий в админке
    def __str__(self):
        return self.title

class CartProduct(models.Model): #Продукт в корзине
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE) #юзер которому пренадлежит продукт
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products') #корзина
    #product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE) #продукт, который кладем в корзину
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    contetnt_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1) #количество
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена') #финальная цена

    # представление категорий в админке
    def __str__(self):
        return "Продукт: {} (для корзины)".format(self.product.title)

class Cart(models.Model): #Корзина
    owner = models.ForeignKey('Customer', verbose_name='Владелец', on_delete=models.CASCADE)  #владелец
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart') #многие ко многим
    total_products = models.PositiveIntegerField(default=0) #для показа корректного количества товара в корзине
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена') #финальная цена

    def __str__(self):
        return str(self.id)

class Customer(models.Model): #Покупатель
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    # first_name = models.CharField(max_length=255, verbose_name='Имя пользователя')
    phone = models.CharField(max_length=13, verbose_name='Номер телефона') #номер телефона
    address = models.CharField(max_length=255, verbose_name='Адрес')

    def __str__(self):
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)

class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Диагональ экрана')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
    processor_freq = models.CharField(max_length=255, verbose_name='Частота процессора')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    video = models.CharField(max_length=255, verbose_name='Видеокарта')
    time_without_charge = models.CharField(max_length=255, verbose_name='Время работы')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

class Smartphone(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Диагональ экрана')
    display_type = models.CharField(max_length=255, verbose_name='Тип дисплея')
    resolution = models.CharField(max_length=255, verbose_name='Разрешение экрана')
    accum_volume = models.CharField(max_length=255, verbose_name='Объем батареи')
    ram = models.CharField(max_length=255, verbose_name='Оперативная память')
    sd = models.BooleanField(default=True)
    sd_volume_max = models.CharField(max_length=255, verbose_name='Максимальный объем встраиваемой памяти')
    main_cam_mp = models.CharField(max_length=255, verbose_name='Главная камера')
    frontal_cam_mp = models.CharField(max_length=255, verbose_name='Фронтальная камера')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)


