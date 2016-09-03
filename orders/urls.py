from django.conf.urls import url

from orders import views

urlpatterns = [
    url(r'^order-creation/$', views.order_creation, name='order_creation'),
]
