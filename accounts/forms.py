from django import forms
from django.contrib.auth.forms import AuthenticationForm


class VerificationForm(forms.Form):
    college_id = forms.CharField(max_length=100, label="College ID")

    def clean_college_id(self):
        value = self.cleaned_data["college_id"].strip()
        if len(value) < 4:
            raise forms.ValidationError("Enter a valid college ID.")
        return value


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Username or college ID")
