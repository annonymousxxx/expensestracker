from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list/', views.expense_list, name='expense_list'),
    path('create/', views.expense_create, name='expense_create'),
    path('<int:pk>/', views.expense_detail, name='expense_detail'),
    path('<int:pk>/edit/', views.expense_update, name='expense_update'),
    path('<int:pk>/delete/', views.expense_delete, name='expense_delete'),
]
