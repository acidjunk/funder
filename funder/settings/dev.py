from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

for template_engine in TEMPLATES:
    template_engine['OPTIONS']['debug'] = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*1%%@qo733cpl%ctlcmyg7!gi%qa-yraoie_bj$ij3l%+n9vtl'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DISQUS_API_KEY = 'TFq1eaFJ0wFgcUbj6BoOHCnuzrYu4WUK1M6fswyaOGE22Hhvzf4VdhT5YPHCyIbu'
DISQUS_WEBSITE_SHORTNAME = 'Funder DEMO site'


try:
    from .local import *
except ImportError:
    pass
