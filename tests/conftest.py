"""
This configuration script is run automatically by Pytest before every test run.
"""
import os

import django

# Manually designates which settings we will be using in an environment
# variable. This is similar to what occurs in the `manage.py`.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webhooks_example.settings.development')


def pytest_configure():
    """
    Pytest automatically calls this function once when tests are run.
    Additional settings can be added here for example:

    from django.conf import settings
    settings.DEBUG = True
    """
    django.setup()
