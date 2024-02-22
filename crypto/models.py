from django.db import models
from django.shortcuts import reverse
import random
# Create your models here.
class Crypto(models.Model):
    icon = models.URLField(max_length=1000, default="", verbose_name="Иконка")
    name = models.CharField(max_length=50, default="", verbose_name="Имя")
    symbol = models.CharField(max_length=10, default="", verbose_name="Индекс")
    price = models.DecimalField(max_digits=20, decimal_places=10, default=0, verbose_name="Цена")
    is_available = models.BooleanField(default=True, verbose_name="Включение/Выключение")
    
    def update_price(self, new_price):
        self.price = new_price
        
    def save(self, *args, **kwargs):
        self.symbol = self.symbol.upper() # Change "symbol" to uppercase before saving 
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.symbol}"
    
    class Meta:
        verbose_name = "Монета"
        verbose_name_plural = "Монеты"

class DepositPayment(models.Model):
    crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE, verbose_name="Монета")
    NETWOR_CHOISES = (
                ('', ''),
                ('TRC-20', 'TRC-20'),
                ('BEP-20', 'BEP-20'),
                ('ERC-20', 'ERC-20'),
                ('C-Chain', 'C-Chain'),
                ('Polygon', 'Polygon'),)
    network = models.CharField(max_length=100, verbose_name="Сеть", null=True, blank=True, default="", choices=NETWOR_CHOISES, help_text="Указывать только на монеты где нужно")
    qrcode = models.ImageField(upload_to="", verbose_name="QR-код")
    address = models.CharField(max_length=1000, verbose_name="Адрес")
    is_available = models.BooleanField(default=True, verbose_name="Включение/Выключение")


    def __str__(self):
        return f"{self.crypto.symbol}"
    
    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"


class DepositSettings(models.Model):
    

    title = models.CharField(max_length=100, editable=False, verbose_name="", default="Изменить")
    @staticmethod
    def generate_crypto_choices():
        # Assume Crypto is a list of predefined cryptocurrencies
        objects = Crypto.objects.all()
        crypto_choices = [(crypto.symbol, crypto.symbol) for crypto in objects] + [('RUB', 'RUB')]
        return crypto_choices
    
    CRYPTO_CHOICES = generate_crypto_choices()

    crypto = models.CharField(
        max_length=20,
        choices=CRYPTO_CHOICES,
        verbose_name="Валюта",
        null=True
    )
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10, verbose_name="min $", blank=True)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=100000, verbose_name="max $", blank=True)
    
    def __str__(self):
        return f"Лимит"
    
    class Meta:
        verbose_name = "Лимит"
        verbose_name_plural = "Лимиты"


class Exchange(models.Model):
    id = models.CharField(max_length=100, unique=True, primary_key=True, verbose_name="ID")
    dep_wallet = models.CharField(max_length=500, null=True, verbose_name="Ваш адрес")
    coinFrom = models.CharField(max_length=100, null=True, verbose_name="")
    coinTo = models.CharField(max_length=100, null=True, verbose_name="")
    networkFrom = models.CharField(max_length=100, null=True, verbose_name="в сеть")
    networkTo = models.CharField(max_length=100, null=True, verbose_name="в сеть")
    sumFrom = models.CharField(max_length=100, null=True, verbose_name="Из")
    sumTo = models.CharField(max_length=100, null=True, verbose_name="В")
    wallet = models.CharField(max_length=500, null=True, verbose_name="Адрес")
    date = models.DateField(auto_now_add=True, verbose_name="Дата", null=True)
    confirmed = models.BooleanField(default=False, verbose_name="Подтверждение")
    
    PAYED = 'P'
    NOT_PAYED = 'NP'
    # IP_ERROR = 'IP'
    # MAC_ERROR = 'MAC'
    # DOES_NOT_EXIST = 'DOES_NOT_EXIST'
    # AML_ERROR = 'AML'
    WAIT = "W"
    STEP2 = "S2"
    
    STATUS_CHOICES = [
            (WAIT, "В ожидании"),
            (PAYED, 'Оплачено'),
            (NOT_PAYED, 'Ошибка'),
            (STEP2, 'Шаг 2')
            # (IP_ERROR, 'Несовпадение IP-адреса'),
            # (MAC_ERROR, 'Несовпадение MAC-адреса'),
            # (DOES_NOT_EXIST, 'Кошелек не существует'),
            # (AML_ERROR, 'Нарушение AML политики'),
            
        ]
    status = models.CharField(max_length=30, verbose_name="Статус", choices=STATUS_CHOICES, default=WAIT)
    
    def __str__(self):
        return f"Обмен - {self.id}"
    
    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"


class TGbot(models.Model):
    name = models.CharField(max_length=100, editable=False, verbose_name="", default="Изменить")
    token = models.CharField(max_length=1000, verbose_name="Токен")
    chat_id = models.CharField(max_length=1000, verbose_name="Чат ID")
    
    class Meta:
        verbose_name = "Бот"
        verbose_name_plural = "Бот"