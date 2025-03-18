from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import *

from .models import Comment, Post
from django.http import JsonResponse


# Create your views here.
def index(request):
    # 1. 获取所有去重的分类
    categories = Post.objects.values_list('category', flat=True).distinct()

    # 2. 获取前端查询参数
    selected_category = request.GET.get('category')

    # 3. 根据selected_category进行过滤（或全部）
    if selected_category:
        filtered_posts = Post.objects.filter(category=selected_category).order_by("-id")
    else:
        filtered_posts = Post.objects.all().order_by("-id")

    return render(request, "index.html", {
        'recent_posts': filtered_posts,
        'categories': categories,
        'selected_category': selected_category,
        'top_posts': Post.objects.all().order_by("-likes"),
        'posts': Post.objects.filter(user_id=request.user.id).order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL
    })


def admin_page(request):
    return render(request, 'admin.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already Exists")
                return redirect('signup')
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already Exists")
                return redirect('signup')
            else:
                User.objects.create_user(username=username, email=email, password=password).save()
                return redirect('signin')
        else:
            messages.info(request, "Password should match")
            return redirect('signup')

    return render(request, "signup.html")


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        is_super_user = request.POST.get('is_super_user', 'false') == 'true'

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if is_super_user and not user.is_superuser:
                messages.info(request, 'You do not have admin privileges')
                return redirect("signin")

            auth.login(request, user)

            if is_super_user:
                return redirect("admin_page")
            else:
                return redirect("index")
        else:
            messages.info(request, 'Username or Password is incorrect')
            return redirect("signin")

    return render(request, "signin.html")


def logout(request):
    auth.logout(request)
    return redirect('index')


def blog(request):
    return render(request, "blog.html", {
        'posts': Post.objects.filter(user_id=request.user.id).order_by("id").reverse(),
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL
    })


def create(request):
    if request.method == 'POST':
        # 处理 POST 数据
        postname = request.POST['postname']
        content = request.POST['content']
        category = request.POST['category']
        image = request.FILES.get('image')
        Post.objects.create(
            postname=postname,
            content=content,
            category=category,
            image_path=image,
            user_id=request.user.id
        )
        return redirect('index')
    else:
        # 传给模板的可选分类，用字典
        category_choices = {
            'tech': 'Technology',
            'life': 'Lifestyle',
            'edu': 'Education',
            'other': 'Other',
        }
        return render(request, "create.html", {
            "category_choices": category_choices
        })


def profile(request, id):
    return render(request, 'profile.html', {
        'user': User.objects.get(id=id),
        'posts': Post.objects.all(),
        'media_url': settings.MEDIA_URL,
    })


def profileedit(request, id):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']

        user = User.objects.get(id=id)
        user.first_name = firstname
        user.email = email
        user.last_name = lastname
        user.save()
        return profile(request, id)
    return render(request, "profileedit.html", {
        'user': User.objects.get(id=id),
    })


def increaselikes(request, id):
    if request.method == 'POST':
        post = Post.objects.get(id=id)
        post.likes += 1
        post.save()
    return redirect("index")


def post(request, id):
    post = Post.objects.get(id=id)
    print(post.image_path.url)

    return render(request, "post-details.html", {
        "user": request.user,
        'post': Post.objects.get(id=id),
        'recent_posts': Post.objects.all().order_by("-id"),
        'media_url': settings.MEDIA_URL,
        'comments': Comment.objects.filter(post_id=post.id),
        'total_comments': len(Comment.objects.filter(post_id=post.id))
    })


def savecomment(request, id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        content = request.POST['message']
        Comment(post_id=post.id, user_id=request.user.id, content=content).save()
        return redirect("index")


def deletecomment(request, id):
    comment = Comment.objects.get(id=id)
    postid = comment.post_id
    comment.delete()
    return post(request, postid)


def editpost(request, id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        try:
            postname = request.POST['postname']
            content = request.POST['content']
            category = request.POST['category']

            post.postname = postname
            post.content = content
            post.category = category
            post.save()
        except:
            print("Error")
        return profile(request, request.user.id)

    return render(request, "postedit.html", {
        'post': post
    })


def deletepost(request, id):
    Post.objects.get(id=id).delete()
    return profile(request, request.user.id)


def contact_us(request):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        obj = Contact(name=name, email=email, subject=subject, message=message)
        obj.save()
        context['message'] = f"Dear {name}, Thanks for your time!"

    return render(request, "contact.html")


def all_post(request):
    posts = Post.objects.all().values("id", "postname", "category", "image_path", "content", "time", "likes", "user_id")
    response_data = {
        "media_url": settings.MEDIA_URL,
        "posts": list(posts),
    }
    return JsonResponse(response_data, safe=False)
