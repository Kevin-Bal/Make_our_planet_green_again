from django.http import HttpResponse
from django.shortcuts import redirect


# Décorateur permettant d'accéder à la view_func seulement si l'utilisateur 
# appartient à un groupe qui est dans la liste 'allowed_groups'
def allowed_users(allowed_groups=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.groups.exists():
                for g in allowed_groups:
                    if request.user.groups.filter(name=g).exists():
                        return view_func(request, *args, **kwargs)
            return HttpResponse("You are not authorized to view this page")
        return wrapper_func
    return decorator
