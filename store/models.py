from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone

class Category(models.Model):
    name=models.CharField(max_length=80,unique=True)
    slug=models.SlugField(unique=True)
    description=models.TextField(blank=True)
    def save(self,*a,**kw):
        if not self.slug: self.slug=slugify(self.name)
        super().save(*a,**kw)
    def __str__(self): return self.name

class Brand(models.Model):
    name=models.CharField(max_length=100,unique=True)
    def __str__(self): return self.name

class Product(models.Model):
    category=models.ForeignKey(Category,on_delete=models.PROTECT,related_name="products")
    brand=models.ForeignKey(Brand,on_delete=models.SET_NULL,null=True,blank=True)
    name=models.CharField(max_length=180)
    slug=models.SlugField(unique=True)
    description=models.TextField()
    image_url=models.URLField(blank=True)
    image=models.ImageField(upload_to="products/",blank=True,null=True)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    discount_percent=models.PositiveSmallIntegerField(default=0)
    sizes=models.CharField(max_length=200,default="S,M,L,XL")
    colours=models.CharField(max_length=200,default="Black,Blue")
    stock=models.PositiveIntegerField(default=10)
    rating=models.DecimalField(max_digits=3,decimal_places=2,default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True)
    @property
    def selling_price(self): return (self.price*(Decimal(100)-Decimal(self.discount_percent))/Decimal(100)).quantize(Decimal("0.01"))
    @property
    def size_list(self): return [x.strip() for x in self.sizes.split(",") if x.strip()]
    @property
    def colour_list(self): return [x.strip() for x in self.colours.split(",") if x.strip()]
    def __str__(self): return self.name

class Address(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="addresses")
    full_name=models.CharField(max_length=120)
    phone=models.CharField(max_length=15)
    line1=models.CharField(max_length=220)
    city=models.CharField(max_length=80)
    state=models.CharField(max_length=80)
    pincode=models.CharField(max_length=10)
    is_default=models.BooleanField(default=False)
    def __str__(self): return f"{self.full_name} - {self.city}"

class Coupon(models.Model):
    code=models.CharField(max_length=30,unique=True)
    discount_percent=models.PositiveSmallIntegerField(default=10)
    flat_amount=models.DecimalField(max_digits=8,decimal_places=2,default=0)
    minimum_order=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    active=models.BooleanField(default=True)
    expires_at=models.DateTimeField(null=True,blank=True)
    def valid(self,total):
        return self.active and total>=self.minimum_order and (not self.expires_at or self.expires_at>=timezone.now())
    def discount(self,total):
        if not self.valid(total): return Decimal("0")
        value=(total*Decimal(self.discount_percent)/100)+self.flat_amount
        return min(value,total)

class Order(models.Model):
    STATUS=[("placed","Order placed"),("confirmed","Confirmed"),("processing","Processing"),("packed","Packed"),("shipped","Shipped"),("out_for_delivery","Out for delivery"),("delivered","Delivered"),("cancelled","Cancelled")]
    PAYMENT=[("cod","Cash on Delivery"),("pending","Payment pending"),("paid","Paid")]
    user=models.ForeignKey(User,on_delete=models.PROTECT,related_name="shop_orders")
    order_id=models.CharField(max_length=24,unique=True)
    address=models.ForeignKey(Address,on_delete=models.PROTECT)
    status=models.CharField(max_length=24,choices=STATUS,default="placed")
    payment_method=models.CharField(max_length=20,choices=PAYMENT,default="cod")
    subtotal=models.DecimalField(max_digits=10,decimal_places=2)
    discount=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    delivery_charge=models.DecimalField(max_digits=8,decimal_places=2,default=0)
    total=models.DecimalField(max_digits=10,decimal_places=2)
    coupon_code=models.CharField(max_length=30,blank=True)
    created_at=models.DateTimeField(default=timezone.now)
    expected_delivery=models.DateField(null=True,blank=True)
    def __str__(self): return self.order_id

class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name="items")
    product=models.ForeignKey(Product,on_delete=models.PROTECT)
    product_name=models.CharField(max_length=180)
    unit_price=models.DecimalField(max_digits=10,decimal_places=2)
    quantity=models.PositiveIntegerField(default=1)
    size=models.CharField(max_length=20,blank=True)
    colour=models.CharField(max_length=40,blank=True)
    def line_total(self): return self.unit_price*self.quantity

class Review(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="reviews")
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    rating=models.PositiveSmallIntegerField()
    comment=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: unique_together=("product","user")
    def __str__(self): return f"{self.product} - {self.rating}/5"

class ReturnRequest(models.Model):
    KIND=[("return","Return"),("exchange","Exchange")]
    STATE=[("requested","Requested"),("approved","Approved"),("rejected","Rejected"),("completed","Completed")]
    order_item=models.ForeignKey(OrderItem,on_delete=models.CASCADE,related_name="requests")
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    kind=models.CharField(max_length=12,choices=KIND)
    reason=models.TextField()
    replacement_size=models.CharField(max_length=20,blank=True)
    status=models.CharField(max_length=12,choices=STATE,default="requested")
    created_at=models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=150)
    message=models.TextField()
    is_read=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
