from django import forms
from .models import User

class RegisterForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email 
    
    def save(self):
        user = User(email=self.cleaned_data["email"],
                username=self.cleaned_data["username"],)
        user.set_password(self.cleaned_data["password"])
        user.save()
        return user
    
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)