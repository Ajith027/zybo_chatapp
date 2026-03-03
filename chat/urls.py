from django.urls import path
from . import views

urlpatterns = [
    path('users', views.user_list_view, name='user_list'),
    path('register/', views.register_view, name='register'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/<int:user_id>/', views.chat_view, name='chat'),
    path('send_message', views.send_message, name='send_message'),
    # path('delete-message/<int:message_id>/', views.delete_message_view, name='delete_message'),
]
