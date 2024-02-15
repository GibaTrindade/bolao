from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(User)
admin.site.register(Time)
admin.site.register(Partida)
admin.site.register(StatusPartida)
admin.site.register(Aposta)
admin.site.register(Campeonato)
admin.site.register(StatusBolao)
admin.site.register(Bolao)
admin.site.register(Ranking)

