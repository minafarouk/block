from django.shortcuts import render
from django_hosts.resolvers import reverse
from .forms import *
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.


def home(request):
    return render(request, 'landing/index.html')


def faq(request):
    faq_url = reverse('faq', host='landing')
    return render(request, 'landing/faq.html',{'faq_url': faq_url})


def contact(request):
    form = ContactForm(request.POST)

    if request.method == 'POST' and form.is_valid():
        sender = settings.EMAIL_HOST_USER
        to = settings.EMAIL_HOST_USER
        send_mail(
            form.cleaned_data['contact_name'] + ">>" + form.cleaned_data['contact_email'],  #subject
            form.cleaned_data['content'],       #message
            sender, [to])
        returnedJSON = {}
        returnedJSON['message'] = 'Your message sent successfully'
        return JsonResponse(returnedJSON)

    else:

        return JsonResponse(form.errors.as_json(), safe=False,  status=400)


