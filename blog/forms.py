from django import forms

from blog.models import Ad


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        exclude = ['user', 'created_at', 'moderated', 'is_active']

# class RegisterForm(forms.Form):
#     email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}), required=True)
#     password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), required=True, strip=False)
#     password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}), required=True,
#                                 strip=False)