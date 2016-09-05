import hmac
import hashlib
import base64
import json

import pytest
from mock import patch

from django.core.urlresolvers import reverse
from django.conf import settings

pytestmark = pytest.mark.django_db


class TestOrderCreation:
    """
    Tests the webhook handler attached to Shopify's order creation event.
    """
    @pytest.fixture
    def data(self):
        """
        Fake Shopify order data.
        """
        return {
            'shipping_address': {},
            'customer': {
                'email': 'fake@fake.com'
            }
        }

    def get_shopify_hmac(self, data_string):
        """
        Hashes the data using the secret webhook signature.
        """
        key = settings.SHOPIFY_APP_WEBHOOK_SECRET.encode()
        hm = hmac.new(key, data_string.encode(), hashlib.sha256)
        return base64.b64encode(hm.digest()).decode()

    def test_returns_404_for_get_requests(self, client):
        """
        The handler must must return a 404 response for GET requests.
        """
        response = client.get(reverse('orders:order_creation'))
        assert response.status_code == 404

    def test_returns_401_for_unverified_post_requests(self, client):
        """
        The handler must return a 401 response for unsigned POST requests.
        """
        response = client.post(reverse('orders:order_creation'), {})
        assert response.status_code == 401

    def test_returns_401_for_wrongly_signed_post_requests(self, client, data):
        """
        The handler must return a 401 response for wrongly signed POST
        requests.
        """
        url = reverse('orders:order_creation')
        data_string = json.dumps(data)
        key = 'Wrong key'.encode()
        hm = hmac.new(key, data_string.encode(), hashlib.sha256)
        bad_hmac = base64.b64encode(hm.digest()).decode()
        headers = {
            'content_type': 'application/json',
            'HTTP_X_SHOPIFY_HMAC_SHA256': bad_hmac,
        }
        response = client.post(url, data_string, **headers)
        assert response.status_code == 401

    def test_must_handle_verified_post_requests(self, client, data):
        """
        The handler must handle correctly signed POST requests.
        """
        url = reverse('orders:order_creation')
        data_string = json.dumps(data)
        hmac = self.get_shopify_hmac(data_string)
        headers = {
            'content_type': 'application/json',
            'HTTP_X_SHOPIFY_HMAC_SHA256': hmac,
        }
        response = client.post(url, data_string, **headers)
        assert response.status_code == 200

    @patch('orders.views.send_mail')
    def test_email_is_sent_to_customer_with_non_english_address(
            self, send_mail, client, data):
        """
        An email must be sent to customers if there are non-English characters
        in their address.
        """
        url = reverse('orders:order_creation')
        data['shipping_address']['address1'] = '测试'
        data_string = json.dumps(data)
        hmac = self.get_shopify_hmac(data_string)
        headers = {
            'content_type': 'application/json',
            'HTTP_X_SHOPIFY_HMAC_SHA256': hmac,
        }
        client.post(url, data_string, **headers)
        assert send_mail.call_count == 1
