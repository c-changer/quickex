from django.contrib import admin
from .models import Crypto, DepositPayment, DepositSettings, Exchange, TGbot

# Register your models here.
class CryptoAdmin(admin.ModelAdmin):
    actions_on_top = True
    actions_on_bottom = False    
    list_display = ['name', 'symbol', 'price', 'is_available']
    list_editable = ['is_available']
    
admin.site.register(Crypto, CryptoAdmin)

class DepositCryptoAdmin(admin.ModelAdmin):
    # actions_on_top = False
    actions_on_bottom = False    
    list_display = ['crypto', 'address', 'network', 'is_available']
    list_editable = ['address', 'is_available']

admin.site.register(DepositPayment, DepositCryptoAdmin)

class DepositSettingsAdmin(admin.ModelAdmin):
    actions_on_top = False
    actions_on_bottom = False    
    list_display = ['title', 'crypto', 'min_amount', 'max_amount']
    list_editable = ['min_amount', 'max_amount']

admin.site.register(DepositSettings, DepositSettingsAdmin)

class ExchangeAdmin(admin.ModelAdmin):
    actions_on_bottom = False    
    list_display = ['id', 'status', 'sumFrom', 'coinFrom', 'sumTo', 'coinTo', 'wallet', 'date', ]
    list_editable = ["status"]
    ordering = ['-date']
    def has_add_permission(self, request):
        # Disable the ability to add new instances
        return False

admin.site.register(Exchange, ExchangeAdmin)

class TGbotAdmin(admin.ModelAdmin):
    actions_on_bottom = False    
    list_display = ['name', 'token', 'chat_id']
    def has_add_permission(self, request):
        return True
    def has_delete_permission(self, request, obj=None):
        return False
admin.site.register(TGbot, TGbotAdmin)
