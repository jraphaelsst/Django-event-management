from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.contrib.messages import constants

def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not (senha == confirmar_senha):
            messages.add_message(request, constants.ERROR, 'As senhas devem ser iguais.')
            return redirect(reverse('cadastro'))
        
        #TO DO: Validar a força da senha
        
        user = User.objects.filter(username=username)

        if user.exists():
            messages.add_message(request, constants.ERROR, 'Usuário já existe.')
            return redirect(reverse('cadastro'))
        
        user = User.objects.create_user(username=username, email=email, password=senha)
        messages.add_message(request, constants.SUCCESS, 'Usuário salvo com sucesso.')
        user.save()
        return redirect(reverse('login'))


def login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        
        user = auth.authenticate(username=username, password=senha)
        
        if not user:
            messages.add_message(request, constants.ERROR, 'Username ou Senha inválidos.')
            return redirect(reverse('login'))
        
        auth.login(request, user)
        return redirect('/eventos/novo_evento')


def logout(request):
    auth.logout(request)
    messages.add_message(request, constants.INFO, 'Deslogado do sistema com sucesso.')
    return redirect(reverse('login'))