from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="dashboard", permanent=False), name="home"),    
    path('delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('login/', auth_views.LoginView.as_view(template_name ='expenses/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page = "login"), name='logout'),
    path('register/', views.register, name='register'),
    path('add-category/', views.add_category, name='add_category'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('budgets/', views.manage_budgets, name='manage_budgets'),
    path('add-budget/', views.add_budget, name='add_budget'),
    path('edit-budget/<int:budget_id>/', views.edit_budget, name='edit_budget'),
    path('delete-budget/<int:budget_id>/', views.delete_budget, name='delete_budget'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("categories/", views.categories, name="categories"),
    path("transactions/", views.transactions, name="transactions"),
]

