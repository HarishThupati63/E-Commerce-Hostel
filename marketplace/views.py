from functools import wraps
from django.contrib import messages as flash_messages
from django.db import transaction
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ListingForm, MessageForm, validate_images
from .models import Conversation, Listing, ListingImage, Message, SavedListing


def verified_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_verified:
            return redirect("verify")
        return view(request, *args, **kwargs)
    return wrapped


def verify(request):
    return redirect("accounts:verify")


def explore(request):
    category, search = request.GET.get("category", ""), request.GET.get("q", "").strip()
    listings = Listing.objects.filter(status="active").select_related("seller").prefetch_related("images")
    if category in dict(Listing.CATEGORY_CHOICES):
        listings = listings.filter(category=category)
    if search:
        listings = listings.filter(Q(title__icontains=search) | Q(description__icontains=search))
    return render(request, "explore.html", {"listings": listings, "active_category": category, "search": search, "categories": Listing.CATEGORY_CHOICES})


@verified_required
def create_listing(request):
    form = ListingForm(request.POST or None)
    if request.method == "POST":
        images = request.FILES.getlist("images")
        try:
            validate_images(images)
        except Exception as error:
            form.add_error(None, error)
        if form.is_valid():
            with transaction.atomic():
                listing = form.save(commit=False)
                listing.seller = request.user
                listing.save()
                for index, image in enumerate(images):
                    ListingImage.objects.create(listing=listing, image=image, is_primary=index == 0, order=index)
            flash_messages.success(request, "Your listing is live.")
            return redirect("listing_detail", pk=listing.pk)
    return render(request, "marketplace/sell.html", {"form": form})


def listing_detail(request, pk):
    listing = get_object_or_404(Listing.objects.select_related("seller").prefetch_related("images"), pk=pk)
    saved = request.user.is_authenticated and SavedListing.objects.filter(user=request.user, listing=listing).exists()
    return render(request, "listing_detail.html", {"listing": listing, "saved": saved})


@verified_required
def toggle_save(request, pk):
    if request.method != "POST": raise Http404
    listing = get_object_or_404(Listing, pk=pk)
    saved, created = SavedListing.objects.get_or_create(user=request.user, listing=listing)
    if not created: saved.delete()
    return JsonResponse({"saved": created})


@verified_required
def start_chat(request, pk):
    if request.method != "POST": raise Http404
    listing = get_object_or_404(Listing, pk=pk, status="active")
    if listing.seller_id == request.user.id:
        flash_messages.info(request, "This is your listing.")
        return redirect("listing_detail", pk=listing.pk)
    conversation, _ = Conversation.objects.get_or_create(listing=listing, buyer=request.user, seller=listing.seller)
    return redirect("thread", pk=conversation.pk)


@verified_required
def messages(request):
    conversations = Conversation.objects.filter(Q(buyer=request.user) | Q(seller=request.user)).select_related("listing", "buyer", "seller").prefetch_related("messages").order_by("-updated_at")
    return render(request, "messages.html", {"conversations": conversations})


@verified_required
def thread(request, pk):
    conversation = get_object_or_404(Conversation.objects.select_related("listing", "buyer", "seller"), pk=pk)
    if request.user.id not in (conversation.buyer_id, conversation.seller_id): raise Http404
    form = MessageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        Message.objects.create(conversation=conversation, sender=request.user, body=form.cleaned_data["body"])
        conversation.save(update_fields=["updated_at"])
        return redirect("thread", pk=conversation.pk)
    conversation.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
    contact = conversation.seller if conversation.buyer_id == request.user.id else conversation.buyer
    return render(request, "thread.html", {"conversation": conversation, "contact": contact, "form": form})
