from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Partida, Aposta, Ranking

@receiver(post_save, sender=Partida)
def atualizar_pontuacao(sender, instance, **kwargs):
    if instance.status.nome == 'FINALIZADA':
        # Aqui você define a lógica para atualizar as pontuações
        apostas = Aposta.objects.filter(partida=instance)
        for aposta in apostas:
            # Lógica para calcular a pontuação baseada na aposta vs resultado real
            pontuacao = calcular_pontuacao(aposta, instance)
            
            # Atualizar ou criar pontuação no Ranking
            ranking, created = Ranking.objects.get_or_create(user=aposta.user, campeonato=instance.campeonato)
            if not created:
                ranking.pontuacao = (ranking.pontuacao or 0) + pontuacao
            else:
                ranking.pontuacao = pontuacao
            ranking.save()

def calcular_pontuacao(aposta, partida):
    # Implemente sua lógica de cálculo de pontuação aqui
    # Exemplo simples:
    pontuacao = 0
    if aposta.previsao_goals1 == partida.gols1 and aposta.previsao_goals2 == partida.gols2:
        pontuacao = 3  # Pontuação por acertar o placar exato
    elif (aposta.previsao_goals1 > aposta.previsao_goals2 and partida.gols1 > partida.gols2) or \
         (aposta.previsao_goals1 < aposta.previsao_goals2 and partida.gols1 < partida.gols2):
        pontuacao = 1  # Pontuação por acertar o vencedor
    elif (aposta.previsao_goals1 == aposta.previsao_goals2 and partida.gols1 == partida.gols2):
        pontuacao = 1
    return pontuacao
