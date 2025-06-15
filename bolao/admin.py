from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import *

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', 'cpf', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_superuser', 'is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informações pessoais'), {'fields': ('nome', 'cpf', 'email')}),
        (_('Permissões'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Datas'), {'fields': ('last_login', 'date_joined', 'data_criacao', 'data_atualizacao')}),
        (_('Extra'), {'fields': ('role', 'avatar', 'avatar_base64')}),
    )

    readonly_fields = ('data_criacao', 'data_atualizacao', 'last_login', 'date_joined', 'avatar_base64')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'cpf', 'nome', 'password1', 'password2'),
        }),
    )

    search_fields = ('username', 'email', 'cpf')
    ordering = ('username',)



admin.site.register(Time)
admin.site.register(Partida)
admin.site.register(StatusPartida)
admin.site.register(Aposta)
admin.site.register(Campeonato)
admin.site.register(StatusBolao)
admin.site.register(Bolao)
admin.site.register(Ranking)

