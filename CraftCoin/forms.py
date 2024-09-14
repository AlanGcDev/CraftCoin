from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import re
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError
from PIL import Image
import io

class UserProfileForm(UserChangeForm):
    password = None  # Excluye el campo de contraseña del formulario
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'profile_picture']

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            try:
                img = Image.open(profile_picture)
                if img.height > 500 or img.width > 500:
                    img.thumbnail((500, 500))
                img_io = io.BytesIO()
                img.save(img_io, format='PNG')
                img_file = img_io.getvalue()
                return img_file
            except Exception as e:
                raise ValidationError(f"Error al procesar la imagen: {str(e)}")
        return profile_picture

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('profile_picture'):
            user.profile_picture = self.cleaned_data['profile_picture']
            user.profile_picture_type = 'image/png'
        if commit:
            user.save()
        return user
    
    
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    terms_and_conditions = forms.BooleanField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'id': 'password1'})
        self.fields['password2'].widget.attrs.update({'id': 'password2'})

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        errors = []
        if len(password1) < 8:
            errors.append("La contraseña debe tener al menos 8 caracteres.")
        if not re.search("[A-Z]", password1):
            errors.append("La contraseña debe contener al menos una mayúscula.")
        if not re.search("[0-9]", password1):
            errors.append("La contraseña debe contener al menos un número.")
        if not re.search("[^A-Za-z0-9]", password1):
            errors.append("La contraseña debe contener al menos un símbolo.")
        if errors:
            raise forms.ValidationError(errors)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def clean_terms_and_conditions(self):
        terms = self.cleaned_data.get("terms_and_conditions")
        if not terms:
            raise forms.ValidationError("Debes aceptar los términos y condiciones.")
        return terms
    
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)

class PasswordResetConfirmForm(forms.Form):
    new_password = forms.CharField(label="Nueva contraseña", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirmar nueva contraseña", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden")
        return cleaned_data