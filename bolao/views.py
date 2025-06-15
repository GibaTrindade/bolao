from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages, auth
from django.db.models import OuterRef, Subquery, Prefetch
from collections import defaultdict

def login(request):
    if request.method != 'POST':
        if request.user.is_authenticated:
            return redirect('bolao_list')
        return render(request, 'bolao/login.html')

    usuario = request.POST.get('usuario')
    senha = request.POST.get('senha')

    user = auth.authenticate(username=usuario, password=senha)

    if not user:
        messages.error(request, 'Usuário ou senha inválidos!')
        return render(request, 'bolao/login.html')
    else:
        auth.login(request, user)
        messages.success(request, f'Oi, {user.nome.split(" ")[0].capitalize()}!')
        return redirect('bolao_list')

    return render(request, 'pfc_app/login.html')

def logout(request):
    auth.logout(request)
    return redirect('login')

def listar_apostas(request):
    apostas = Aposta.objects.all().select_related('user', 'partida', 'partida__time1', 'partida__time2')
    return render(request, 'bolao/listar_apostas.html', {'apostas': apostas})

def bolao_list(request):
    boloes = Bolao.objects.all()
    return render(request, 'bolao/bolao_list.html', {'boloes': boloes})

def bolao_detail(request, bolao_id):
    bolao = get_object_or_404(Bolao, pk=bolao_id)
    quantidade_users = bolao.participante.count()
    # Determinar a data de início e fim da semana atual
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # segunda
    end_of_week = start_of_week + timedelta(days=6)  # domingo

    # Obter as apostas do usuário atual para as partidas no campeonato
    apostas_subquery = Aposta.objects.filter(
        user=request.user,
        partida=OuterRef('pk')
    ).values('previsao_goals1', 'previsao_goals2')[:1]

    partidas = Partida.objects.filter(
        campeonato=bolao.campeonato,
        data_partida__gte=start_of_week.strftime('%Y-%m-%d'),
        data_partida__lte=end_of_week.strftime('%Y-%m-%d')).annotate(
                                                previsao_goals1_subquery=Subquery(apostas_subquery.values('previsao_goals1')),
                                                previsao_goals2_subquery=Subquery(apostas_subquery.values('previsao_goals2'))
                                                ).order_by('data_partida')
    partidas_apostadas = Partida.objects.filter(campeonato=bolao.campeonato).exclude(
                                                        status__nome='A INICIAR').prefetch_related(
                                                            Prefetch('aposta_set', queryset=Aposta.objects.select_related('user'))).order_by('data_partida')
    for partida in partidas:
        p1 = partida.previsao_goals1_subquery
        p2 = partida.previsao_goals2_subquery

        if p1 is None or p2 is None:
            partida.previsao_formatada = "- -"
        else:
            partida.previsao_formatada = f"{p1} - {p2}"

    partidas_por_data = defaultdict(list)
    for partida in partidas_apostadas:
        print(partida.data_partida)
        partidas_por_data[partida.data_partida].append(partida)

    rankings = Ranking.objects.filter(campeonato=bolao.campeonato).order_by('-pontuacao')
    contexto = {
        'bolao': bolao,
        'partidas': partidas,
        'quantidade_users': quantidade_users,
        'rankings':rankings,
        'partidas_por_data':dict(partidas_por_data),
    }
    return render(request, 'bolao/bolao_detail.html', contexto)

from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def make_bet(request, bolao_id):
    bolao = get_object_or_404(Bolao, pk=bolao_id)

    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # segunda
    end_of_week = start_of_week + timedelta(days=6)  # domingo

    # Subquery para apostas existentes
    apostas_subquery = Aposta.objects.filter(
        user=request.user,
        partida=OuterRef('pk')
    ).values('previsao_goals1', 'previsao_goals2')[:1]

    partidas = Partida.objects.filter(
        campeonato=bolao.campeonato,
        data_partida__gte=start_of_week,
        data_partida__lte=end_of_week,
        status__nome='A INICIAR'
    ).annotate(
        previsao_goals1_subquery=Subquery(apostas_subquery.values('previsao_goals1')),
        previsao_goals2_subquery=Subquery(apostas_subquery.values('previsao_goals2'))
    ).order_by('data_partida')

    # Se o formulário individual foi submetido
    if request.method == 'POST':
        partida_id = request.POST.get("partida_id")
        goals1 = request.POST.get("goals1")
        goals2 = request.POST.get("goals2")

        if not all([partida_id, goals1, goals2]):
            messages.error(request, "Dados incompletos para a aposta.")
            return redirect("make_bet", bolao_id=bolao_id)

        partida = get_object_or_404(Partida, pk=partida_id)

        aposta, created = Aposta.objects.update_or_create(
            user=request.user,
            partida=partida,
            defaults={
                "previsao_goals1": goals1,
                "previsao_goals2": goals2,
            }
        )

        messages.success(request, f"Aposta salva para {partida.time1.nome} x {partida.time2.nome}.")
        return redirect("make_bet", bolao_id=bolao_id)

    return render(request, 'bolao/make_bet.html', {
        'bolao': bolao,
        'partidas': partidas,
    })
