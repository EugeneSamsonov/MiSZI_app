import re
from users.models import User
from django import forms
from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible


@deconstructible
class PasswordValidator(BaseValidator):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, pswd):
        # 25. Чередование цифр, знаков арифметических операций и снова цифр.
        # 26. Несовпадение с именем пользователя.
        # 27. Несовпадение с именем пользователя, записанным в обратном порядке.
        # 28. Наличие строчных и прописных латинских букв, цифр и символов кириллицы.
        # 29. Наличие строчных и прописных букв, цифр и знаков арифметических операций.
        if not re.search(r"\d", pswd):
            raise forms.ValidationError("Пароль должен содержать хотя бы одну цифру")
        if not re.search(r"[\W_]", pswd):
            raise forms.ValidationError(
                "Пароль должен содержать хотя бы один знак арифметической операции"
            )
        if not re.search(r"[a-zA-Z]", pswd):
            raise forms.ValidationError("Пароль должен содержать хотя бы одну букву латинского алфавита")
        if not re.search(r"[а-яА-Я]", pswd):
            raise forms.ValidationError(
                "Пароль должен содержать хотя бы одну букву кириллицы"
            )
        if not re.search(r"\d+\W+\d+", pswd):
            raise forms.ValidationError(
                "Пароль должен содержать чередование цифр, знаков арифметических операций и снова цифр"
            )


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    username = forms.CharField()
    password1 = forms.CharField(
        widget=forms.PasswordInput, required=False, validators=[PasswordValidator()], label="Пароль"
    )
    password2 = forms.CharField(widget=forms.PasswordInput, required=False, label="Повторите пароль")

    def clean_password1(self):
        usnm = self.cleaned_data.get("username")
        pswd = self.cleaned_data.get("password1")

        if usnm.lower() in pswd.lower():
            raise forms.ValidationError("Error: password contains username")

        if usnm[::-1].lower() in pswd.lower():
            raise forms.ValidationError(
                "Error: password contains reversed username"
            )

        return pswd

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        
        return password2


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(
        widget=forms.PasswordInput, required=False, validators=[PasswordValidator()], label="Пароль"
    )

    def clean_password(self):
        usnm = self.cleaned_data.get("username")
        pswd = self.cleaned_data.get("password")
        
        if usnm.lower() in pswd.lower():
            raise forms.ValidationError("Error: password contains username")
            
        if usnm[::-1].lower() in pswd.lower():
            raise forms.ValidationError(
                "Error: password contains reversed username"
            )

        return pswd


class UserChangePasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("old_password", "new_password1", "new_password2")

    old_password = forms.CharField(
        widget=forms.PasswordInput, required=False, label="Старый пароль"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput, required=False, validators=[PasswordValidator()], label="Новый пароль"
    )
    new_password2 = forms.CharField(
        label="Повторите новый пароль",
        widget=forms.PasswordInput,
        required=False,
        validators=[PasswordValidator()],
    )

    def clean_new_password2(self):
        old_password = self.cleaned_data.get("old_password")
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")

        if old_password == new_password1 == new_password2:
            raise forms.ValidationError("Old password and new password is equal")

        if new_password1 != new_password2:
            raise forms.ValidationError("Passwords don't match.")

