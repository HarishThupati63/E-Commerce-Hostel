from io import BytesIO
from tempfile import TemporaryDirectory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from accounts.models import User
from .models import Conversation, Listing, Message, SavedListing


class MarketplaceWorkflowTests(TestCase):
    def setUp(self):
        self.temp_media = TemporaryDirectory()
        self.media_override = override_settings(MEDIA_ROOT=self.temp_media.name)
        self.media_override.enable()
        self.seller = User.objects.create_user(username="seller", college_id="SELL100", is_verified=True)
        self.buyer = User.objects.create_user(username="buyer", college_id="BUY100", is_verified=True)

    def tearDown(self):
        self.media_override.disable()
        self.temp_media.cleanup()

    def test_verification_creates_a_session(self):
        self.assertRedirects(self.client.get(reverse("verify")), reverse("accounts:verify"))
        self.assertEqual(self.client.get(reverse("accounts:verify")).status_code, 200)
        response = self.client.post(reverse("accounts:verify"), {"college_id": "NEW100"})
        self.assertRedirects(response, reverse("explore"))
        self.assertTrue(User.objects.get(college_id="NEW100").is_verified)

    def test_listing_upload_save_and_chat_workflow(self):
        self.client.force_login(self.seller)
        image_data = BytesIO()
        Image.new("RGB", (1, 1), "white").save(image_data, "PNG")
        image = SimpleUploadedFile("book.png", image_data.getvalue(), content_type="image/png")
        response = self.client.post(reverse("create_listing"), {"title": "Physics textbook", "description": "Clean copy", "price": "35.00", "category": "textbooks", "condition": "good", "listing_type": "sell", "images": image})
        self.assertEqual(response.status_code, 302)
        listing = Listing.objects.get(title="Physics textbook")
        self.assertEqual(listing.images.count(), 1)
        self.assertEqual(self.client.get(reverse("listing_detail", args=[listing.pk])).status_code, 200)
        self.client.force_login(self.buyer)
        self.assertEqual(self.client.get(reverse("explore")).status_code, 200)
        self.assertJSONEqual(self.client.post(reverse("toggle_save", args=[listing.pk])).content, {"saved": True})
        self.assertTrue(SavedListing.objects.filter(user=self.buyer, listing=listing).exists())
        response = self.client.post(reverse("start_chat", args=[listing.pk]))
        conversation = Conversation.objects.get(listing=listing, buyer=self.buyer)
        self.assertRedirects(response, reverse("thread", args=[conversation.pk]))
        self.assertEqual(self.client.get(reverse("messages")).status_code, 200)
        self.assertEqual(self.client.get(reverse("thread", args=[conversation.pk])).status_code, 200)
        self.client.post(reverse("thread", args=[conversation.pk]), {"body": "Is this available?"})
        self.assertTrue(Message.objects.filter(conversation=conversation, body="Is this available?").exists())
