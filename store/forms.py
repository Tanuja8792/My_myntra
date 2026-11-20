from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Address, Review, ReturnRequest

class RegisterForm(UserCreationForm):
    email=forms.EmailField(required=True)
    class Meta:
        model=User
        fields=("username","email","password1","password2")
    def save(self,commit=True):
        user=super().save(commit=False); user.email=self.cleaned_data["email"]
        if commit: user.save()
        return user

class AddressForm(forms.ModelForm):
    class Meta:
        model=Address
        fields=("full_name","phone","line1","city","state","pincode")
        widgets={x:forms.TextInput(attrs={"class":"form-control"}) for x in ("full_name","phone","line1","city","state","pincode")}

class ReviewForm(forms.ModelForm):
    class Meta:
        model=Review
        fields=("rating","comment")
        widgets={"rating":forms.Select(choices=[(i,f"{i} stars") for i in range(1,6)],attrs={"class":"form-select"}),"comment":forms.Textarea(attrs={"class":"form-control","rows":3})}

class ReturnForm(forms.ModelForm):
    class Meta:
        model=ReturnRequest
        fields=("kind","reason","replacement_size")
        widgets={"kind":forms.Select(attrs={"class":"form-select"}),"reason":forms.Textarea(attrs={"class":"form-control","rows":3}),"replacement_size":forms.TextInput(attrs={"class":"form-control"})}
