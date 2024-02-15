from django.urls import path
from .views import *

urlpatterns = [
    path('apostas/', listar_apostas, name='listar_apostas'),
    path('', bolao_list, name='bolao_list'),
    path('bolao/<int:bolao_id>/', bolao_detail, name='bolao_detail'),
    path('bolao/<int:bolao_id>/make_bet/', make_bet, name='make_bet'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
]