from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import mcrpc
import hashlib
from .forms import *
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
import json
import base64
import codecs

from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

import qrcode
import qrcode.image.svg
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
import short_url
from creds.models import Files

import os
from django.template import Context
from django.template.loader import get_template

from io import StringIO
from io import BytesIO

from django_hosts.resolvers import reverse

# Create your views here.
def _create_pdf(request, form):
    context = {}
    context['sname'] = form.cleaned_data['student_name']
    context['semail'] = form.cleaned_data['student_email']
    context['smobile'] = form.cleaned_data['mobile']
    context['cname'] = form.cleaned_data['course_name']
    context['grade'] = form.cleaned_data['grade']
    context['dep'] = form.cleaned_data['department']
    html_string = render_to_string('creds/memo.html', context)
    import logging
    logger = logging.getLogger('weasyprint')
    logger.addHandler(logging.FileHandler('/tmp/weasyprint.log'))
    html = HTML(string=html_string, base_url=request.build_absolute_uri())

    certificate_name = form.cleaned_data['student_name'] + "_" + form.cleaned_data['course_name'] + ".pdf"
    html.write_pdf(target='/tmp/{0}'.format(certificate_name), stylesheets=[CSS("/root/django_lab_testing/blockcred/creds/static/css/pdf.css")])
    return '/tmp/{0}'.format(certificate_name)


def _send_email(sname, cname, semail):

    sender = settings.EMAIL_HOST_USER #'cert@poa-certificates.com'
    subject = 'Congratulation ... your new certificate has been issued'
    to = semail
    context = {}
    context['sname'] = sname
    context['cname'] = cname
    html_content = render_to_string('creds/email.html', context)  # render with dynamic value
    text_content = strip_tags(html_content)  # Strip the html tag. So people can see the pure text at least.
    pdf = '/tmp/'+ sname + '_' + cname + '.pdf'

    msg = EmailMultiAlternatives(subject, text_content, sender, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.attach_file(pdf, 'application/pdf')
    msg.send()



def _download_pdf(certificate_name):
    fs = FileSystemStorage('/tmp')
    with fs.open(certificate_name) as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(certificate_name)
        return response


def _file_hash(file_path):
    h = hashlib.sha256()
    with open(file_path, 'rb', buffering=0) as f:
        for b in iter(lambda : f.read(128*1024), b''):
            h.update(b)
    return h.hexdigest()


def _generate_poe(key, form):
    student_info = {}
    student_info['certificate_hash'] = key
    student_info['sname'] = form.cleaned_data['student_name']
    student_info['semail'] = form.cleaned_data['student_email']
    student_info['smobile'] = form.cleaned_data['mobile']
    student_info['cname'] = form.cleaned_data['course_name']
    student_info['grade'] = form.cleaned_data['grade']
    student_info['dep'] = form.cleaned_data['department']

    student_json = json.dumps(student_info)
    student_base64 = base64.b64encode(student_json.encode())
    student_hexa = codecs.encode(student_base64, 'hex')
    client = mcrpc.RpcClient('159.89.226.46', '2778', 'multichainrpc', '5NVcmBy6YYHTj95XFp6ZrELdApxusaKrAtCxKs1K86Gc')
    tx_id = client.publish('POACERT', key, student_hexa)
    return tx_id

def _verify(key):
#    key = 'edc21560ada6e962a08b52b7e836a563306a889c7df9e7a6e4cc37a5e7776a9c'
    client = mcrpc.RpcClient('159.89.226.46', '2778', 'multichainrpc', '5NVcmBy6YYHTj95XFp6ZrELdApxusaKrAtCxKs1K86Gc')
    tx_data = client.liststreamkeyitems('POACERT', key)[0]
    meta_data = tx_data['data']
    student_base64 = codecs.decode(meta_data, 'hex')
    student_json = json.loads(base64.b64decode(student_base64).decode())
    student_json['confirmations'] = tx_data['confirmations']
    if 'blocktime' in tx_data:
        student_json['blocktime'] = tx_data['blocktime']
    return student_json


def _generate_qr_code(data, size=10, border=0):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    factory = qrcode.image.svg.SvgImage
    return qr.make_image(image_factory=factory)


def issue(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            file_path = _create_pdf(request, form)
            file_hashed = _file_hash(file_path)
            tx_id = _generate_poe(file_hashed, form)
            Files.objects.create(file_hashed=file_hashed)
            certificate_info = _verify(file_hashed)
            sname = form.cleaned_data['student_name']
            semail = form.cleaned_data['student_email']
            cname = form.cleaned_data['course_name']
            _send_email(sname, cname, semail)
            return render( request,'creds/certificate.html', context = certificate_info)
        else:
 #           issue_url = reverse('issue-cert', args=form, current_app='creds', host='creds')
            return render(request, 'creds/issue-certificate.html', context = {'form': form})

    else:
        form = StudentForm()
#        issue_url = reverse('issue-cert', args=form, current_app='creds', host='creds')
        return render(request, 'creds/issue-certificate.html', context = {'form': form})


def download_cert(request, cert_name):
    return _download_pdf(cert_name)


def qr_cert(request, cert_name):
    url = "http://127.0.0.1:8000/creds/download-cert/" + cert_name
    qr = _generate_qr_code(url, 20, 2)
    response = HttpResponse(content_type="image/svg+xml")
    qr.save(response, "SVG")
    return response


def mail_cert(request, sname, cname, dep):
   to = request.POST.get('to')
   _send_email(sname, cname, to)
   context = {}
   context['sname'] = sname
   context['cname'] = cname
   context['dep'] = dep
   return render(request, 'creds/certificate.html', context = context)


def url_cert(request, cert_name):

    key = _file_hash('/tmp/' + cert_name)
    id = Files.objects.get(file_hashed=key).id
    short = short_url.encode_url(id)

    return HttpResponse("www.blockreds.io/" + short)


def verify(request):
     if request.method == 'POST':
         try:
            fs = FileSystemStorage()
            file = request.FILES['file']
            filename = fs.save(file.name, file)
            uploaded_file_path = fs.url(filename)
            file_hash = _file_hash(settings.BASE_DIR + uploaded_file_path)
            context = _verify(file_hash)
            return render_to_response('creds/verify-success.html', context=context)
         except:
            return render_to_response('creds/verify-unsuccess.html')

     if request.method == 'GET':
        url = request.GET.get('url')
        if url:
            try:
                id = short_url.decode_url(url[url.find('/') + 1:])
                key = Files.objects.get(id=id).file_hashed
                context = _verify(key)
                return render(request, 'creds/verify-success.html', context=context)
            except:
                return render(request, 'creds/verify-unsuccess.html')
        else:
            return render(request, 'creds/verify-certificate.html')

     else:
        return render(request, 'creds/verify-certificate.html')
