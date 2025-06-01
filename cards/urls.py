from django.urls import path, include
from django.contrib.auth import views as auth_views
from cards import views

urlpatterns = [

    path('cards', views.cards, name='cards'),
    path('cards/<int:id>', views.cards_single, name='cards_single'),
    path('cards_create', views.cards_create, name='cards_create'),
    path('cards_gen', views.cards_gen, name='cards_gen'),
    path('search_card', views.search_card, name='search_card'),

    path('cards_print', views.cards_print, name='cards_print'),
    path('cards_print_gen', views.cards_print_gen, name='cards_print_gen'),

    path('bar', views.bar_home, name='bar'),
    path('bar/<int:id>', views.bar_transaction, name='bar_transaction'),

    path('full_screen_message', views.full_screen_message, name='full_screen_message'),

    path('card_info', views.card_info, name='card_info'),

    path('transaction-summary/', views.transaction_summary_view, name='transaction_summary'),

]