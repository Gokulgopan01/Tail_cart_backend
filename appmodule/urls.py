from django.urls import path
from .views import RegisterView, LoginView, UserProfileView, PetView, ProductView, DocumentView, CartView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("user/register/", RegisterView.as_view(), name="simple-register"), 
    path("user/login/", LoginView.as_view(), name="simple-login"), 
    path("user/profile/", UserProfileView.as_view(), name="create-profile"), 
    path("user/pets/", PetView.as_view(), name='manage-pets'),
    path("user/documents/", DocumentView.as_view(), name ="manage-user-documents"),
    path("user/cart/", CartView.as_view(), name="manage-cart-items"),
    
    path("admin/products/", ProductView.as_view(), name="manage-products"),   
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

