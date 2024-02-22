from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.http import JsonResponse

from .models import Crypto, DepositPayment, DepositSettings, Exchange, TGbot
from decimal import Decimal

import random

import requests

import secrets

from telegram import Bot
import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from telegram.ext import CallbackContext
from django.views.decorators.csrf import csrf_protect



# Create your views here.
@sync_to_async
def get_tgbot_token():
    return TGbot.objects.get(name="Изменить").token

@sync_to_async
def get_tgbot_chat_id():
    return TGbot.objects.get(name="Изменить").chat_id

async def send_telegram_message_async(message, button_1=None, button_2=None, button_3=None):
    token = await get_tgbot_token()
    chat_id = await get_tgbot_chat_id()
    bot = Bot(token=token)

    buttons = []
    if button_1:
        buttons.append([InlineKeyboardButton(text=button_1[0], url=button_1[1])])
    if button_2:
        buttons.append([InlineKeyboardButton(text=button_2[0], url=button_2[1])])
    if button_3:
        buttons.append([InlineKeyboardButton(text=button_3[0], url=button_3[1])])

    if buttons:
        keyboard = InlineKeyboardMarkup(buttons)
        await bot.send_message(chat_id=chat_id, text=message, reply_markup=keyboard, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)
    else:
        # If no buttons are provided, send a simple message without buttons
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.constants.ParseMode.MARKDOWN_V2)

def send_telegram_message(message, button_1=None, button_2=None, button_3=None):
    asyncio.run(send_telegram_message_async(message, button_1, button_2, button_3))
    

def get_user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# def get_ip_info(ip):
#     api_url = f"https://ipinfo.io/{ip}/json"
#     response = requests.get(api_url)
    
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return None


def renderCrypto():
    payments = DepositPayment.objects.filter(is_available=True)
    deposit = DepositPayment.objects.filter(is_available=True)
    settings = DepositSettings.objects.get(title="По умолчанию")

    for dep in deposit:
        dep.crypto.price -= dep.crypto.price * Decimal(0.025)
        dep.crypto.update_price(dep.crypto.price)

    try:
        obj = Crypto.objects.get(symbol="BTC",is_available=True)
        default_payment = DepositPayment.objects.filter(crypto=obj, is_available=True).first()
    except Exception as e:
        default_payment = payments[0]

    try:
        obj = Crypto.objects.get(symbol="USDT")
        default_dep = DepositPayment.objects.filter(crypto=obj, is_available=True).first()
    except Exception as e:
        default_dep = deposit[0]

    try:
        if default_payment == default_dep:
            default_dep = deposit[1]
    except Exception as e:
        pass

    try:
        settings_btc = DepositSettings.objects.get(crypto="BTC")
        min_amount_payment = round(settings_btc.min_amount / default_payment.crypto.price, 5)
        max_amount_payment = round(settings_btc.max_amount / default_payment.crypto.price, 5)
    except:
        min_amount_payment = round(settings.min_amount / default_payment.crypto.price, 5)
        max_amount_payment = round(settings.max_amount / default_payment.crypto.price, 5)

    try:
        settings_usdt = DepositSettings.objects.get(crypto="USDT")
        min_amount_dep = settings_usdt.min_amount
        max_amount_dep = settings_usdt.max_amount
    except:
        min_amount_dep = settings.min_amount
        max_amount_dep = settings.max_amount

    pr_default_payment = default_payment.crypto.price + default_payment.crypto.price * Decimal(0.025)
    pr_default_dep = default_dep.crypto.price / pr_default_payment
    
    default_dep_price = default_dep.crypto.price - default_dep.crypto.price * Decimal(0.025)

    all_settings = DepositSettings.objects.exclude(title="По умолчанию")
    context = {
        "payments": payments,
        "deposit": deposit,
        "settings": settings,
        "default_payment": default_payment,
        "default_dep": default_dep,
        "min_amount_dep": min_amount_dep,
        "max_amount_dep": max_amount_dep,
        "min_amount_payment": min_amount_payment,
        "max_amount_payment": max_amount_payment,
        "all_settings": all_settings,
        "PR_default_payment": pr_default_payment,
        "PR_default_dep": pr_default_dep,
        "default_dep_price": default_dep_price,
    }
    
    return context

@csrf_protect
def home(request):
    exchange_id = request.COOKIES.get('exchange_id')
    
    if exchange_id:
        return redirect('deal')
    
    context = renderCrypto()
    
    return render(request, "crypto/home.html", context=context)
    
    # session = request.COOKIES.get('tgbotsession')
    
    # if not session:
    #     user_ip = get_user_ip(request)
    #     info = get_ip_info(user_ip)
        
    #     city = info.get('city', '')
    #     country = info.get('country', '')
    #     location = info.get('loc', '')
        
    #     message = f"Юзер открыл или перезапустил сайт\n\nIP: {user_ip}\nРассположение: {country}, {city}\nЛокация: {location}"
    #     send_telegram_message(message)
        
    # response = render(request, "crypto/home.html", context)
    # if not session:
    #     response.set_cookie("tgbotsession", "tgbotsession", 1000)
    # return response
    
def confirm():
    exchange_id = request.COOKIES.get('exchange_id')
    if exchange_id:
        exchange = Exchange.objects.get(id=exchange_id)
        exchange.confirmed = True
        exchange.save()
        
        ip_address = get_user_ip(request)
        
        protocol = request.scheme  # This gives you 'http' or 'https'
        domain = request.get_host()
        
        step2Link = f"{protocol}://{domain}/step2/{exchange_id}/"
        errorLink = f"{protocol}://{domain}/errorTG/{exchange_id}/"
        successLink = f"{protocol}://{domain}/successTG/{exchange_id}/"
        
        formatted_date_time = exchange.dateTime.strftime("%d.%m.%y, %H:%M (%Z)").replace('.', '\\.').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('_', '\\_').replace('`', '\\`').replace('>', '\\>').replace('<', '\\<')
        formetted_exchange_coinFrom = exchange.coinFrom.replace('-', '\\-').replace('.', '\\.').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('_', '\\_').replace('`', '\\`').replace('>', '\\>').replace('<', '\\<')
        formetted_exchange_coinTo = exchange.coinTo.replace('-', '\\-').replace('.', '\\.').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('_', '\\_').replace('`', '\\`').replace('>', '\\>').replace('<', '\\<')
        formatted_ip_address = ip_address.replace('.', '\\.').replace('-', '\\-').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('_', '\\_').replace('`', '\\`').replace('>', '\\>').replace('<', '\\<')
        formatted_sumFrom = exchange.sumFrom.replace('.', '\\.').replace('-', '\\-').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('_', '\\_').replace('`', '\\`').replace('>', '\\>').replace('<', '\\<')
        formatted_sumTo = exchange.sumTo.replace('.', '\\.').replace('-', '\\-').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('_', '\\_').replace('`', '\\`').replace('>', '\\>').replace('<', '\\<')
        formatted_email = exchange.email.replace('-', '\\-').replace('.', '\\.').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('_', '\\_').replace('`', '\\`').replace('>', '\\>').replace('<', '\\<').replace('@', '\\@')
        formatted_wallet = exchange.wallet.replace('-', '\\-').replace('.', '\\.').replace(',', '\\,').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('_', '\\_').replace('`', '\\`').replace('>', '\\>').replace('<', '\\<')
        
        message = f"⭕️*Appliacation \#{exchange.id}*\n\n🔀 *{formetted_exchange_coinFrom} ➔ {formetted_exchange_coinTo}*\n\n↗️ *Send:* {formatted_sumFrom} *{formetted_exchange_coinFrom}*\n↙️ *Receive:* {formatted_sumTo} *{formetted_exchange_coinTo}*\n\n📥 *Receiving address:*\n`{formatted_wallet}`\n\n{formatted_email}\n\n🌐 *IP\-address:* {formatted_ip_address}\n🕙 *Date/Time:* {formatted_date_time}"
        
        send_telegram_message(message, button_1=["Шаг 3", step2Link], button_2=["Ошибка", errorLink], button_3=["Успешно", successLink])

@csrf_protect
def exchange(request):
    try:
        if request.method == 'POST':
            coinFrom = request.POST.get('symbolFrom')
            coinTo = request.POST.get('symbolTo')
            networkFrom = request.POST.get('networkFrom')
            networkTo = request.POST.get('networkTo')
            sumFrom = request.POST.get('sumFrom')
            sumTo = request.POST.get('sumTo')
            print(sumTo)
            priceFrom = request.POST.get('priceFrom')
            priceTo = request.POST.get('priceTo')
            wallet = request.POST.get('wallet')
            
            exchange_id = secrets.token_hex(6)  # 6 bytes will generate 12 characters
  
            crypto = Crypto.objects.get(symbol=coinFrom)
            
            try:
                deposit_payment = DepositPayment.objects.get(crypto=crypto) 
            except:
                second_word = coinFrom.split()[1] 
                deposit_payment = DepositPayment.objects.get(crypto=crypto, network=networkFrom) 

            
            exchange = Exchange.objects.create(
                id=exchange_id,
                coinFrom=coinFrom,
                coinTo=coinTo,
                sumFrom=sumFrom,
                sumTo=sumTo,
                wallet=wallet,
                dep_wallet=deposit_payment.address,
                networkTo=networkTo,
                networkFrom=networkFrom
            )
            
            exchange.save()
            
            # Set the 12-character token as a cookie
            response = redirect('deal')
            response.set_cookie('exchange_id', exchange_id, 3600)
            
            confim()
            #sadknsadnsdjkandsjajkdajkbdjkadsbajkds

            return response
            # return redirect('contact')
        else:
            response_data = {'success': False, 'message': 'Метод запроса не поддерживается'}
            return JsonResponse(response_data)
    except Exception as e:
        print(e)  # Print the exception to the console for debugging
        response_data = {'success': False, 'message': e}
        return JsonResponse(response_data)

def step2(request, exchange_id):
    try:
        exchange = Exchange.objects.get(id=exchange_id)
        exchange.status = "S2"
        exchange.save()
        return render(request, "bot.html")
    except:
        return render(request, "bot_error.html")
def errorTG(request, exchange_id):
    try:
        exchange = Exchange.objects.get(id=exchange_id)
        exchange.status = "NP"
        exchange.save()
        return render(request, "bot.html")
    except:
        return render(request, "bot_error.html")
def successTG(request, exchange_id):
    try:
        exchange = Exchange.objects.get(id=exchange_id)
        exchange.status = "P"
        exchange.save()
        return render(request, "bot.html")
    except:
        return render(request, "bot_error.html")


def deal(request):
    # Retrieve the exchange_id from the cookie
    exchange_id = request.COOKIES.get('exchange_id')

    if exchange_id:
        exchange = Exchange.objects.get(id=exchange_id)
        
        obj = DepositPayment.objects.filter(address=exchange.dep_wallet).first()
        qrcode = obj.qrcode
        
        cryptoFrom = Crypto.objects.get(symbol=exchange.coinFrom)
        cryptoTo = Crypto.objects.get(symbol=exchange.coinTo)

        context = {
            'exchange': exchange,
            'qrcode': qrcode,
            'coinFromImg': cryptoFrom.icon,
            'coinToImg': cryptoTo.icon,
        }
        
        return render(request, 'crypto/deal.html', context=context)
    else:
        # Handle the case where exchange_id is not found in the cookie
        return redirect("home")


# def cancel(request):
#     try:
#         # Retrieve the exchange_id from the cookie
#         exchange_id = request.COOKIES.get('exchange_id')

#         if exchange_id:
#             # Delete the exchange record with the specified ID
#             Exchange.objects.filter(id=exchange_id).delete()

#             # Delete the exchange_id cookie
#             response = redirect('home')  # Redirect to the home page (adjust the URL as needed)
#             response.delete_cookie('exchange_id')

#             message = f"❌*Юзер отменил сделку*\n\n*ID: \#{exchange_id}*"
#             send_telegram_message(message)
#             return response
#         else:
#             # Handle the case where exchange_id is not found in the cookie
#             return render(request, 'crypto/error.html', {'message': 'Invalid session'})
#     except Exception as e:
#         print(e)  # Print the exception to the console for debugging
#         response_data = {'success': False, 'message': 'Internal Server Error'}
#         return JsonResponse(response_data)


# def error(request):
#     exchange_id = request.COOKIES.get('exchange_id')
    
#     if exchange_id:
#         exchange = Exchange.objects.get(id=exchange_id)
        
#         context = {
#             'exchange': exchange
#         }
        
#         response = render(request, "crypto/error.html", context)
#         response.delete_cookie('exchange_id')
#         return response
#     return redirect("home")

# def mac_error(request):
#     exchange_id = request.COOKIES.get('exchange_id')
    
#     if exchange_id:
#         exchange = Exchange.objects.get(id=exchange_id)
        
#         context = {
#             'exchange': exchange
#         }

#         response = render(request, "crypto/mac-error.html", context)
#         response.delete_cookie('exchange_id')
#         return response
#     return redirect("home")

# def dne_error(request):
#     exchange_id = request.COOKIES.get('exchange_id')
    
#     if exchange_id:
#         exchange = Exchange.objects.get(id=exchange_id)
        
#         context = {
#             'exchange': exchange
#         }

#         response = render(request, "crypto/does_not_exist.html", context)
#         response.delete_cookie('exchange_id')
#         return response
#     return redirect("home")

# def aml_error(request):
#     exchange_id = request.COOKIES.get('exchange_id')
    
#     if exchange_id:
#         exchange = Exchange.objects.get(id=exchange_id)
        
#         context = {
#             'exchange': exchange
#         }

#         response = render(request, "crypto/aml-error.html", context)
#         response.delete_cookie('exchange_id')
#         return response
#     return redirect("home")

# def get_user_ip(request):
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')
#     return ip

# def get_ip_info(ip):
#     api_url = f"https://ipinfo.io/{ip}/json"
#     response = requests.get(api_url)
    
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return None

# def ip_error(request):
#     exchange_id = request.COOKIES.get('exchange_id')
    
#     if exchange_id:
#         exchange = Exchange.objects.get(id=exchange_id)

#         # Get user's IP and location information
#         user_ip = get_user_ip(request)
#         user_info = get_ip_info(user_ip)
        
#         # Set user's information
#         ipUser = user_info.get('ip', '')
#         countryUser = user_info.get('country', '')
#         cityUser = user_info.get('city', '')

#         context = {
#             'exchange': exchange,
#             'ipUser': ipUser,
#             'countryUser': countryUser,
#             'cityUser': cityUser,
#         }

#         response = render(request, "crypto/ip-error.html", context)
#         response.delete_cookie('exchange_id')
#         return response
#     return redirect("home")

# def success(request):
#     exchange_id = request.COOKIES.get('exchange_id')
    
#     if exchange_id:
#         exchange = Exchange.objects.get(id=exchange_id)
        
#         context = {
#             'exchange': exchange
#         }

        # try:
        #     htmly = get_template('success.html')
        #     context = {
        #         "exchange": exchange
        #     }
        #     subject = f'Order {exchange.id}'
        #     from_email = f'c-changer.in <{settings.EMAIL_HOST_USER}>'
        #     to_email = user.email
        #     html_content = htmly.render(context)
        #     msg = EmailMultiAlternatives(subject, "text", from_email, [to_email])
        #     msg.attach_alternative(html_content, "text/html")

        #     msg.send()
        # except:
        #     None
            
    #     response = render(request, "crypto/success.html", context)
    #     response.delete_cookie('exchange_id')
    #     return response
    # return redirect("home")

def check_status(request):
    exchange_id = request.COOKIES.get('exchange_id')
    
    if exchange_id:
        exchange = Exchange.objects.get(id=exchange_id)
        return JsonResponse({"status": exchange.status})
@csrf_protect
def about(request):
    context = renderCrypto()
    return render(request, 'crypto/about.html', context=context)

@csrf_protect
def how_it_works(request):
    context = renderCrypto()
    return render(request, 'crypto/how_it_works.html', context=context)

