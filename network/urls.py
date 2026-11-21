
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("comment/<int:post_id>", views.comment, name="comment"),
    path("like/<int:post_id>", views.like, name="like"),
    path("follow/<int:user_id>", views.follow, name="follow"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("following", views.following, name="following"),
    path("network/", views.network, name="network"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post"),
    path("post_detail/<int:post_id>", views.post_details, name="post_detail")
]
