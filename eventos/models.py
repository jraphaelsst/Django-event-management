from django.db import models
from django.contrib.auth.models import User

class Evento(models.Model):
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    data_inicio = models.DateField()
    data_termino = models.DateField()
    carga_horaria = models.IntegerField()
    logo = models.ImageField(upload_to='logos') # FileField para arquivos em geral
    participantes = models.ManyToManyField(User, related_name="evento_participante", blank=True)
    
    # Paleta de cores
    cor_principal = models.CharField(max_length=7)
    cor_secundaria = models.CharField(max_length=7)
    cor_fundo = models.CharField(max_length=7)
    
    def __str__(self) -> str:
        return self.nome
    
class Certificado(models.Model):
    certificado = models.ImageField(upload_to='certificados')
    participante = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    evento = models.ForeignKey(Evento, on_delete=models.DO_NOTHING)