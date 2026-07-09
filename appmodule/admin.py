from django.contrib import admin
from .models import *

admin.site.register(LoginModule)
admin.site.register(PasswordResetOTP)
admin.site.register(PetModule)
admin.site.register(PetAlert)
admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(Documents)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PetRemainders)
admin.site.register(ProductReview)