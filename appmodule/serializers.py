from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import LoginModule, UserProfile, PetModule, Product, Documents, CartItem, PetAlerts


class LoginSerializer(serializers.Serializer):
    email_address = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email_address = data.get("email_address")
        password = data.get("password")

        try:user = LoginModule.objects.get(email_address=email_address)
        except LoginModule.DoesNotExist:raise serializers.ValidationError("User not found")

        if user.password != password:raise serializers.ValidationError("Incorrect password")

        data['user'] = user
        return data
    

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginModule
        fields = ['username', 'email_address', 'password']

    def create(self, validated_data):
        user = LoginModule.objects.create(**validated_data)
        return user


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetModule
        fields = ['pet_id', 'pet_name', 'species', 'breed', 'owner']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'model', 'product_info', 'price', 'breed', 'quantity', 'image', 'reviews', 'deals']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
    
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Documents
        fields=['document_id','user','pet','document_title','document_file','upload_date']

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source = 'product.model',read_only=True)
    product_price = serializers.IntegerField(source = 'product.price',read_only=True)
    pet_name = serializers.CharField(source = 'pet.pet_name',read_only=True)
    product_image = serializers.ImageField(source = 'product.image',read_only=True)
    class Meta:
        model = CartItem
        fields = ['cart_id', 'quantity', 'status', 'product_name', 'product_price', 'product_image', 'pet_name', "created_at","updated_at","owner","pet","product"]



class UserProfileSerializer(serializers.ModelSerializer):
    pets = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.IntegerField(write_only=True) 

    class Meta:
        model = UserProfile
        fields = [ 'user_id', 'owner_name', 'owner_address', 'owner_phone',"owner_city","owner_state", 'pets']

    def get_pets(self, obj):
        return PetSerializer(obj.user.pets.all(), many=True).data
    
    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        try: user = LoginModule.objects.get(user_id=user_id)
        except LoginModule.DoesNotExist:raise serializers.ValidationError("User not found")
        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile
    
class PetAlertSerializer(serializers.ModelSerializer):

    class Meta:
        model = PetAlerts 
        fields = ['alert_id','user', 'pet', 'alert_type', 'title', 'due_date', 'frequency', 'is_active']

        def create(self, validated_data):
            alert = PetAlerts.objects.create(**validated_data)
            return alert