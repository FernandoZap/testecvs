from django.shortcuts import render

def home(request):
	usuario = ''
	user_name = request.user.username
	return render (request, 'core/home.html', { 'usuario': user_name })


def sessao(request):
    if not request.session.get('username'):
        request.session['username'] = request.user.username
    return
