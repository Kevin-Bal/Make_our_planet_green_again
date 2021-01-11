from django.shortcuts import render


def view_mentions_legales(request):
    return render(request, 'mentionslegales/mentions_legales.html')