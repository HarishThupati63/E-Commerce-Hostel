from django.urls import path
from . import views

urlpatterns = [
    path("", views.verify, name="verify"),
    path("explore/", views.explore, name="explore"),
    path("messages/", views.messages, name="messages"),
    path("sell/", views.create_listing, name="create_listing"),
    path("listing/<int:pk>/", views.listing_detail, name="listing_detail"),
    path("listing/<int:pk>/save/", views.toggle_save, name="toggle_save"),
    path("listing/<int:pk>/chat/", views.start_chat, name="start_chat"),
    path("messages/<int:pk>/", views.thread, name="thread"),
]
