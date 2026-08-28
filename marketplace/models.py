from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models


class Listing(models.Model):
    CATEGORY_CHOICES = [("textbooks", "Textbooks"), ("electronics", "Electronics"), ("furniture", "Furniture"), ("clothing", "Clothing"), ("other", "Other")]
    CONDITION_CHOICES = [("new", "New"), ("like_new", "Like New"), ("good", "Good"), ("fair", "Fair")]
    LISTING_TYPE_CHOICES = [("sell", "Sell"), ("rent", "Rent")]
    STATUS_CHOICES = [("active", "Active"), ("sold", "Sold"), ("reserved", "Reserved")]
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    original_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES, default="sell")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    is_price_firm = models.BooleanField(default=False)
    pickup_only = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="listings/%Y/%m/", validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])])
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]


class SavedListing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_listings")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "listing"], name="unique_saved_listing")]


class Conversation(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="conversations")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="purchases")
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sales_chats")
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["listing", "buyer", "seller"], name="unique_listing_conversation")]


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    class Meta:
        ordering = ["created_at"]
