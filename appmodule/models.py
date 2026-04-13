from django.db import models
from django.contrib.auth.models import User
from rest_framework import generics
import uuid
from django.utils import timezone
from datetime import timedelta


class LoginModule(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, default='USER')

    def __str__(self):
        return self.user.username


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(LoginModule, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.created_at + timedelta(minutes=10)

    def mark_used(self):
        self.is_used = True
        self.save()


class PetAlert(models.Model):
    pet = models.ForeignKey('PetModule', on_delete=models.CASCADE, related_name="alerts")
    sender_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=255)
    message = models.TextField(blank=True, null=True)
    is_resolved = models.TextField(default=False,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PetModule(models.Model):  
    pet_id = models.AutoField(primary_key=True)
    pet_name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)
    breed = models.CharField(max_length=50)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    about = models.TextField(blank=True, null=True)

    pet_photo = models.ImageField(upload_to='pet_photos/', blank=True, null=True)
    pet_qr_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_lost = models.BooleanField(default=False)

    owner = models.ForeignKey(LoginModule, on_delete=models.CASCADE, related_name="pets")

    def __str__(self):
        return f"{self.pet_name} ({self.species})"


class UserProfile(models.Model):  

    profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(LoginModule, on_delete=models.CASCADE, related_name="profile")
    owner_name = models.CharField(max_length=120)
    owner_address = models.CharField(max_length=255)
    owner_phone = models.CharField(max_length=15) 
    owner_email = models.EmailField(blank=True, null=True)
    owner_city = models.CharField(max_length=100, blank=True, null=True)
    owner_state = models.CharField(max_length=255, null=True, blank=True)
    owner_photo = models.ImageField(upload_to='owner_photos/', blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=120, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.owner_name
    

class Product(models.Model):
    product_material = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    reviews_stars = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    colours = models.JSONField(default=list, blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_long_description =models.TextField(blank=True, null=True)
    product_other_specifications = models.TextField(blank=True, null=True)
    thumbnail_image = models.ImageField(upload_to='products/', null=True, blank=True)
    second_image_1 = models.ImageField(upload_to='products/', null=True, blank=True)
    in_stock = models.BooleanField(default=True)
    deals = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.product_name


class Documents(models.Model):
    document_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(LoginModule, on_delete=models.CASCADE, related_name="documents")
    pet = models.ForeignKey(PetModule, on_delete=models.CASCADE, related_name="documents")
    document_title = models.CharField(max_length=200)
    document_file = models.FileField(upload_to='documents/')
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.document_name


class CartItem(models.Model):

    cart_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(LoginModule, on_delete=models.CASCADE)
    pet = models.ForeignKey(PetModule, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.owner.username} - {self.product.product_name}"
    

class Order(models.Model):
#check out model with status choices and order items

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
        ('Refunded', 'Refunded')
    ]

    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(LoginModule, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    order_date = models.DateField(auto_now_add=True)

    #tracking statuses
    confirmed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    out_for_delivery_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    

class PetRemainders(models.Model):

    alert_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(LoginModule, on_delete = models.CASCADE)
    pet = models.ForeignKey(PetModule, on_delete = models.CASCADE)
    
    alert_type = models.CharField(choices = [
    ('Health', 'Health'),
    ('Grooming', 'Grooming'),
    ('Activity', 'Activity'),
    ('Nutrition', 'Nutrition'),
    ('Administrative', 'Administrative')
    ], max_length=50)
    
    alert_subtype = models.CharField(choices = [('Vaccination', 'Vaccination'),
    ('Medication', 'Medication'),
    ('Vet Appointment', 'Vet Appointment'),
    ('Deworming', 'Deworming'),
    ('Flea Treatment', 'Flea Treatment'),
    ('Bath', 'Bath'),
    ('Nail Trimming', 'Nail Trimming'),
    ('Teeth Cleaning', 'Teeth Cleaning'),
    ('Walk', 'Walk'),
    ('Exercise', 'Exercise'),
    ('Insurance Renewal', 'Insurance Renewal'),
    ('License Renewal', 'License Renewal')
    ], max_length=50)
    
    title = models.CharField(max_length=200)
    remainder_date = models.DateField()
    reminder_time = models.TimeField(null=True, blank=True)
    frequency = models.CharField(choices = [('One-time', 'One-time'), ('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly'),('Yearly', 'Yearly')], max_length=50)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pet.pet_name} - {self.alert_type} Alert"