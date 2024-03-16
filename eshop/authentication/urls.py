from django.urls import path
from .views import Signup, Verify, Register, UserAccount, VendorApply, Home, Login, Logout, VendorPage

# user/
urlpatterns = [
    path('', Signup.as_view(), name='signup'),
    path('verifier/', Verify.as_view(), name='verifyit'),
    path('register/', Register.as_view(), name='registerit'),
    path('account/', UserAccount.as_view(), name='account'),
    path('apply/', VendorApply.as_view(), name='apply'),
    path('vendor/', VendorPage.as_view(), name='vendor'),
    path('home/', Home.as_view(), name='home'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout, name='logout'),    
]
