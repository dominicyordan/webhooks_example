import hmac
import hashlib
import base64
import json

from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _


@csrf_exempt
def order_creation(request, *args, **kwargs):
    order = json.loads(request.body.decode())
    header = request.META.get('HTTP_X_SHOPIFY_HMAC_SHA256')

    if not verify_webhook(request.body, header):
        return HttpResponse(status=401)

    if not check_order(order):
        send_customer_email(order)

    return HttpResponse('Verified')


def verify_webhook(data, header):
    """
    Verifies the origin the of the request by checking the signature
    """
    key = settings.SHOPIFY_APP_WEBHOOK_SECRET.encode()
    hm = hmac.new(key, data, hashlib.sha256)
    digest = base64.b64encode(hm.digest()).decode()
    return digest == header


def check_order(order):
    """
    Returns False if there are non-English characters in the address.
    """
    shipping_address = order.get('shipping_address', {})
    address_list = [
        shipping_address.get('address1'),
        shipping_address.get('address2'),
    ]
    address = ' '.join([address for address in address_list if address])

    try:
        address.encode().decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def send_customer_email(order):
    """
    Sends an email to the customer to correct their order address.
    """
    subject = _('Please correct the errors in your order shipping address')
    customer_email = order['customer']['email']
    message = render_to_string('orders/emails/correct_shipping_address.txt')
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [customer_email])
