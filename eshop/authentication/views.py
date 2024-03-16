from django.views.generic import View
from django.shortcuts import render, redirect, HttpResponse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
import random
from eshop.settings import EMAIL_HOST_USER
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import VendorApplyForm
from django.utils import timezone
from datetime import timedelta
# Create your views here.

User = get_user_model()  # Get the active user model


class Signup(View):
    def get(self, request):
        return render(request, 'user/signup.html')

    def post(self, request):
        email = request.POST['email']
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        
        if User.objects.filter(email=email).exists():
            return HttpResponse('Email already exists')
        if User.objects.filter(username=username).exists():
            return HttpResponse('Username already exists')

        user = User.objects.create_user(email=email, username=username, first_name=first_name, last_name=last_name)

        generate_verification = random.randint(100000, 999999)
        user.otp = generate_verification
        user.otp_created_at = timezone.now()  # Store the timestamp when OTP was generated
        user.save()

        subject = "OTP Verification"
        body = f"Your verification code is: {generate_verification}"
        from_email = EMAIL_HOST_USER
        to_email = email
        send_now = send_mail(subject, body, from_email, [to_email])
        
        if send_now:
            messages.success(request, 'Successfully sent OTP. Verify your email here.')
            return redirect('verifyit')

        return render(request, 'user/signup.html')
    
    
class Verify(View):
    def get(self, request):
        return render(request, 'user/verify.html')

    def post(self, request):
        entered_otp = request.POST['otp']
        try:
            user = User.objects.get(otp=entered_otp, is_emailverified=False)
            if user.otp_created_at >= timezone.now() - timedelta(minutes=5):
                user.is_emailverified = True
                user.save()
                login(request, user)
                messages.success(request, 'Success, You are logged in. Create your account here.')
                return redirect('registerit')
            else:
                # If user is not found or OTP is invalid, delete the user 
                user.delete()
                messages.error(request, 'Verification failed, signup again.')
                return redirect('signup')
            
        except User.DoesNotExist:
            messages.error(request, 'User not found, signup.')
            return redirect('signup')


class Register(View):

    def get(self, request):
        
        return render(request, 'user/page-register.html')

    def post(self, request):
        # Ensure the user is logged in
        if not request.user.is_authenticated:
            # return HttpResponse('user_not_authenticated')
            messages.error(request, 'user_not_authenticated')

        # Retrieve the logged-in user
        user = request.user

        # Retrieve the username entered in the form
        entered_username = request.POST.get('username')
        entered_email = request.POST.get('email')

        if entered_email != request.user.email:
            return HttpResponse('email_mismatch')
            # messages.error(request, 'email mismatch')

        if entered_username != request.user.username:
            return HttpResponse('username_mismatch')
            # messages.error(request, 'username mismatch')


         # Update user password provided in the form
        password = request.POST['password']
        confirm_password = request.POST['password']
        if password and confirm_password:
            if password == confirm_password:
                user.set_password(password)
                # Save the user instance without affecting other data
                user.save(update_fields=['password'])
                # return HttpResponse('Password updated successfully')
                messages.success(request, 'Password updated successfully')
                
            else:
                messages.error(request, 'Passwords do not match')
        else:
            messages.warning(request, 'No password provided')


        # Check if the user selected the vendor option
        is_vendor = request.POST.get('payment_option') == 'is_vendor'
        if is_vendor:
            user.is_vendor = False
            user.vendor_application_status = 'pending'
            user.save()

            login(request, user)
           
            return redirect('apply') 

        # Redirect to the dashboard page
        messages.success(request, 'Welcome to your Dashboard!')
        return redirect('account')    







class UserAccount(View):
    def get(self, request):
        return render(request, 'dash/page-account.html')


    def post(self, request):
        pass    
        





class VendorApply(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, 'User not authenticated')
            return redirect('login')
        
        form = VendorApplyForm()  # Create an empty form instance
        return render(request, 'dash/vendor-apply.html', {'form': form})

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, 'User not authenticated')
            return redirect('login')

        # Retrieve the logged-in user
        user = request.user

        # Initialize the form with the POST data
        form = VendorApplyForm(request.POST)

        if form.is_valid():
            # Update the user's fields with the form data
            user.business_name = form.cleaned_data['business_name']
            user.location = form.cleaned_data['location']
            user.registration_no = form.cleaned_data['registration_no']
            user.registering_body = form.cleaned_data['registering_body']
            user.business_description = form.cleaned_data['business_description']
            user.website_url = form.cleaned_data['website_url']

            # Update user's vendor status
            is_vendor = form.cleaned_data.get('is_vendor')
            if is_vendor:
                user.is_vendor = False
                user.vendor_application_status = 'pending'

            # Save the user instance
            user.save()

            return redirect('account')
        else:
            messages.error(request, 'Please fill all required fields')
            return render(request, 'dash/vendor-apply.html', {'form': form})





class VendorPage(View):
    def get(self, request):
        return render(request, 'dash/vendor-dashboard.html')
    

    def post(self, request):
        pass





class Home(View):
    def get(self, request):
        return render(request, 'index.html')
    




class Login(View):
    def get(self, request):
        return render(request, 'user/page-login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Retrieve the user by email
            user = User.objects.get(email=email)

            # Check if the user is a superuser
            if user.is_superuser and user.check_password(password):
                # Log in the superuser if password match
                login(request, user)
                messages.success(request, 'Welcome back')
                return redirect('account')
            if not password:
                messages.error(request, 'Invalid input')
                return redirect('login')

            else:
                # For regular users, check email verification
                user = User.objects.filter(is_emailverified=True).first()

                if password and email:
                    user = authenticate(request, email=email, password=password)
                    if user:
                        login(request, user)
                        messages.success(request, 'Welcome back!')
                        if user.is_vendor:
                            messages.success(request, 'Welcome back, Vendor!')
                            return redirect('vendor')
                        else:
                            return redirect('account')
                    else:
                        messages.error(request, 'Invalid input')
                        return redirect('login')    

        except User.DoesNotExist:
            messages.success(request, 'Sign up to get started')
            return redirect('signup')





def Logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')




