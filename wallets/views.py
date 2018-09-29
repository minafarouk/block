from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import mcrpc

from creds.views import _verify
import short_url
from creds.models import Files

# Create your views here.


def _connect():
    client = mcrpc.RpcClient(settings.MULTICHAIN_IP, settings.MULTICHAIN_PORT, settings.MULTICHAIN_RPCUSER,
                             settings.MULTICHAIN_RPCPASSWORD)
    return client


def _authenticated(address):
    client = _connect()
    addresses = client.getaddresses()
    return address in addresses


def _import_address(address):
    client = _connect()
    client.importaddress(address, rescan='true')
    client.grant(address, 'send,receive')
    client.issuemore(address, 'xbc', 500)


def wallet_landing(request):
    if request.COOKIES.get('address'):
        return redirect('wallet-dashboard')
    else:
        return render(request, 'wallets/wallet-landing.html')


def create(request):
    return render(request, 'wallets/create-wallet.html')


def login(request):
    address = request.COOKIES.get('address')
    if address is not None:
        request.session['address'] = address
        if _authenticated(address):
            return redirect('wallet-dashboard')
        else:
            _import_address(address)
            return redirect('wallet-dashboard')
    else:
        return render(request, 'wallets/wallet-login.html')


"""def import_address(request):
    if request.method == 'POST':
        address = request.COOKIES.get('address')
        client = _connect()
        client.importaddress(address, rescan='true')
        client.grant(address, 'send,receive')
        client.issuemore(address, 'xbc', 500)
        return redirect('login')
    else:
        return render(request, 'wallets/import-address.html')
"""


def wallet(request):
    if request.COOKIES.get('address'):
        address = request.session['address']
        client = _connect()
        credit = client.getaddressbalances(address, 0)
        xbc = next((x for x in credit if x['name'] == 'xbc'), {'qty': 0})
        creds = next((x for x in credit if x['name'] == 'creds'), {'qty': 0})

        txids = client.listaddresstransactions(address)
        xbc_txids = [x for x in txids[3:] if 'balance' in x.keys() and x['balance']['assets'] and x['balance']['assets'][0]['name'] == 'xbc']
        creds_txids = [x for x in txids[3:] if 'balance' in x.keys() and x['balance']['assets'] and x['balance']['assets'][0]['name'] == 'creds']
        context = dict()
        context['address'] = address
        context['credit'] = int(xbc['qty'])
        context['creds'] = int(creds['qty'])
        context['txids'] = xbc_txids
        context['creds_txids'] = creds_txids
        return render(request, 'wallets/wallet-dashboard.html', context=context)
    else:
        return redirect('login')


def transfer_asset(request):
    sender_address = request.session['address']
    if request.method == 'POST':
        receiver_address = request.POST.get('receiver_address')
        amount = request.POST.get('amount')
        privKey = request.POST.get('privkey')
        client = _connect()
        unsigned_tx = client.createrawsendfrom(sender_address, {receiver_address: {'xbc': int(amount)}})
        signed_tx = client.signrawtransaction(unsigned_tx, [], [privKey])
        txid = client.sendrawtransaction(signed_tx['hex'])
    return redirect('wallet-dashboard')


def cred_to_verify(request, cred_txid):
    try:
        client = _connect()
        file_hash = client.getrawtransaction(cred_txid, 1)['data'][0]
        context = _verify(file_hash)

        file_id = Files.objects.get(file_hashed=file_hash).id
        context['url'] = short_url.encode_url(file_id)

        return render(request, 'creds/verify-success.html', context=context)
    except:
        return redirect('wallet-dashboard')
