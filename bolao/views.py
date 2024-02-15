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

def make_bet(request, bolao_id):
    bolao = get_object_or_404(Bolao, pk=bolao_id)
    # Determinar a data de início e fim da semana atual
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # segunda
    end_of_week = start_of_week + timedelta(days=6)  # domingo

    # Obter as apostas do usuário atual para as partidas no campeonato
    apostas_subquery = Aposta.objects.filter(
        user=request.user,
        partida=OuterRef('pk')
    ).values('previsao_goals1', 'previsao_goals2')[:1]

    partidas = Partida.objects.filter(campeonato=bolao.campeonato,
                                      data_partida__gte=start_of_week.strftime('%Y-%m-%d'),
                                      data_partida__lte=end_of_week.strftime('%Y-%m-%d'),
                                      status__nome='A INICIAR').annotate(
                                                previsao_goals1_subquery=Subquery(apostas_subquery.values('previsao_goals1')),
                                                previsao_goals2_subquery=Subquery(apostas_subquery.values('previsao_goals2'))
                                                ).order_by('data_partida')
    

    if request.method == 'POST':
        for partida in partidas:
            goals1 = request.POST.get(f'goals1_{partida.id}')
            goals2 = request.POST.get(f'goals2_{partida.id}')
            user = request.user
            try:
                aposta, created = Aposta.objects.get_or_create(
                user=user, 
                partida=partida,
                defaults={'previsao_goals1': goals1, 'previsao_goals2': goals2}
                )

                if not created:
                    aposta.previsao_goals1 = goals1
                    aposta.previsao_goals2 = goals2
                    aposta.save()
                    
            except Exception as e:
                messages.error(request, f'{e}')
                return redirect('make_bet',bolao_id=bolao_id)
        messages.success(request, f'Aposta feita!')
        return redirect('bolao_detail', bolao_id=bolao_id)
    contexto ={
        'bolao': bolao, 
        'partidas': partidas,
    }
    return render(request, 'bolao/make_bet.html', contexto)