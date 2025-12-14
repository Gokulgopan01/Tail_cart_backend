from django.db import models
from rest_framework import generics


class LoginModule(models.Model): 
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150)
    email_address = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username


class PetModule(models.Model):  
    pet_id = models.AutoField(primary_key=True)
    pet_name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)
    breed = models.CharField(max_length=50)
    owner = models.ForeignKey(LoginModule, on_delete=models.CASCADE, related_name="pets")

    def __str__(self):
        return f"{self.pet_name} ({self.species})"


class UserProfile(models.Model):  
    profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(LoginModule, on_delete=models.CASCADE, related_name="profile")
    owner_name = models.CharField(max_length=120)
    owner_address = models.CharField(max_length=255)
    owner_phone = models.CharField(max_length=15) 
    owner_city = models.CharField(max_length=100, blank=True, null=True)
    owner_state = models.CharField(max_length=255, null=True, blank=True)
    

    def __str__(self):
        return self.owner_name
    
class Product(models.Model):
    model = models.CharField(max_length=255)
    product_info =models.TextField(blank=True, null=True)
    price = models.IntegerField()
    breed = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/')
    reviews = models.TextField(blank=True, null=True)
    deals = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.name

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

    STATUS_CHOICES = [
        ('In Cart', 'In Cart'),
        ('Ordered', 'Ordered'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]

    cart_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(LoginModule, on_delete=models.CASCADE)
    pet = models.ForeignKey(PetModule, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='In Cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.owner.username} - {self.product.name} ({self.status})"
    

class PetAlerts(models.Model):
    alert_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(LoginModule, on_delete = models.CASCADE)
    pet = models.ForeignKey(PetModule, on_delete = models.CASCADE)
    alert_type = models.CharField(choices = [('Vaccination', 'Vaccination'), ('Medication', 'Medication'), ('Appointment', 'Appointment')], max_length=50)
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    frequency = models.CharField(choices = [('One-time', 'One-time'), ('Daily', 'Daily'), ('Weekly', 'Weekly'), ('Monthly', 'Monthly')], max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

