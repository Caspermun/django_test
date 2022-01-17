# coding=utf-8
import unicodedata
from django import forms
from django.contrib.auth import password_validation, get_user_model, authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.template.defaultfilters import capfirst
from django.utils.translation import ugettext, ugettext_lazy as _
from .models import Users


class EmailField(forms.EmailField):
    def to_python(self, value):
        return unicodedata.normalize('NFKC', super(EmailField, self).to_python(value))


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = '__all__'
        field_classes = {'email': EmailField}

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update({'autofocus': '', 'placeholder': 'Email'})

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"../password/\">this form</a>."
        ),
    )

    class Meta:
        model = Users
        fields = '__all__'
        field_classes = {'email': EmailField}

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions')
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': '', 'placeholder': 'Email'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), required=True, strip=False)


class RegisterForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}), required=True, strip=False)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'}), required=True,
                                strip=False)


class SetPasswordForm(forms.Form):
    password1 = forms.CharField(max_length=255, strip=False, widget=forms.PasswordInput(
        attrs={'placeholder': 'Пароль'}
    ), label=_("Password"))
    password2 = forms.CharField(max_length=255, strip=False, widget=forms.PasswordInput(
        attrs={'placeholder': 'Повторите пароль'}
    ), label=_("Password confirmation"))


class SetUserInfoForm(forms.Form):
    first_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(
        attrs={
            'placeholder': 'Имя',
            'autofocus': ''
        }
    ))
    last_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(
        attrs={
            'placeholder': 'Фамилия'
        }
    ))


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(max_length=255, strip=False, widget=forms.PasswordInput(
        attrs={'placeholder': 'Старый пароль'}
    ))
    new_password = forms.CharField(max_length=255, strip=False, widget=forms.PasswordInput(
        attrs={'placeholder': 'Новый пароль'}
    ))
    confirm_new_password = forms.CharField(max_length=255, strip=False, widget=forms.PasswordInput(
        attrs={'placeholder': 'Повторите новый пароль'}
    ))
