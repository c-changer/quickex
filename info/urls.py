from django.urls import path
from .views import *

urlpatterns = [
    path('partners/', partners, name="partners"),
    path('wallet/', wallet, name="wallet"),
    path('support/', support, name="support"),
    path('aml/', aml, name="aml"),
    path('blog/', blog, name="blog"),
]
