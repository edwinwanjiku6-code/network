from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import User, Post, Comment, Like, Follow
import json
@login_required
def index(request):
    posts = Post.objects.all().order_by("-created_at")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    comments = Comment.objects.all().order_by("-created_at")
    likes = Like.objects.all().order_by("-created_at")
    users = User.objects.exclude(id=request.user.id)
    for post in page_obj:
        if request.user.is_authenticated:
            post.is_liked = Like.objects.filter(post=post, user=request.user).exists()
            post.author.is_followed = Follow.objects.filter(
    follower=request.user,
    following=post.author).exists()
        else:
            post.is_liked = False
    for user in users:
        if request.user.is_authenticated:
            user.is_followed = Follow.objects.filter(follower=request.user, following=user).exists()
    return render(request, "network/index.html", {
        "posts": page_obj, "comments": comments, "likes": likes, "follow": follow, "users": users, "page_obj": page_obj
    })

  
@login_required 
def post(request):
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            post = Post(author=request.user, content=content)
            post.save()
            return HttpResponseRedirect(reverse("index"))
@login_required
def comment(request, post_id):
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            post = Post.objects.get(pk=post_id)
            comment = Comment(post=post, commenter=request.user, content=content)
            comment.save()
            return JsonResponse({
                "username": comment.commenter.username,
                "content": comment.content,
                "timestamp": comment.created_at.strftime("%b %d, %Y, %I:%M %p")
                })
def post_details(request, post_id):
    post = Post.objects.get(pk=post_id)
    comments = Comment.objects.filter(post=post)
    return render(request, "network/post_detail.html", 
    {"comments": comments, "post": post})

@login_required
def like(request, post_id):
    post = Post.objects.get(pk=post_id)
    like = Like.objects.filter(post=post, user=request.user).first()
    if like:
        like.delete()
        liked = False
    else:
        like = Like(post=post, user=request.user)
        liked = True
        like.save()
    return JsonResponse({"liked": liked,
    "like_count": Like.objects.filter(post=post).count()})
@login_required
def follow(request, user_id):
    user_to_follow = User.objects.get(pk=user_id)
    if user_to_follow == request.user:
        return HttpResponseRedirect(reverse("index"))
    follow = Follow.objects.filter(follower=request.user, following=user_to_follow).first()
    if follow:
        follow.delete()
    else:
        follow = Follow(follower=request.user, following=user_to_follow)
        follow.save()
    return HttpResponseRedirect(reverse("index"))
@login_required
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user != post.author:
        return HttpResponseForbidden("you are not allowed to edit this post")
    else:
        if request.method == "PUT":
            data = json.loads(request.body)
            new_content = data["content"]
            post.content = new_content
            post.save()
@login_required
def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    posts = Post.objects.filter(author=user).order_by("-created_at")
    comments = Comment.objects.filter(commenter=user).order_by("-created_at")
    likes = Like.objects.filter(user=user).order_by("-created_at")
    followers_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    is_followed = Follow.objects.filter(follower=request.user, following=user).exists()
    return render(request, "network/profile.html", {
        "user": user,
        "posts": posts,
        "comments": comments,
        "likes": likes,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_followed": is_followed
    })
def following(request):
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(author__in=following_users).order_by("-created_at")
    commented_post = Comment.objects.filter(post__in=posts, commenter=request.user).order_by("-created_at")
    liked_post = Like.objects.filter(post__in=posts, user=request.user).order_by("-created_at")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html", {
        "comments": commented_post, "likes": liked_post, "page_obj": page_obj
    })
@login_required
def network(request):
    posts = Post.objects.all().order_by("-created_at")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/network.html", {
        "page_obj": page_obj
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
