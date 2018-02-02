import datetime
import braintree
import random

from mediacoin.models import Transaction, Referral, GiftCode, GiftPrice, GiftRecipient, ReferralTrack

from django.conf import settings

from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail

def index(request):
	return render(request, 'mediacoin/index.html')
def demo(request):
	return render(request, 'mediacoin/demo.html')

# ICO stretch goals view page
def ico(request):
	return render(request, 'mediacoin/pages/ico.html')
def refund(request):
	return render(request, 'mediacoin/pages/refund.html')
def privacy(request):
	return render(request, 'mediacoin/pages/privacy.html')
def cookies(request):
	return render(request, 'mediacoin/pages/cookies.html')
def land(request):
	return render(request, 'mediacoin/land/land_page1.html')
def land2(request):
	return render(request, 'mediacoin/land/landing_page.html')
def land3(request):
	return render(request, 'mediacoin/land/landing_page.html')

# contact
def contact(request):
	return render(request, 'mediacoin/pages/contact.html')

# support
def support(request):
	return render(request, 'mediacoin/pages/support.html')

# platform page
def platform(request):
	return render(request, 'mediacoin/pages/platform.html')

# referral page
def manageref(request):
	return render(request, 'mediacoin/pages/referral.html')

# artist page
def artist(request):
	return render(request, 'mediacoin/pages/artist.html')

# roadmap page
def roadmap(request):
	return render(request, 'mediacoin/pages/roadmap.html')

# team page
def team(request):
	return render(request, 'mediacoin/pages/team.html')

# purchase gift promo code page
def purchaseGiftCard(request):
    gift_prices = GiftPrice.objects.all()

    return render(request, 'mediacoin/purchase-gift.html', {'gift_prices': gift_prices})

# Log with Referral Link Path
def logWithReferralLinkPath(request, referral_link_path):
    return render(request, 'mediacoin/demo.html')


# purchase gift promo code
def purchaseGiftPromoCode(request):
    if request.method == 'POST':
        uuid = request.POST.get('uuid', '')
        gift_type = request.POST.get('gift_type', '')
        gift_price = request.POST.get('gift_price', '')
        payment_nonce = request.POST.get('payment_method_nonce')

        if uuid == '' or gift_type == '' or gift_price == '':
            return JsonResponse({'status': 'failed', 'message': 'Error in ajax call!'})

        result = braintree.Transaction.sale({
            "amount": gift_price,
            "payment_method_nonce": payment_nonce,
            "options": {
                "submit_for_settlement": True
            },
            # "custom_fields": {
            #     "Referral_ID": uuid,
            #     "Amount": gift_price,
            #     "Type": "Buy For Me"
            # }
        })

        if result.is_success:
            referral = Referral.objects.get(referral_id=uuid)

            if gift_type == 'buy-for-me':
                gift_code = GiftCode(referral_id=referral.id, type=True, amount=Decimal(gift_price))
                gift_code.updated_at = datetime.datetime.now()
                gift_code.save()

                return JsonResponse({'status': 'success', 'message': 'Purchased Gift Promo Code successfully!'})
            else: # gift for friend
                gift_code = GiftCode(referral_id=referral.id, type=False, amount=Decimal(gift_price))
                gift_code.updated_at = datetime.datetime.now()
                gift_code.save()

                recipient_email = request.POST.get('recipient_email')
                recipient_name = request.POST.get('recipient_name')
                recipient_message = request.POST.get('recipient_message')
                your_name = request.POST.get('your_name')

                message = 'Hi, ' + recipient_name + '!' + ' Just received Gift Code is purchased over $' + gift_price + ' from ' + your_name + '. ' + 'Gift Promo Code: ' + gift_code.get_code()
                if recipient_email != '':
                    message += ' ***' + your_name + '`s message: ' + recipient_message

                send_mail(
                    'MediaCoin Gift Code from ' + your_name,
                    message,
                    'security@mediacoin.com',
                    [recipient_email],
                    fail_silently=False
                )

                gift_recipient = GiftRecipient(gift_code_id=gift_code.id, email=recipient_email, name=recipient_name)

                return JsonResponse({'status': 'success', 'message': 'Sent Gift Promo Code to ' + recipient_name + ' successfully!'})
        else:
            return JsonResponse({'status': 'failed', 'message': 'Connection error with Braintree System! Please try again!'})


def getClientToken(request):
    if request.method == 'POST':
        return JsonResponse({'client_token': braintree.ClientToken.generate()})

# register Referral ID if not exists
def registerUUID(request):
    if request.method == 'POST':
        uuid = request.POST.get('uuid', '')

        if uuid == '':
            return JsonResponse({'status': 'failed', 'message': 'UUID is empty!'})

        if Referral.objects.filter(referral_id=uuid).exists():
            referral = Referral.objects.get(referral_id=uuid)
            referral.count = referral.count + 1
            referral.updated_at = datetime.datetime.now()
        else:
            token = ''.join(random.choice(settings.AVAILABLE_CHARACTERS_FOR_TOKEN) for i in range(10))
            referral = Referral(referral_id=uuid)
            referral.save()
            token_str = referral.get_id_str() + token
            referral.referral_link_path = token_str[:10]
        referral.save()

        wrp_flag = request.POST.get('wrp_flag')
        if (wrp_flag == 'true'):
            other_wlp = request.POST.get('referral_link_path')
            other_referral = Referral.objects.get(referral_link_path=other_wlp)
            if not ReferralTrack.objects.filter(referral=referral, tracked_referral=other_referral).exists():
                if other_referral.referral_id != referral.referral_id:
                    other_referral.times = other_referral.times + 1
                    other_referral.save()
                    referral_track = ReferralTrack(referral_id=referral.id, tracked_referral_id=other_referral.id)
                    referral_track.save()

        return JsonResponse({'status': 'success', 'referral_link_path': referral.referral_link_path, 'referral_times': referral.times})
