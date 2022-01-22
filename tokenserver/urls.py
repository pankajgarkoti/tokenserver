from django.urls import path
from . import views

urlpatterns = [
    # path('<str:utype>/<str:channel>/', views.index, name='index'),
    path('<str:utype>/<str:channel>/<int:uid>/', views.index, name='index'),
]