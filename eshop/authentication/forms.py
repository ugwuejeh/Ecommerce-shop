from django import forms
from .models import Registration

class VendorApplyForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ['business_name', 'registration_no', 'registering_body', 'location', 'business_description', 'website_url']