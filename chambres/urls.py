from django.urls import path
from . import views

app_name = 'chambres'

urlpatterns = [
    path('chambres/', views.chambre_list, name='chambre_list'),
    path('chambres/<int:pk>/', views.chambre_detail, name='chambre_detail'),
    path('chambres/<int:pk>/update/', views.chambre_update, name='chambre_update'),
    path('chambres/<int:pk>/delete/', views.chambre_delete, name='chambre_delete'),
    path('chambres/<int:pk>/change_status/', views.chambre_status, name='chambre_status'),
    
]