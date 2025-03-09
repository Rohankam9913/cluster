from django.shortcuts import render, redirect
from .models import Room, Message, Topic, User
from django.db.models import Q
from .forms import RoomForm, UserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from django.http import HttpResponse

# Create your views here.

def loginUser(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username = username)
        except:
            messages.error(request, "User does not exists")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "User Credentials is invalid")
            return redirect("login")
    else:
        page = "login"
        return render(request, "base/auth.html", {"page": page})

def logoutUser(request):
    logout(request)
    return redirect("home")

def registerUser(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        confirm_password = request.POST.get("confirm_password")

        if(password != confirm_password):
            messages.error(request, "Password not matching")
            return redirect("register")

        check_user = User.objects.filter(username = username)
        if len(check_user) == 1:
            messages.error(request, "User already exists")
            return redirect("register")

        user = User.objects.create_user(username = username, password = password, email = email)
        login(request, user)
        return redirect("home")

    return render(request, "base/auth.html")

def home(request):
    all_rooms = Room.objects.all()
    topics = Topic.objects.all()[0:4]

    query = request.GET.get("q")
    if query is not None:
       all_rooms = Room.objects.filter(
            Q(topic__name__contains = query) |
            Q(name__contains = query) |
            Q(host__username__contains = query)
       )
    
    conversations = Message.objects.all().order_by("-created_at")

    if query is not None:
        conversations = Message.objects.filter(Q(room__topic__name__contains = query))

    context = {"rooms": all_rooms, "topics": topics, "roomCount": all_rooms.count(), "conversations": conversations}

    return render(request, "base/home.html", context)

def rooms(request):
    return render(request, "base/room.html")

def getRoom(request, id):
    try:
        room = Room.objects.get(id=id)

        if request.method == "POST":

            if not request.user.is_authenticated:
                return redirect("login")

            comment = request.POST.get("comment")
            message = Message.objects.create(user=request.user, room = room, body = comment)
            message.save()

            room.participants.add(request.user)
            return redirect("room_no", id=room.id)

        chats = Message.objects.filter(room = room).order_by("-created_at")
        participants = room.participants.all()

        context = {"room": room, "chats": chats, "participants": participants}
        return render(request, "base/room.html", context)

    except:
        context = {"msg" : "Room Not Found"}
        return render(request, "base/not-found.html", context)

@login_required(login_url="login")
def createRoom(request):
    form = RoomForm
    topics = Topic.objects.all()
        
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)

        room = Room.objects.create(host = request.user, topic = topic, name = request.POST.get("name"), description = request.POST.get("description"))
        room.participants.add(request.user)
        return redirect("home")

    context = {"form": form, 'topics': topics}
    return render(request, "base/room_form.html", context)

@login_required(login_url="login")
def updateRoom(request, roomid):
    try:
        room = Room.objects.get(id=roomid)
        topics = Topic.objects.all()

        if request.user.username != room.host.username:
            context = {"msg" : "You are not permitted to perform this action"}
            return render(request, "base/not-found.html", context)

        form = RoomForm(instance = room)
        if request.method == "POST":
            topic_name = request.POST.get("topic")
            topic, created = Topic.objects.get_or_create(name=topic_name)

            room.name = request.POST.get("name")
            room.topic = topic
            room.description = request.POST.get("description")
            room.save()
            return redirect("home")        

        context = {"form": form, "topics": topics, "topic": room.topic}
        return render(request, "base/room_form.html", context)
    except:
        context = {"msg": "Room does not exists"}
        return render(request, "base/not-found.html", context)

@login_required(login_url="login")
def deleteRoom(request, roomid):
    try:
        room = Room.objects.get(id=roomid)

        if request.user.username != room.host.username:
            context = {"msg" : "You are not permitted to perform this action"}
            return render(request, "base/not-found.html", context)

        if request.method == "POST":
            room.delete()
            return redirect("home")

        return render(request, "base/delete.html", {"obj": room})
    except:
        context = {"msg": "Room does not exists"}
        return render(request, "base/not-found.html", context)

@login_required(login_url="login")
def deleteMessage(request, messageid):
    try:
        message = Message.objects.get(id=messageid)

        if request.user.username != message.user.username:
            context = {"msg" : "You are not permitted to perform this action"}
            return render(request, "base/not-found.html", context)

        if request.method == "POST":
            message.delete()
            return redirect("room_no", id=message.room.id)

        return render(request, "base/delete.html", {"obj": "this message"})
    except:
        context = {"msg": "Room does not exists"}
        return render(request, "base/not-found.html", context)

@login_required(login_url="login")
def profile(request, userid):
    try:
        user = User.objects.get(id=userid)
        user_rooms = Room.objects.filter(host = user.id)
        topics = Topic.objects.all()
        conversations = Message.objects.filter(user = user.id)

        context = {"user": user, "rooms": user_rooms, "topics": topics, "conversations": conversations}
        return render(request, "base/profile.html", context)
    except:
        context = {"msg" : "The User with this profile does not exists"}
        return render(request, "base/not-found.html", context)

@login_required(login_url="login")
def update_profile(request, userid):

    if str(request.user.id) != userid:
       context = {"msg" : "You are not permitted to perform this action"}
       return render(request, "base/not-found.html", context)
    
    user = User.objects.get(id=userid)

    if request.method == "POST":
        username = request.POST.get("username")
        user.username = username

        bio = request.POST.get("bio")
        user.bio = bio

        user.save()

        return redirect("user_profile", user.id)

    form = UserForm(instance = user)
    context = {"user": user, "form": form}

    return render(request, "base/edit_user.html",context)


## Views for mobile views

def browseTopics(request):
    topics = Topic.objects.all()
    context = {"topics": topics}
    return render(request, "base/topic_mobile.html",context)

def showActivities(request):
    conversations = Message.objects.all()
    context = {"conversations": conversations}
    return render(request, "base/recent_activity_mobile.html", context)
