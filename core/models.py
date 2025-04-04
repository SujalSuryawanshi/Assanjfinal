from decimal import Decimal
from django.db import models
from datetime import datetime,date
from Main import settings
from django.urls import reverse
from embed_video.fields import EmbedVideoField
from users.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator 
from django.db.models import Avg
from datetime import timedelta




class Category(models.Model):
    cat_name=models.CharField(max_length=30, null=True, blank=True)
    def __str__(self):
        return self.cat_name

class Egit(models.Model):
    egit_name=models.CharField(max_length=30)
    def __str__(self):
        return self.egit_name
    
class Subcat(models.Model):
    sub_cat=models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_name=models.CharField(max_length=30, null=True, blank=True)
    def __str__(self):
        return self.sub_name


class Loccat(models.Model):
    name=models.CharField(max_length=1000, null=True,blank=True)
    def __str__(self):
        return self.name

class Staller(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    loc_cat = models.ForeignKey(Loccat, on_delete=models.SET_NULL, null=True, blank=True)  
    name = models.CharField(max_length=300)
    address = models.CharField(max_length=400)
    category = models.ManyToManyField(Category, related_name='categor')
    video = EmbedVideoField(null=True)
    egit = models.ForeignKey(Egit, on_delete=models.CASCADE, null=True, blank=True)
    contact = models.CharField(max_length=12, default='1234')
    timings = models.CharField(max_length=14)
    rating = models.FloatField(default=0)
    keywords = models.CharField(max_length=1000, default='spicy', null=True)
    rush=models.BooleanField(default=False)
    likes = models.PositiveIntegerField(default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    

    
    def __str__(self):
        return self.name

    def update_rating(self):
        ratings = self.ratings.all()  # Use related name
        avg_rating = sum(r.rating for r in ratings) / len(ratings) if ratings else 0
        self.rating = avg_rating
        self.save()
    def get_location(self):
        return f"{self.latitude}, {self.longitude}" if self.latitude and self.longitude else "Location not set"
    def get_absolute_url(self):
        return reverse("detail", kwargs={"name": self.name})
    

class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    staller = models.ForeignKey(Staller, related_name='ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(default=1)

    class Meta:
        unique_together = ('user', 'staller')

    def __str__(self):
        return f'{self.user} - {self.staller} - {self.rating}'
    
class Foo_Category(models.Model):
    sh_owner=models.ForeignKey(Staller, on_delete=models.CASCADE, default='')
    foo_name=models.CharField(max_length=30, null=True)
    def __str__(self):
        return self.foo_name

class MenuItems(models.Model):
    owner = models.ForeignKey(Staller, on_delete=models.CASCADE, null=True, related_name='menu_items')
    menu_photo = models.ImageField(upload_to='static/images/', null=True, blank=True)
    name = models.CharField(max_length=200)
    foo_cat = models.ForeignKey(Foo_Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Change normal_price to Decimal
    normal_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    premium_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    description = models.CharField(max_length=200, null=True, blank=True)
    stock = models.IntegerField(null=True, blank=True)
    rating = models.FloatField(default=0)
    available = models.BooleanField(default=False)

    def __str__(self):
        return self.name


    def update_rating(self):
        foo_ratings = self.foo_ratings.all()  # Use related name
        avg_rating = sum(r.rating for r in foo_ratings) / len(foo_ratings) if foo_ratings else 0
        self.rating = avg_rating
        self.save()


class FooRating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    menu = models.ForeignKey(MenuItems, related_name='foo_ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(default=1)

    class Meta:
        unique_together = ('user', 'menu')

    def __str__(self):
        return f'{self.user} - {self.menu} - {self.rating}'



class Following(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')
    staller = models.ForeignKey(Staller, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('user', 'staller') 

    def __str__(self):
        return f'{self.user.username} follows {self.staller.name}'
    


class New_offer(models.Model):
    owner=models.ForeignKey(Staller,on_delete=models.CASCADE, related_name='offers')
    title=models.CharField(max_length=100)
    offer_photo = models.ImageField(upload_to='static/images/offer_pics/')
    message=models.CharField(max_length=10000)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title





class UserLike(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    staller = models.ForeignKey(Staller, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'staller')  # Ensure a user can like the same staller only once



class Subscription(models.Model):
    PLAN_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=10, choices=PLAN_CHOICES)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()

    def __str__(self):
        return f'{self.user.username} - {self.plan_type}'
    


# order
import random


class Order(models.Model):  
    ORDER_STATUS = [  
        ('in_process', 'In Process'),  
        ('done', 'Done'),  
    ]  

    order_number = models.CharField(max_length=1000, unique=True)  
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  
    stall_owner = models.ForeignKey(Staller, on_delete=models.CASCADE)  
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default='in_process')  
    created_at = models.DateTimeField(auto_now_add=True)  
    status_pay = models.CharField(max_length=20, default="PENDING")

    def save(self, *args, **kwargs):  
        if not self.order_number:  
            self.order_number = str(random.randint(10000, 99999))  # Generate random 5-digit order number  
        super(Order, self).save(*args, **kwargs)  

    def __str__(self):  
        return f"Order {self.order_number} - {self.user.username} - {self.stall_owner.owner}"  


class Cart(models.Model):  
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  
    related = models.ForeignKey(Staller, on_delete=models.CASCADE, null=True)  
    items = models.ManyToManyField(MenuItems, through='CartItem')  
    created_at = models.DateTimeField(auto_now_add=True)  
    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')  

    def total_price(self):  
        total = Decimal('0.00')  # Initialize as Decimal  
        for cart_item in self.cart_items.all():  
            total += cart_item.total_price()  # Ensure total_price() returns a Decimal  
        return total  

    def __str__(self):  
        return f"Cart for {self.user.username}" + (f" - Order {self.order.order_number}" if self.order else "")  


class CartItem(models.Model):  
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)  
    menu_item = models.ForeignKey(MenuItems, on_delete=models.CASCADE)  
    quantity = models.PositiveIntegerField(default=1)  

    def total_price(self):  
        return self.menu_item.normal_price * self.quantity  

    def __str__(self):  
        return f"{self.quantity} x {self.menu_item.name} in cart"
    

