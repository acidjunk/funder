from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

for template_engine in TEMPLATES:
    template_engine['OPTIONS']['debug'] = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*1%%@qo733cpl%ctlcmyg7!gi%qa-yraoie_bj$ij3l%+n9vtl'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DISQUS_API_KEY = 'h4Cu1Eo53R34Q9QAsBInvU2p62wVi8rKCXVhqaMSNHLUbSQhv3wvueiBUFafwtPq'
DISQUS_WEBSITE_SHORTNAME = 'Funder DEMO site'

INSTALLED_APPS.append('debug_toolbar')
try:
    from .local import *
except ImportError:
    pass
