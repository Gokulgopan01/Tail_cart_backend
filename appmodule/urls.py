from django.urls import path
from .views import (DeleteUserByIdView, RegisterView, LoginView,ForgotPasswordView,ResetPasswordView, UserProfileView,getqrPetview, PrivatePetView,
                     PetView, ProductView, DocumentView, CartView, PetRemainderView, ResolveAlertView, CreatePetAlertView, PublicPetView, PetDoctorView,
                     CheckoutView, UserOrdersView, AddReviewView)
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    # Auth Login and Registration 
    path("user/login/", LoginView.as_view(), name="simple-login"), 
    path("user/register/", RegisterView.as_view(), name="simple-register"), 
    path("user/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),  
    path("user/reset-password/", ResetPasswordView.as_view(), name="reset-password"), 

    #User profiles and pet management
    path("user/profile/", UserProfileView.as_view(), name="create-profile"), 
    path("user/pets/", PetView.as_view(), name='manage-pets'),
    path("user/pet/<int:pet_id>/", PrivatePetView.as_view(), name="private-pet-view"),

    #public alerts and pet views
    path("alerts/resolve/", ResolveAlertView.as_view(), name="resolve-alert"),
    path("alerts/create/", CreatePetAlertView.as_view(), name="create-pet-alert"),
    path("public/pet/qr/<str:qr_uuid>/", PublicPetView.as_view(), name="public-pet-view"),
    path("product/qr/<int:pet_id>/", getqrPetview.as_view(), name="get-pet-by-qr"),  

    #other user features
    path("user/doctor/", PetDoctorView.as_view(), name="pet-doctor-view"),
    path("user/pet-remainder/", PetRemainderView.as_view(), name="manage-pet-remainder"),
    path("user/documents/", DocumentView.as_view(), name ="manage-user-documents"),

    #products
    path("manager/products/", ProductView.as_view(), name="manage-products"), 
    path('manager/products/<int:id>/', ProductView.as_view(), name='admin-product-detail'),  
    path('add-review/', AddReviewView.as_view(), name='add-review'),

    #cart management
    path("user/cart/", CartView.as_view(), name="manage-cart-items"),
    path("user/checkout/", CheckoutView.as_view()),
    path("user/myorders/", UserOrdersView.as_view(), name="user-my-orders"),

    #Auth and Admin
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("manager/user/delete/<int:user_id>/", DeleteUserByIdView.as_view()),
    
    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

