# sendemail/views.py
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.mail import mail_admins
from django.contrib import messages
from .forms import ContactForm
from plateforme.views import home


def contactView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            sender = form.cleaned_data['email']
            subject = "Vous avez une nouvelle demande par {} sur Mopga".format(sender)
            message = "Sujet: {}\n\nMessage: {}".format(form.cleaned_data['sujet'], form.cleaned_data['message'])
            mail_admins(subject, message)

            form.save()
            messages.add_message(request, messages.INFO, 'Demande soumise.')
            return redirect(home)
    return render(request, "sendemail/email.html", {'form': form})

