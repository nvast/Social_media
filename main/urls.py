from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name="index"),
    path('profile/<str:username>/', views.profile, name="profile"),
    path("post_like/<int:post_id>", views.post_like, name="post_like"),
    path('home/', views.home, name="home"),
    path('profile/<str:username>/follow/', views.follow, name='follow'),
    path('profile/<str:username>/unfollow/', views.unfollow, name='unfollow'),
    path('profile/<str:username>/cancel_follow/', views.cancel_follow, name='cancel_unfollow'),
    path("follows/", views.follows, name="follows"),
    path('profile/<str:username>/edit_profile/', views.edit_profile, name="edit_profile"),
    path('search_users/', views.search_users, name='search_users'),
    path("delete_post/", views.delete_post, name="delete_post"),
    path("edit_post/<int:post_id>/", views.edit_post, name="edit_post"),
    path("delete_comment/", views.delete_comment, name="delete_comment"),
    path("chat/<str:conversation_id>/", views.chat, name="chat"),
    path("chats/<str:username>/", views.chat_choice, name="chat_choice"),
    path("delete_chat/", views.chat_delete, name="chat_delete"),
    path('notification/<str:notification_type>/<int:item_id>/', views.display_notification, name="display_notification"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)