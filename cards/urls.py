from django.urls import path, include
from django.contrib.auth import views as auth_views
from cards import views

urlpatterns = [

    path('instructions', views.instructions, name='instructions'),
    path('cards', views.cards, name='cards'),
    path('cards/<int:id>', views.cards_single, name='cards_single'),
    path('cards_create', views.cards_create, name='cards_create'),
    path('cards_gen', views.cards_gen, name='cards_gen'),
    path('cards_print', views.cards_print, name='cards_print'),
    path('cards_print_gen', views.cards_print_gen, name='cards_print_gen'),
    path('bar', views.bar, name='bar'),

]