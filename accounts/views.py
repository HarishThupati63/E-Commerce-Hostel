from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import VerificationForm
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect("explore")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next") or "explore")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("verify")


def verify(request):
    form = VerificationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        college_id = form.cleaned_data["college_id"]
        user, created = User.objects.get_or_create(
            college_id=college_id,
            defaults={"username": college_id.lower(), "is_verified": True},
        )
        if not created:
            user.is_verified = True
            user.save(update_fields=["is_verified"])
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, "Your student status has been verified.")
        return redirect("explore")
    return render(request, "verify.html", {"form": form})
