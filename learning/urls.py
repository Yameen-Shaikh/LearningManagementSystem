from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subject/<int:subject_id>/', views.level_select, name='level_select'),
    path('subject/<int:subject_id>/level/<int:level>/', views.chapter_list, name='chapter_list'),
    path('chapter/<int:chapter_id>/', views.topic_list, name='topic_list'),
    
]