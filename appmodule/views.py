from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Avg


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from .permissions import IsAdminRole

from .models import UserProfile, PetModule, Product, Documents, CartItem, PetRemainders, LoginModule, PetAlert, Order, OrderItem, ProductReview
from .serializers import (LoginSerializer, RegisterSerializer,ForgotPasswordSerializer, ResetPasswordSerializer, UserProfileSerializer, OrderSerializer,UserProfileShareSerializer,
PetSerializer, ProductSerializer, DocumentSerializer, CartItemSerializer, PetRemainderSerializer, PublicPetSerializer,PetDoctorSerializer,PetQRSerializer,PetShareSerializer)

from django.core.mail import send_mail
from django.conf import settings
from uuid import UUID 
from google import genai
from django.utils import timezone
client = genai.Client(api_key="AIzaSyAhNblR5szagAzKuETt-5LitFTsMe3-VSU")




#Register View    
class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user_module = serializer.save()

            refresh = RefreshToken.for_user(user_module.user)
            return Response({
                "message": "User registered successfully",
                "user_id": user_module.user_id,
                "username": user_module.user.username,  
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
#Login View
class LoginView(APIView):
    '''Login user with email and password'''

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            if user is None:
                return Response( {"message": "No account found, login again"},  status=status.HTTP_404_NOT_FOUND )
            
            refresh = RefreshToken.for_user(user.user) 
            return Response({
                "message": "Login successful",
                "user_id": user.user_id,
                "username": user.user.username, 
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user.role,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

    def delete(self, request):
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

#Delet User
class DeleteUserByIdView(APIView):

    def delete(self, request, user_id):
        try:
            user = LoginModule.objects.get(user_id=user_id)
            user.delete()
            return Response(
                {"message": "User and all related data deleted successfully"},
                status=status.HTTP_200_OK
            )
        except LoginModule.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )



class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            otp_obj = serializer.create_otp()

            # Send OTP via email
            send_mail(
                subject="TailCart Services - Password Reset OTP",
                message=f"Your one time OTP for login to the account is : {otp_obj.otp}. Please dont send this OTP to anyone, it is valid for 10 minutes only.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[serializer.validated_data['email_address']],
            )

            return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#only shared username and image
class UserProfileSharedView(APIView):
    '''Share only username image'''

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id: return Response('error: user_id is required', status=status.HTTP_400_BAD_REQUEST)
        try: profile = UserProfile.objects.only(
        "owner_name",
        "owner_photo"
    ).get(user__user_id=user_id)
        except UserProfile.DoesNotExist:return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileShareSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

#Users Profile View
class UserProfileView(APIView):
    '''Create, Retrieve, Update User Profile'''
    permission_classes = [IsAuthenticated]

    #create profile
    def post(self, request):
        '''Create user profile'''

        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():profile = serializer.save() ;return Response({"message": "profile created", "profile_id": profile.profile_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Get profile of users
    def get(self, request):
        '''Retrieve user profile'''

        user_id = request.query_params.get('user_id')
        if not user_id: return Response('error: user_id is required', status=status.HTTP_400_BAD_REQUEST)
        try: profile = UserProfile.objects.get(user__user_id=user_id)
        except UserProfile.DoesNotExist:return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #Update profile of users
    def put(self, request):
        '''update entire user profile'''

        user_id = request.data.get('user_id')
        if not user_id: return Response('error: user_id is required', status=status.HTTP_400_BAD_REQUEST)
        try: profile = UserProfile.objects.get(user__user_id=user_id)
        except UserProfile.DoesNotExist: return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        #user id no need to update
        data = request.data.copy()
        data.pop("user_id", None)

        serializer = UserProfileSerializer(profile, data=data, partial=True)
        if serializer.is_valid(): serializer.save() ;return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Update profile
    def patch(self, request):
        """Partial update of user profile"""

        user_id = request.data.get("user_id")
        if not user_id: return Response({"error": "user_id query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        try: profile = UserProfile.objects.get(user__user_id=user_id)
        except UserProfile.DoesNotExist: return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        #user id no need to update
        data = request.data.copy()
        data.pop("user_id", None)

        serializer = UserProfileSerializer(profile, data=data, partial=True) 
        if serializer.is_valid(): serializer.save() ;return Response({"message": "profile partially updated", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#alerts reolve for lost pet
class ResolveAlertView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        alert_id = request.data.get("alert_id")
        user_id = request.data.get("user_id")

        if not alert_id or not user_id: return Response({"error": "alert_id and user_id are required"}, status=status.HTTP_400_BAD_REQUEST )

        try: alert = PetAlert.objects.get( id=alert_id, pet__owner__user_id=user_id )
        except PetAlert.DoesNotExist: return Response({"error": "Alert not found"}, status=status.HTTP_404_NOT_FOUND )

        alert.is_resolved = True
        alert.save()
        return Response( {"message": "Alert resolved successfully"}, status=status.HTTP_200_OK )
    
class getqrPetview(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pet_id):
        try:
            pet = PetModule.objects.get(pet_id=pet_id)
            serializer = PetQRSerializer(pet)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PetModule.DoesNotExist:
            return Response({"error": "Pet not found"}, status=404)
        
class getqrPublicPetView(APIView):
    permission_classes = [AllowAny]

    def get(self,request, qr_uuid):
        try:
            pet = PetModule.objects.get(pet_qr_uuid=qr_uuid)
            serializer = PetQRSerializer(pet)
            if pet.is_lost:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "This pet is not reported as lost"}, status=status.HTTP_400_BAD_REQUEST)
        except PetModule.DoesNotExist:
            return Response({"error": "Pet not found"}, status=404)

class PrivatePetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pet_id):
        try:
            pet = PetModule.objects.select_related(
                "owner", "owner__profile"
            ).get(
                pet_id=pet_id,
                owner=request.user.loginmodule  # ✅ FIX
            )
        except PetModule.DoesNotExist:
            return Response({"error": "Pet not found"}, status=404)

        serializer = PublicPetSerializer(pet)
        return Response(serializer.data, status=200)
    

class PublicPetView(APIView):
    permission_classes = []

    def get(self, request, qr_uuid):
        try:
            # Normalize UUID (add hyphens if missing)
            qr_uuid = str(UUID(qr_uuid))
            pet = PetModule.objects.select_related("owner", "owner__profile").get(pet_qr_uuid=qr_uuid)
        except (PetModule.DoesNotExist, ValueError):
            return Response({"error": "Pet not found"}, status=404)

        serializer = PublicPetSerializer(pet)
        return Response(serializer.data, status=200)

#create alerts
class CreatePetAlertView(APIView):
    permission_classes = []  # PUBLIC (QR scan)

    def post(self, request):
        pet_id = request.data.get("pet_id")
        location = request.data.get("location")

        if not pet_id or not location:
            return Response(  {"error": "pet_id and location are required"},status=status.HTTP_400_BAD_REQUEST )

        try: pet = PetModule.objects.get(pet_id=pet_id)
        except PetModule.DoesNotExist: return Response( {"error": "Pet not found"},status=status.HTTP_404_NOT_FOUND)

        alert = PetAlert.objects.create( pet=pet, sender_name=request.data.get("sender_name"), phone=request.data.get("phone"), location=location, message=request.data.get("message") )

        return Response( {"message": "Alert created successfully", "alert_id": alert.id}, status=status.HTTP_201_CREATED)


#Share just pet image and name
class PetShareView(APIView):
    '''Share pet image and name only'''
    permission_classes = [IsAuthenticated]

    def get(self, request):
        '''Show pets'''

        user_id = request.query_params.get('user_id')
        if not user_id: return Response('error: user_id is required', status=status.HTTP_400_BAD_REQUEST)

        pets = (PetModule.objects.filter(owner__user_id=user_id).only("pet_id", "pet_name", "pet_photo"))
        if not pets.exists():
            return Response({"error": "No pets found"},status=status.HTTP_404_NOT_FOUND)
        
        serializer = PetShareSerializer(pets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#pets View
class PetView(APIView):
    '''Create and List Pets'''
    permission_classes = [IsAuthenticated]

    #create pets
    def post(self, request):
        '''Create a new pet for a user'''

        serializer = PetSerializer(data=request.data)
        if serializer.is_valid(): pet = serializer.save() ;return Response({"message": "Pet created successfully", "pet_id": pet.pet_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #get pets details
    def get(self, request):
        '''Show pets of a user'''

        user_id = request.query_params.get('user_id')
        if not user_id: return Response('error: user_id is required', status=status.HTTP_400_BAD_REQUEST)
        pets = PetModule.objects.filter(owner__user_id=user_id)
        if not pets.exists(): return Response({"error": "you have not pets now"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PetSerializer(pets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #update pets infos
    def put(self, request):
        '''Update pet information'''

        user_id = request.data.get('user_id')
        pet_id = request.data.get('pet_id')
        if not user_id or not pet_id: return Response('error: user_id and pet_id are required', status=status.HTTP_400_BAD_REQUEST)
        try: pet = PetModule.objects.get(pet_id=pet_id, owner__user_id=user_id)
        except PetModule.DoesNotExist: return Response({"error": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PetSerializer(pet, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({"message": "Pet updated successfully"}, status=status.HTTP_200_OK)
    
    #delete pets
    def delete(self, request):
        '''Delete a pet'''

        user_id = request.query_params.get('user_id')
        pet_id = request.query_params.get('pet_id')
        if not user_id or not pet_id: return Response('error: user_id and pet_id are required', status=status.HTTP_400_BAD_REQUEST)
        try: pet = PetModule.objects.get(pet_id=pet_id, owner__user_id=user_id)
        except PetModule.DoesNotExist: return Response({"error": "Pet not found"}, status=status.HTTP_404_NOT_FOUND)
        pet.delete()
        return Response({"message": "Pet deleted successfully"}, status=status.HTTP_200_OK)


#products View
class ProductView(APIView):
    """List and Create products"""

    authentication_classes = []  
    permission_classes = [AllowAny]

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAdminRole()]

    #get all products
    def get(self, request, id=None):

        if id is not None:
            try:
                product = Product.objects.get(id=id)
            except Product.DoesNotExist:
                return Response({"error": "Product not found"}, status=404)

            serializer = ProductSerializer(product, context={'request': request})
            return Response(serializer.data)

        products = Product.objects.all().order_by('-id')

        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    #create products admin only
    def post(self, request):
        """Create a new product"""
    
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save()
            return Response( {"message": "Product created successfully", "product_id": product.id},status=status.HTTP_201_CREATED,  )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #edit product details
    def put(self, request, product_id=None):
        '''update entire user profile'''

        if product_id is None: return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try: product = Product.objects.get(id=product_id)
        except Product.DoesNotExist: return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid(): serializer.save() ;return Response({"message": "Product updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #dekete product
    def delete(self, request, product_id=None):
        """Delete a product"""

        if product_id is None:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_200_OK)
 


class AddReviewView(APIView):

    permission_classes = [IsAuthenticated]  

    def post(self, request):
        product_id = request.data.get('product')
        rating = request.data.get('rating')
        comment = request.data.get('comment')

        product = get_object_or_404(Product, id=product_id)

        try:
            login_user = LoginModule.objects.get(user=request.user)
        except LoginModule.DoesNotExist:
            return Response({"error": "User profile not found"}, status=400)

        #dupliccation check
        if ProductReview.objects.filter(product=product, user=login_user).exists():
            return Response({"error": "You already reviewed this product"}, status=400)

        review = ProductReview.objects.create( product=product, user=login_user, rating=rating, comment=comment)

        # ✅ Update product average rating
        avg_rating = product.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        product.reviews_stars = round(avg_rating, 1)
        product.save()

        return Response({
            "message": "Review added successfully",
            "review_id": review.id
        }, status=status.HTTP_201_CREATED)
    

#Documents View
class DocumentView(APIView):
    """Create and List Documents"""

    #create pet documents
    def post(self, request):
        """Create a new document for a user and pet"""
        user_id = request.data.get("user")
        pet_id = request.data.get("pet")
        if not PetModule.objects.filter(pet_id=pet_id).exists():
            return Response( {"error": "Pet not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            owner = LoginModule.objects.get(user_id=user_id)
        except LoginModule.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pet = PetModule.objects.get(pet_id=pet_id)
        except PetModule.DoesNotExist:
            return Response({"error": "Pet not found."}, status=status.HTTP_400_BAD_REQUEST)

        if pet.owner != owner:
            return Response(
                {"error": "This pet does not belong to the user."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            document = serializer.save()
            return Response({"message": "Document uploaded successfully", "document_id":document.document_id}, status=status.HTTP_201_CREATED,)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #get pet documents
    def get(self, request):
        """List Documents of user"""

        user_id = request.query_params.get('user_id')
        if not user_id: return Response('error: user_id is required', status=status.HTTP_400_BAD_REQUEST)
        documents = Documents.objects.filter(user__user_id=user_id)
        if not documents.exists(): return Response([], status=status.HTTP_200_OK)
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #delete Documents
    def delete(self, request):
        '''Delete a document'''

        document_id = request.query_params.get('document_id')
        if not document_id:
            return Response({'error': 'document_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            document = Documents.objects.get(document_id=document_id)
            document.delete()
            return Response( {'message': 'Document deleted successfully'}, status=status.HTTP_200_OK)
        except Documents.DoesNotExist:
            return Response( {'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND )
    
#cart view
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('user_id')

        try:
            owner = LoginModule.objects.get(user_id=user_id)
        except LoginModule.DoesNotExist:
            return Response({"error": "User not found"}, status=400)
        
        cart_items = CartItem.objects.filter(owner=owner)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #create cart item
    def post(self, request):
        user_id = request.data.get("owner")
        pet_id = request.data.get("pet")

        try:
            owner = LoginModule.objects.get(user_id=user_id)
        except LoginModule.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pet = PetModule.objects.get(pet_id=pet_id)
        except PetModule.DoesNotExist:
            return Response({"error": "Pet not found."}, status=status.HTTP_400_BAD_REQUEST)

        if pet.owner != owner:
            return Response({"error": "This pet does not belong to the user."},status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Item added to cart successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #update cart item
    def put(self, request):
        '''update entire user profile'''

        user_id = request.data.get('user_id')
        owner = LoginModule.objects.get(user_id=user_id)
        if not owner: return Response('error: user_id is required', status=status.HTTP_400_BAD_REQUEST)

        cart_id = request.data.get('cart_id')
        if not cart_id:return Response({'error': 'cart_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:  cart_item = CartItem.objects.get(cart_id=cart_id,owner=owner)
        except CartItem.DoesNotExist: return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CartItemSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid(): serializer.save() ;return Response({'message': 'Cart item updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #delete cart item
    def delete(self, request):
        """Delete a cart item"""
        cart_id = request.query_params.get('cart_id')
        if not cart_id:
            return Response({'error': 'cart_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_id = request.data.get('user_id')
        owner = LoginModule.objects.get(user_id=user_id)
        if not owner: return Response('error: user_id is required', status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id,owner=owner)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        cart_item.delete()
        return Response({'message': 'Cart item deleted successfully'}, status=status.HTTP_200_OK)



#order placement and management view 
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        user_id = request.data.get("user")
        login = LoginModule.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(owner=login)

        if not cart_items.exists():
            return Response({"message": "Cart is empty"}, status=400)
        
        total = sum(item.product.selling_price * item.quantity for item in cart_items)

        #create order
        order = Order.objects.create( user=login,total_price=total, confirmed_at=timezone.now() )
        for item in cart_items:
            OrderItem.objects.create(  order=order,  product=item.product, quantity=item.quantity, price=item.product.selling_price )

        cart_items.delete()
        return Response({"message": "Order placed successfully"}, status=201)
    


class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        login = request.user.loginmodule

        orders = Order.objects.filter(user=login)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    

#Pets Alert View
class PetRemainderView(APIView):
    '''pet alert management'''

    #create pet alert
    def post(self, request):
        user_id = request.data.get("user")
        pet_id = request.data.get("pet")

        try:
            owner = LoginModule.objects.get(user_id=user_id)
        except LoginModule.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pet = PetModule.objects.get(pet_id=pet_id)
        except PetModule.DoesNotExist:
            return Response({"error": "Pet not found."}, status=status.HTTP_400_BAD_REQUEST)

        if pet.owner != owner:
            return Response(
                {"error": "This pet does not belong to the user."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PetRemainderSerializer(data = request.data)
        if serializer.is_valid():
            alert = serializer.save()
            return Response({"message": "Pet remainder succesfully created", "alert_id": alert.alert_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #get pets alerts of user
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id :
            return Response("error: user_id is mandatory", status = status.HTTP_400_BAD_REQUEST)
        
        alerts = PetRemainders.objects.filter(user__user_id=user_id)
        serializer = PetRemainderSerializer(alerts, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    #update pet alerts
    def put (self, request):
        user_id = request.data.get('user_id')
        if not user_id: return Response('error: user_id is required', status=status.HTTP_400_BAD_REQUEST)
        alert_id = request.data.get('alert_id')
        if not alert_id:return Response({'error': 'alert_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        owner = LoginModule.objects.get(user_id=user_id)
        try: alert = PetRemainders.objects.get(alert_id=alert_id,user=owner)
        except PetRemainders.DoesNotExist: return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PetRemainderSerializer(alert, data=request.data, partial=True) 
        if serializer.is_valid(): serializer.save() ;return Response({'message': 'Pet remainder updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #delete pet alert
    def delete(self, request):  
        user_id = request.data.get('user_id')
        alert_id = request.query_params.get('alert_id')
        if not alert_id:
            return Response({'error': 'alert_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        owner = LoginModule.objects.get(user_id=user_id)
        try:
            alert = PetRemainders.objects.get(alert_id=alert_id,user=owner)
        except PetRemainders.DoesNotExist:
            return Response({'error': 'remainder not found'}, status=status.HTTP_404_NOT_FOUND)
        
        alert.delete()
        return Response({'message': 'Pet remainder deleted successfully'}, status=status.HTTP_200_OK)
    
class PetDoctorView(APIView):

    def post(self, request):
        serializer = PetDoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_prompt = serializer.validated_data["prompt"]

        response = client.models.generate_content(
            model="gemini-1.5-pro",
            contents=f"""
            You are a professional veterinary doctor.
            Answer clearly and simply.
            Do NOT give emergency or life-threatening advice.

            Pet owner's question:
            {user_prompt}
            """
        )

        return Response(
            {"reply": response.text},
            status=status.HTTP_200_OK
        )
