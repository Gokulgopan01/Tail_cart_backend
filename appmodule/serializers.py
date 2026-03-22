from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import random
from .models import LoginModule, UserProfile, PetModule, Product, Documents, CartItem, PetRemainders, PetAlert, PasswordResetOTP, Order, OrderItem


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
        
        user = User.objects.create_user( username=validated_data['username'], email=validated_data['email_address'], password=validated_data['password'] )

        # 2. Create LoginModule linked to User
        login_module = LoginModule.objects.create(user=user,role=validated_data.get('role', 'USER') )
        return login_module
    

class ForgotPasswordSerializer(serializers.Serializer):
    email_address = serializers.EmailField()

    def validate_email_address(self, value):
        try:
            user_module = LoginModule.objects.get(user__email=value)
        except LoginModule.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")
        return value

    def create_otp(self):
        email = self.validated_data['email_address']
        user_module = LoginModule.objects.get(user__email=email)

        otp = str(random.randint(100000, 999999))  # 6-digit OTP
        otp_obj = PasswordResetOTP.objects.create(user=user_module, otp=otp)
        return otp_obj

class ResetPasswordSerializer(serializers.Serializer):
    email_address = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email_address")
        otp = data.get("otp")
        new_password = data.get("new_password")

        try:
            user_module = LoginModule.objects.get(user__email=email)
        except LoginModule.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")

        try:
            otp_obj = PasswordResetOTP.objects.filter(user=user_module, otp=otp, is_used=False).latest('created_at')
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")

        if not otp_obj.is_valid():
            raise serializers.ValidationError("OTP expired or already used.")

        data['user_module'] = user_module
        data['otp_obj'] = otp_obj
        return data

    def save(self):
        user_module = self.validated_data['user_module']
        otp_obj = self.validated_data['otp_obj']
        new_password = self.validated_data['new_password']

        user_module.user.set_password(new_password)
        user_module.user.save()

        otp_obj.mark_used()
        return user_module


class LostPetAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetAlert  # This is the correct model
        fields = ['id', 'sender_name', 'phone', 'location', 'message', 'created_at']

class PetQRSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetModule
        fields = ['pet_id', 'pet_name', 'species', 'breed','age', 'owner', 'pet_qr_uuid'  ]


class PetSerializer(serializers.ModelSerializer):
    alerts = serializers.SerializerMethodField()

    class Meta:
        model = PetModule
        fields = ['pet_id', 'pet_name', 'species', 'breed','age', 'owner', 'is_lost', 'alerts','pet_photo'  ]

    def get_alerts(self, obj):
        alerts_qs = obj.alerts.filter(is_resolved=False)
        return LostPetAlertSerializer(alerts_qs, many=True).data
    
    
class PublicPetSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.profile.owner_name', read_only=True)
    owner_address = serializers.CharField(source='owner.profile.owner_address', read_only=True)
    owner_phone = serializers.CharField(source='owner.profile.owner_phone', read_only=True)
    owner_city = serializers.CharField(source='owner.profile.owner_city', read_only=True)
    owner_state = serializers.CharField(source='owner.profile.owner_state', read_only=True)
    pet_photo = serializers.ImageField(read_only=True)

    class Meta:
        model = PetModule
        fields = [ "pet_name", "species", "breed", "age", "pet_photo", "is_lost","owner_name", "owner_address", "owner_phone", "owner_city",  "owner_state",]


class ProductSerializer(serializers.ModelSerializer):

    thumbnail_image = serializers.ImageField(required=False)
    second_image_1 = serializers.ImageField(required=False)

    class Meta:
        model = Product
        fields = [
            'id',
            'product_material',
            'product_name',
            'reviews_stars',
            'colours',
            'original_price',
            'selling_price',
            'product_long_description',
            'product_other_specifications',
            'thumbnail_image',
            'second_image_1',
            'in_stock',
            'deals'
        ]

        
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Documents
        fields=['document_id','user','pet','document_title','document_file','upload_date']



class CartItemSerializer(serializers.ModelSerializer):

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_details = ProductSerializer(source='product', read_only=True)
    pet_name = serializers.CharField(source='pet.pet_name', read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'cart_id',
            'quantity',
            'owner',
            'pet',
            'pet_name',
            'product',        
            'product_details',  
            'created_at'
        ]





class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'status', 'total_price', 'items']






class UserProfileSerializer(serializers.ModelSerializer):
    pets = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.IntegerField(write_only=True) 

    class Meta:
        model = UserProfile
        fields = [ 'user_id', 'owner_name', 'owner_address', 'owner_phone', 'owner_email', "owner_city","owner_state", 'pets','owner_photo', 'emergency_contact_name', 'emergency_contact_phone', 'created_at']

    def get_pets(self, obj):
        return PetSerializer(obj.user.pets.all(), many=True).data
    
    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        try: user = LoginModule.objects.get(user_id=user_id)
        except LoginModule.DoesNotExist:raise serializers.ValidationError("User not found")
        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile

  
    
class PetRemainderSerializer(serializers.ModelSerializer):

    class Meta:
        model = PetRemainders 
        fields = ['alert_id','user', 'pet', 'alert_type', 'alert_subtype', 'title', 'reminder_time','remainder_date', 'frequency', 'notes', 'is_active', 'completed_at', 'created_at']

        def create(self, validated_data):
            alert = PetRemainders.objects.create(**validated_data)
            return alert
        

class PetDoctorSerializer(serializers.Serializer):
    prompt = serializers.CharField()