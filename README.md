### Installation:

  git clone https://github.com/dominicyordan/webhooks_example

  cd webhooks_example

  pip install -r requirements.txt

  export SECRET_KEY='example'

  export DJANGO_SETTINGS_MODULE='webhooks_example.settings.development'

  export SHOPIFY_APP_WEBHOOK_SECRET='example'

  ./manage.py runserver


### Shopify webhook setup example:

  Event: Order creation

  URL: https://194fabaa.ngrok.io/orders/order-creation/

  Format: JSON


## Running tests:

  py.test tests
