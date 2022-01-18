from django.urls import path
from . import views

urlpatterns = [
    path('<str:fb_uid>/<int:ag_uid>/<str:channel>/', views.index, name='index'),
]