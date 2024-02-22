from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"),
    path("exchange/", exchange, name="exchange"),
    path("order/", deal, name="deal"),
    path("cancel/", cancel, name="cancel"),
    path("error/", error, name="error"),
    
    # path("ip-error/", ip_error, name="ip-error"),
    # path("mac-error/", mac_error, name="mac-error"),
    # path("aml-error/", aml_error, name="aml-error"),
    # path("does-not-exist-error/", dne_error, name="dne-error"),
    path("success/", success, name="success"),
    path("confirm/", confirm, name="confirm"),
    path("check_status/", check_status, name="check_status"),
    path("step2/<str:exchange_id>/", step2),
    path("errorTG/<str:exchange_id>/", errorTG),
    path("successTG/<str:exchange_id>/", successTG),
    path("about/", about, name="about"),
    path("how-it-works/", how_it_works, name="how_it_works"),
]
