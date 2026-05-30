from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import CampusAuthenticationForm

app_name = 'core'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('items/', views.home, name='home'),
    path('lost/', views.report_lost, name='report_lost'),
    path('found/', views.report_found, name='report_found'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('item/<int:pk>/claim/', views.claim_item, name='claim_item'),
    path('claim/<int:pk>/respond/', views.respond_claim_request, name='respond_claim_request'),
    path('profile/', views.profile, name='profile'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=CampusAuthenticationForm), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
]
