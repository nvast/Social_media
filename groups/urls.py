from django.urls import path
from . import views

urlpatterns = [
    path('groups/', views.groups, name='groups'),
    path('groups/create-group/', views.create_group, name='create_group'),
    path('groups/<str:group_name>/', views.group, name='group'),
    path("delete_group_post/", views.delete_group_post, name="delete_group_post"),
    path("edit_group_post/<str:post_id>/", views.edit_group_post, name="edit_group_post"),
    path("group_post_like/<int:post_id>", views.group_post_like, name="group_post_like"),
    path("groups/<str:group_name>/edit/", views.edit_group, name="edit_group"),
    path("groups/<str:group_name>/followers/", views.group_followers, name="group_followers"),
    path("groups/<str:group_name>/moderators/", views.group_moderators, name="group_moderators"),
    path("groups/<str:group_name>/leave_group/", views.leave_group, name="leave_group"),
    path("groups/<str:group_name>/delete_follower/", views.delete_follower, name="delete_follower"),
    path("groups/<str:group_name>/delete_moderator/", views.delete_moderator, name="delete_moderator"),
    path("groups/<str:group_name>/add_moderator/", views.add_moderator, name="add_moderator"),
    path("groups/<str:group_name>/invite/", views.group_invite, name="group_invite"),
    path('search_groups/', views.search_groups, name='search_groups'),
]