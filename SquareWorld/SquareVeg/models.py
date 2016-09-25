from django.db import models
from django.core.urlresolvers import reverse
from django.utils.text import slugify
from django.conf import settings
from decimal import Decimal
from django.db.models.signals import pre_save, post_save

# Create your models here.

class ProductQuerySet(models.query.QuerySet):
	def active(self):
		return self.filter(active=True)


class ProductManager(models.Manager):
	def get_queryset(self):
		return ProductQuerySet(self.model, using=self._db)

	def all(self, *args, **kwargs):
		return self.get_queryset().active()

	def get_related(self, instance):
		products_one = self.get_queryset().filter(categories__in=instance.categories.all())
		products_two = self.get_queryset().filter(default=instance.default)
		qs = (products_one | products_two).exclude(id=instance.id).distinct()
		return qs


class Product(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=20)
    sale_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    active = models.BooleanField(default=True)
    categories = models.ManyToManyField('Category', blank=True)
    default = models.ForeignKey('Category', related_name='default_category', null=True, blank=True)
    inventory = models.IntegerField(null=True, blank=True)

    objects = ProductManager()

    class Meta:
        ordering = ["-title"]

    def __unicode__(self): #def __str__(self):
        return self.title 

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.pk})

    def get_image_url(self):
        img = self.productimage_set.first()
        if img:
            return img.image.url
        return img #None

    def get_price(self):
        if self.sale_price is not None:
            return self.sale_price
        else:
            return self.price

    def remove_from_cart(self):
        return "%s?item=%s&qty=1&delete=True" %(reverse("cart"), self.id)

def image_upload_to(instance, filename):
	title = instance.product.title
	slug = slugify(title)
	basename, file_extension = filename.split(".")
	new_filename = "%s-%s.%s" %(slug, instance.id, file_extension)
	return "products/%s/%s" %(slug, new_filename)

class ProductImage(models.Model):
	product = models.ForeignKey(Product)
	image = models.ImageField(upload_to=image_upload_to)

	def __unicode__(self):
		return self.product.title


class Category(models.Model):
	title = models.CharField(max_length=120, unique=True)
	slug = models.SlugField(unique=True)
	description = models.TextField(null=True, blank=True)
	active = models.BooleanField(default=True)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("category_detail", kwargs={"slug": self.slug })

class CartItem(models.Model):
	cart = models.ForeignKey("Cart")
	item = models.ForeignKey(Product)
	quantity = models.DecimalField(max_digits=10, decimal_places=1,default=1.0)
	line_item_total = models.DecimalField(max_digits=10, decimal_places=2)

	def __unicode__(self):
		return self.item.title

	def remove(self):
		return self.item.remove_from_cart()

def cart_item_pre_save_receiver(sender, instance, *args, **kwargs):
	qty = instance.quantity
	if qty >= 1:
		price = instance.item.get_price()
		line_item_total = Decimal(qty) * Decimal(price)
		instance.line_item_total = line_item_total

pre_save.connect(cart_item_pre_save_receiver, sender=CartItem)

def cart_item_post_save_receiver(sender, instance, *args, **kwargs):
	instance.cart.update_subtotal()

post_save.connect(cart_item_post_save_receiver, sender=CartItem)


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    items = models.ManyToManyField(Product, through=CartItem)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    subtotal = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)
    tax_percentage  = models.DecimalField(max_digits=10, decimal_places=5, default=0.085)
    tax_total = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)
    total = models.DecimalField(max_digits=50, decimal_places=2, default=25.00)
    totalquantity = models.IntegerField(null=True, blank=True, default=0)
	# discounts
	# shipping

    def __unicode__(self):
        return str(self.id)

    def update_subtotal(self):
        print "updating..."
        subtotal = 0
        totalquantity = 0.0
        items = self.cartitem_set.all()
        for item in items:
            subtotal += item.line_item_total
        self.subtotal = "%.2f" %(subtotal)
        self.totalquantity = items.count()
        self.save()

def do_tax_and_total_receiver(sender, instance, *args, **kwargs):
	subtotal = Decimal(instance.subtotal)
	tax_total = round(subtotal * Decimal(instance.tax_percentage), 2) #8.5%
	print instance.tax_percentage
	total = round(subtotal + Decimal(tax_total), 2)
	instance.tax_total = "%.2f" %(tax_total)
	instance.total = "%.2f" %(total)
	#instance.save()

pre_save.connect(do_tax_and_total_receiver, sender=Cart)


class Addresses(models.Model):
    user_id = models.ForeignKey('auth.user',on_delete=models.CASCADE)
    user_name = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    street_address = models.TextField(max_length=400)
    landmark = models.CharField(max_length=150)
    pincode = models.IntegerField(default=411057)

    def __unicode__(self):
        return self.user_name