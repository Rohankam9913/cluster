from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("room/",views.rooms,name="rooms"),
    path("room/<int:id>/", views.getRoom,name="room_no"),
    path("create_room/", views.createRoom, name="create_room"),
    path("update_room/<int:roomid>/", views.updateRoom, name="update_room"),
    path("delete_room/<int:roomid>/", views.deleteRoom, name="delete_room"),
    path("login/", views.loginUser, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerUser, name="register"),
    path("delete-message/<int:messageid>", views.deleteMessage, name="delete_message"),
    path("profile/<str:userid>", views.profile, name="user_profile"),
    path("update_profile/<str:userid>", views.update_profile, name="update_user_profile"),
    
    path("browse_topics", views.browseTopics, name="browse_topics"),
    path("recent_activity", views.showActivities, name="recent_activity")
]