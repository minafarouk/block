from django.shortcuts import render
from django_hosts.resolvers import reverse
# Create your views here.


def home(request):
    return render(request, 'landing/index.html')

def faq(request):
    faq_url = reverse('faq', host='landing')
    return render(request, 'landing/faq.html',{'faq_url': faq_url})
