from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import UserProfile, PetModule, Product, Documents, CartItem, PetAlerts
from .serializers import LoginSerializer, RegisterSerializer, UserProfileSerializer, PetSerializer, ProductSerializer, DocumentSerializer, CartItemSerializer, PetAlertSerializer


#Login View
class LoginView(APIView):
    '''Login user with email and password'''

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(): user = serializer.validated_data['user'];return Response({"message": "Login successful","user_id": user.user_id,"username": user.username})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Register View    
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():user = serializer.save();return Response({"message": "User registered successfully", "user_id": user.user_id, "username": user.username}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Users Profile View
class UserProfileView(APIView):
    '''Create, Retrieve, Update User Profile'''

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
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid(): serializer.save() ;return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Update profile
    def patch(self, request):
        """Partial update of user profile"""

        user_id = request.data.get("user_id")
        if not user_id: return Response({"error": "user_id query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        try: profile = UserProfile.objects.get(user__user_id=user_id)
        except UserProfile.DoesNotExist: return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True) 
        if serializer.is_valid(): serializer.save() ;return Response({"message": "profile partially updated", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#pets View
class PetView(APIView):
    '''Create and List Pets'''

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

    permission_classes = [AllowAny] 

    #get all products
    def get(self, request):
        """List all products"""
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True , context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #create products admin only
    def post(self, request):
        """Create a new product"""
        user_id = request.data.get("user")
        pet_id = request.data.get("pet")
        if not PetModule.objects.filter(pet_id=pet_id).exists():
            return Response( {"error": "Pet not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not PetModule.objects.filter(pet_id=pet_id, owner=user_id).exists():
            return Response( {"error": "This pet does not belong to the user."}, status=status.HTTP_400_BAD_REQUEST )
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save()
            return Response( {"message": "Product created successfully", "product_id": product.id},status=status.HTTP_201_CREATED,  )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #edit product details
    def put(self, request):
        '''update entire user profile'''

        user_id = request.data.get('user_id')
        if not user_id: return Response('error: user_id is required', status=status.HTTP_400_BAD_REQUEST)
        try: profile = UserProfile.objects.get(user__user_id=user_id)
        except UserProfile.DoesNotExist: return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid(): serializer.save() ;return Response({"message": "Profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #dekete product
    def delete(self, request):
        """Delete a product"""

        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_200_OK)
 

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
        
        if not PetModule.objects.filter(pet_id=pet_id, owner=user_id).exists():
            return Response( {"error": "This pet does not belong to the user."}, status=status.HTTP_400_BAD_REQUEST )
        
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            document = serializer.save()
            return Response({"message": "Product created successfully", "document_id":document.document_id}, status=status.HTTP_201_CREATED,)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #get pet documents
    def get(self, request):
        """List Documents of user"""

        user_id = request.query_params.get('user_id')
        if not user_id: return Response('error: user_id is required', status=status.HTTP_400_BAD_REQUEST)
        documents= Documents.objects.filter(user_id=user_id)
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
        except Documents.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
    

#cart view
class CartView(APIView):

    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        cart_items = CartItem.objects.filter(owner=user_id)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #create cart item
    def post(self, request):
        user_id = request.data.get("owner")
        pet_id = request.data.get("pet")
        if not PetModule.objects.filter(pet_id=pet_id).exists():
            return Response( {"error": "Pet not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not PetModule.objects.filter(pet_id=pet_id, owner=user_id).exists():
            return Response( {"error": "This pet does not belong to the user."}, status=status.HTTP_400_BAD_REQUEST )
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Item added to cart successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #update cart item
    def put(self, request):
        '''update entire user profile'''

        user_id = request.data.get('user_id')
        if not user_id: return Response('error: user_id is required', status=status.HTTP_400_BAD_REQUEST)

        cart_id = request.data.get('cart_id')
        if not cart_id:return Response({'error': 'cart_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:  cart_item = CartItem.objects.get(cart_id=cart_id)
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
        
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        cart_item.delete()
        return Response({'message': 'Cart item deleted successfully'}, status=status.HTTP_200_OK)


#Pets Alert View
class PetAlertView(APIView):
    '''pet alert management'''

    #create pet alert
    def post(self, request):
        user_id = request.data.get("user")
        pet_id = request.data.get("pet")

        if not PetModule.objects.filter(pet_id=pet_id, owner=user_id).exists():
            return Response( {"error": "This pet does not belong to the user."}, status=status.HTTP_400_BAD_REQUEST )
        
        serializer = PetAlertSerializer(data = request.data)
        if serializer.is_valid():
            alert = serializer.save()
            return Response({"message": "Pet alert created successfully", "alert_id": alert.alert_id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #get pets alerts of user
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id :
            return Response("error: user_id is mandatory", status = status.HTTP_400_BAD_REQUEST)
        
        alerts = PetAlerts.objects.filter(user_id = user_id)
        serializer = PetAlertSerializer(alerts, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    #update pet alerts
    def put (self, request):
        user_id = request.data.get('user_id')
        if not user_id: return Response('error: user_id is required', status=status.HTTP_400_BAD_REQUEST)
        alert_id = request.data.get('alert_id')
        if not alert_id:return Response({'error': 'alert_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try: alert = PetAlerts.objects.get(alert_id=alert_id)
        except PetAlerts.DoesNotExist: return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PetAlertSerializer(alert, data=request.data, partial=True) 
        if serializer.is_valid(): serializer.save() ;return Response({'message': 'Pet alert updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #delete pet alert
    def delete(self, request):  
        alert_id = request.query_params.get('alert_id')
        if not alert_id:
            return Response({'error': 'alert_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            alert = PetAlerts.objects.get(alert_id=alert_id)
        except PetAlerts.DoesNotExist:
            return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
        
        alert.delete()
        return Response({'message': 'Pet alert deleted successfully'}, status=status.HTTP_200_OK)
    



    

