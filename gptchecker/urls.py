from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    path('contactsend/', views.contactsend, name='contactsend'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login'),  # Adjust according to your view function names
    path('admin_login/', views.admin_login_view, name='admin_login'),
    path('register/', views.register, name='register'),
    path('registeradmin/', views.registeradmin, name='registeradmin'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('document/', views.document_view, name='document_view'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('services/place_order/', views.place_order, name='place_order'),
    path('place_order/', views.place_order, name='place_order'),
    path('credit_card_form/', views.place_order, name='credit_card_form'),
]
