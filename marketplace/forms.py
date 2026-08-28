from pathlib import Path
from django import forms
from PIL import Image
from .models import Listing


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "price", "original_price", "category", "condition", "listing_type", "is_price_firm", "pickup_only"]
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}


def validate_images(images):
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if not images:
        raise forms.ValidationError("Add at least one listing photo.")
    if len(images) > 5:
        raise forms.ValidationError("You can upload a maximum of five photos.")
    for image in images:
        if image.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Each image must be 5 MB or smaller.")
        if image.content_type not in allowed:
            raise forms.ValidationError("Photos must be JPG, PNG, or WebP files.")
        if Path(image.name).suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise forms.ValidationError("Photos must be JPG, PNG, or WebP files.")
        try:
            check = Image.open(image)
            check.verify()
            image.seek(0)
        except Exception as error:
            raise forms.ValidationError("One of the uploaded files is not a valid image.") from error


class MessageForm(forms.Form):
    body = forms.CharField(max_length=2000, widget=forms.TextInput(attrs={"placeholder": "Write a message…", "aria-label": "Message"}))
