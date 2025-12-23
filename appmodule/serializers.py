from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import LoginModule, UserProfile, PetModule, Product, Documents, CartItem, PetAlerts


class LoginSerializer(serializers.Serializer):
    email_address = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email_address = data.get("email_address")
        password = data.get("password")

        try:
            # Look up the LoginModule via the related User's email
            user_module = LoginModule.objects.get(user__email=email_address)
        except LoginModule.DoesNotExist:
            raise serializers.ValidationError("No account found, login again")

        if not user_module.user.check_password(password):
            raise serializers.ValidationError("Incorrect password")

        data['user'] = user_module
        return data
    

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email_address = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(default='USER') 

    def create(self, validated_data):
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email_address'],
            password=validated_data['password']
        )

        # 2. Create LoginModule linked to User
        login_module = LoginModule.objects.create(
            user=user,
            role=validated_data.get('role', 'USER')
        )
        return login_module


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