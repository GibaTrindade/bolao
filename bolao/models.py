from django.db import models
from django.contrib.auth.models import AbstractUser
import base64
import os

# Create your models here.

class User(AbstractUser):
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    cpf = models.CharField(max_length=11, blank=False, null=False, unique=True)
    nome = models.CharField(max_length=400, blank=False, null=False)
    email = models.EmailField(default='a@b.com', null=False, blank=False, unique=True)
    
    is_ativo = models.BooleanField(default=True)
    role = models.CharField(max_length=40, default="USER")
    avatar = models.ImageField(null=True, blank=True)
    avatar_base64 = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        self.nome = self.nome.upper()
        self.first_name = self.first_name.upper()
        self.last_name = self.last_name.upper()
        if self.avatar:
            # Leia a imagem em bytes
            image_data = self.avatar.read()
            # Converta a imagem em base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            # Salve a imagem em base64 no campo avatar_base64
            self.avatar_base64 = base64_data

        self.avatar = None
        super(User, self).save(*args, **kwargs)

        if self.avatar:
            os.remove(self.avatar.path)

class Campeonato(models.Model):
    nome = models.CharField(max_length=50, blank=False, null=False)
    def __str__(self):
        return self.nome

class StatusBolao(models.Model):
    nome = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.nome

class Bolao(models.Model):
    nome = models.CharField(max_length=100, blank=False, null=False, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, related_name='boloes',on_delete=models.CASCADE, blank=False, null=False)
    status = models.ForeignKey(StatusBolao,on_delete=models.PROTECT, blank=False, null=False)
    campeonato = models.ForeignKey(Campeonato,on_delete=models.CASCADE, blank=False, null=False)
    participante = models.ManyToManyField(User)
    imagem = models.ImageField(null=True, blank=True)
    imagem_base64 = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if self.imagem:
            # Leia a imagem em bytes
            image_data = self.imagem.read()
            # Converta a imagem em base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            # Salve a imagem em base64 no campo imagem_base64
            self.imagem_base64 = base64_data

        self.imagem = None
        super(Bolao, self).save(*args, **kwargs)

        if self.imagem:
            os.remove(self.imagem.path)


class Time(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    nome =  models.CharField(max_length=50, blank=False, null=False)
    #logo =  models.PositiveSmallIntegerField(max_length=2, blank=True, null=True)

    def __str__(self):
        return self.nome

class StatusPartida(models.Model):
    nome = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.nome

class Partida(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    time1 =  models.ForeignKey(Time, related_name='partidas_casa', on_delete=models.CASCADE, blank=False, null=False)
    time2 =  models.ForeignKey(Time, related_name='partidas_visitante',on_delete=models.CASCADE, blank=False, null=False)
    gols1 = models.PositiveSmallIntegerField(blank=True, null=True)
    gols2 = models.PositiveSmallIntegerField(blank=True, null=True)
    status = models.ForeignKey(StatusPartida,on_delete=models.PROTECT, blank=False, null=False)
    campeonato = models.ForeignKey(Campeonato,on_delete=models.CASCADE, blank=False, null=False)
    data_partida = models.DateField()

    def resultado_formatado(self):
        if self.gols1 is None or self.gols2 is None:
            return "- -"
        return f"{self.gols1} - {self.gols2}"

    def __str__(self):
        return f'{self.time1.nome} x {self.time2.nome}'


class Aposta(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='apostas')
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    previsao_goals1 = models.PositiveSmallIntegerField()
    previsao_goals2 = models.PositiveSmallIntegerField()

    def previsao_formatada(self):
        if self.previsao_goals1 is None or self.previsao_goals2 is None:
            return "- -"
        return f"{self.previsao_goals1} - {self.previsao_goals2}"

    def __str__(self):
        return f'{self.user.nome}: {self.partida.time1.nome} [{self.previsao_goals1}] x {self.partida.time2.nome} [{self.previsao_goals2}]'


class Ranking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    pontuacao = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.user.nome