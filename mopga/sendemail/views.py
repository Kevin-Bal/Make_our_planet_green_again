# sendemail/views.py
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import ContactForm


def contactView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            sujet = form.cleaned_data['sujet']
            contact_email = form.cleaned_data['contact_email']
            message = form.cleaned_data['message']
            try:
                send_mail(sujet, message, contact_email, ['smtp.gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('success')
    return render(request, "sendemail/email.html", {'form': form})

def successView(request):
    return HttpResponse("C'est bon! Merci pour votre message.")