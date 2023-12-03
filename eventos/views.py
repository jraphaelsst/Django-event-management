from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Evento, Certificado
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages import constants
from django.http import HttpResponse
from django.http import Http404
from secrets import token_urlsafe
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import csv
import os
import sys


@login_required
def novo_evento(request):
    if request.method == "GET":
        return render(request, 'novo_evento.html')
    elif request.method == "POST":
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        data_inicio = request.POST.get('data_inicio')
        data_termino = request.POST.get('data_termino')
        carga_horaria = request.POST.get('carga_horaria')

        cor_principal = request.POST.get('cor_principal')
        cor_secundaria = request.POST.get('cor_secundaria')
        cor_fundo = request.POST.get('cor_fundo')
        
        logo = request.FILES.get('logo')
        
        evento = Evento(
            criado_por=request.user,
            nome=nome,
            descricao=descricao,
            data_inicio=data_inicio,
            data_termino=data_termino,
            carga_horaria=carga_horaria,
            cor_principal=cor_principal,
            cor_secundaria=cor_secundaria,
            cor_fundo=cor_fundo,
            logo=logo,
        )
        
        evento.save()
        
        messages.add_message(request, constants.SUCCESS, 'Evento cadastrado com sucesso!')
        
        return redirect(reverse('novo_evento'))


@login_required
def gerenciar_evento(request):
    if request.method == "GET":
        titulo_filtrado = request.GET.get('titulo_filtrado')
        eventos = Evento.objects.filter(criado_por=request.user)
        # TO DO: realizar outros filtros
        if titulo_filtrado:
            eventos = eventos.filter(nome__contains=titulo_filtrado)
        
        return render(request, 'gerenciar_evento.html', {'eventos': eventos})


@login_required
def inscrever_evento(request, id):
    evento = get_object_or_404(Evento, id=id)
    if request.method == "GET":
        return render(request, 'inscrever_evento.html', {'evento':evento})
    elif request.method == "POST":
        # Validar se o usuário já é participante
        evento.participantes.add(request.user)
        evento.save()
        
        messages.add_message(request, constants.SUCCESS, 'Inscrição realizada com sucesso!')
        return redirect(reverse('inscrever_evento', kwargs={'id': id}))


@login_required
def participantes_evento(request, id):
    evento = get_object_or_404(Evento, id=id)
    if not evento.criado_por == request.user:
        raise Http404('Esse evento não é seu.')
    
    if request.method == 'GET':
        participantes = evento.participantes.all()[:5]
        return render(request, 'participantes_evento.html', {'evento': evento, 'participantes': participantes})


@login_required
def gerar_csv(request, id):
    evento = get_object_or_404(Evento, id=id)
    if not evento.criado_por == request.user:
        raise Http404('Esse evento não é seu.')
    participantes = evento.participantes.all()
    
    token = f'{token_urlsafe(6)}.csv'
    path = os.path.join(settings.MEDIA_ROOT, token)
    
    with open(path, 'w') as file:
        writer = csv.writer(file, delimiter=',')
        for participante in participantes:
            X = (participante.username, participante.email)
            writer.writerow(X)
        
        
    return redirect(f'/media/{token}')


@login_required
def certificados_evento(request, id):
    evento = get_object_or_404(Evento, id=id)
    if not evento.criado_por == request.user:
        raise Http404('Esse evento não é seu.')
    
    if request.method == "GET":
        qtd_certificados = evento.participantes.all().count() - Certificado.objects.filter(evento=evento).count()
        return render(request, 'certificados_evento.html', {'evento':evento, 'qtd_certificados':qtd_certificados})


@login_required
def gerar_certificados(request, id):
    evento = get_object_or_404(Evento, id=id)
    if not evento.criado_por == request.user:
        raise Http404('Esse evento não é seu')

    path_template = os.path.join(settings.BASE_DIR, 'templates/static/eventos/img/template_certificado.png')
    path_fonte = os.path.join(settings.BASE_DIR, 'templates/static/fontes/arimo.ttf')
    
    for participante in evento.participantes.all():
        # TO DO: Validar se já existe certificado desse participante para esse evento
        img = Image.open(path_template)        
        draw = ImageDraw.Draw(img)
        fonte_nome = ImageFont.truetype(path_fonte, 60)
        fonte_info = ImageFont.truetype(path_fonte, 30)
        draw.text((230, 651), f"{participante.username}", font=fonte_nome, fill=(0, 0, 0))
        draw.text((761, 782), f"{evento.nome}", font=fonte_info, fill=(0, 0, 0))
        draw.text((816, 849), f"{evento.carga_horaria} horas", font=fonte_info, fill=(0, 0, 0))
        output = BytesIO()
        img.save(output, format="PNG", quality=100)
        output.seek(0)
        img_final = InMemoryUploadedFile(output,
                                        'ImageField',
                                        f'{token_urlsafe(8)}.png',
                                        'image/jpeg',
                                        sys.getsizeof(output),
                                        None)
        certificado_gerado = Certificado(
            certificado=img_final,
            participante=participante,
            evento=evento,
        )
        certificado_gerado.save()
    
    messages.add_message(request, constants.SUCCESS, 'Certificados gerados')
    return redirect(reverse('certificados_evento', kwargs={'id': evento.id}))


@login_required
def procurar_certificado(request, id):
    evento = get_object_or_404(Evento, id=id)
    if not evento.criado_por == request.user:
        raise Http404('Esse evento não é seu.')
    
    email = request.POST.get('email')
    certificado = Certificado.objects.filter(evento=evento).filter(participante__email=email).first()
    
    if not certificado:
        messages.add_message(request, constants.ERROR, 'Esse certificado ainda não foi gerado.')
        return redirect(reverse('certificados_evento', kwargs={'id':evento.id}))
    
    return redirect(certificado.certificado.url) # Todos os campos do banco de dados possuem atributos,
                                                 # Um deles é a URL
                                                 # Neste caso estamos acessando o Certificado filtrado acima
                                                 # no campo certificado, e trazendo sua URL para acessar a img
                                                    
