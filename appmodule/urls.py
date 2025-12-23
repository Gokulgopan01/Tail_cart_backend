from django.urls import path
from .views import DeleteUserByIdView, RegisterView, LoginView, UserProfileView, PetView, ProductView, DocumentView, CartView, PetAlertView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path("user/register/", RegisterView.as_view(), name="simple-register"), 
    path("user/login/", LoginView.as_view(), name="simple-login"), 
    path("user/profile/", UserProfileView.as_view(), name="create-profile"), 
    path("user/pets/", PetView.as_view(), name='manage-pets'),
    path("user/pet-alerts/", PetAlertView.as_view(), name="manage-pet-alerts"),
    path("user/documents/", DocumentView.as_view(), name ="manage-user-documents"),
    path("user/cart/", CartView.as_view(), name="manage-cart-items"),
    path("admin/user/delete/<int:user_id>/", DeleteUserByIdView.as_view()),

    #Auth and Admin
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("admin/products/", ProductView.as_view(), name="manage-products"), 
    path('admin/products/<int:product_id>/', ProductView.as_view(), name='admin-product-detail'),  
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

