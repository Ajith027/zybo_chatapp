from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from chat.models import User,Message
from .forms import LoginForm, RegisterForm
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.http import JsonResponse
import json



# Create your views here.


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                user.is_online = True
                user.save(update_fields=["is_online"])
                return redirect("user_list")
            else:
                form.add_error(None, "Invalid email or password")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    if request.user.is_authenticated:
        request.user.is_online = False
        request.user.last_seen = timezone.now()
        request.user.save(update_fields=['is_online', 'last_seen'])
    logout(request)
    return redirect('login')

@login_required
def user_list_view(request):
    users = User.objects.filter(is_superuser=False,is_active=True).exclude(id=request.user.id)
    return render(request, "user_list.html", {"users": users})

@login_required
def chat_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return redirect('user_list')

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |Q(sender=other_user, receiver=request.user)
        ).filter(is_deleted=False).order_by('timestamp')

    # Mark received messages as read
    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    return render(request, 'chat.html', {
        'other_user': other_user,
        'messages': messages,
        'current_user': request.user,
    })


@login_required
@csrf_exempt
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        receiver_id = data.get("receiver_id")
        content = data.get("message")

        if receiver_id and content:
            Message.objects.create(
                sender=request.user,
                receiver_id=receiver_id,
                content=content
            )
            return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)