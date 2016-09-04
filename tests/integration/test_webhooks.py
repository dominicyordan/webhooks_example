import hmac
import hashlib
import base64
import json

import pytest
from mock import patch

from django.core.urlresolvers import reverse
from django.conf import settings

pytestmark = pytest.mark.django_db


class TestWebhooks:
    @pytest.fixture
    def json_data(self):
        return {
            'shipping_address': {},
            'customer': {
                'email': 'fake@fake.com'
            }
        }

    def get_shopify_hmac(self, json_data_string):
        key = settings.SHOPIFY_APP_WEBHOOK_SECRET.encode()
        data = json_data_string.encode()
        hm = hmac.new(key, data, hashlib.sha256)
        return base64.b64encode(hm.digest()).decode()

    def test_order_creation_returns_404_for_get_requests(self, client):
        response = client.get(reverse('orders:order_creation'))
        assert response.status_code == 404

    def test_order_creation_returns_401_for_unverified_post_requests(self, client):
        response = client.post(reverse('orders:order_creation'), {})
        assert response.status_code == 401

    def test_order_creations_only_handles_verified_post_requests(self, client, json_data):
        data_string = json.dumps(json_data)
        hmac = self.get_shopify_hmac(data_string)
        response = client.post(
            reverse('orders:order_creation'),
            data_string,
            content_type='application/json',
            HTTP_X_SHOPIFY_HMAC_SHA256=hmac
        )
        assert response.status_code == 200

    @patch('orders.views.send_mail')
    def test_email_is_sent_to_customer_with_non_english_address(self, send_mail, client, json_data):
        json_data['shipping_address']['address1'] = '测试'
        data_string = json.dumps(json_data)
        hmac = self.get_shopify_hmac(data_string)
        client.post(
            reverse('orders:order_creation'),
            data_string,
            content_type='application/json',
            HTTP_X_SHOPIFY_HMAC_SHA256=hmac
        )
        assert send_mail.call_count == 1
