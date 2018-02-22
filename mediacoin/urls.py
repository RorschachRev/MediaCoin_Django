"""mediacoin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static

from mediacoin import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #url(r'^blog/', import('blog.urls')),

    # main page
    url(r'^$', views.index, name='index'),
    # referral user page
    url(r'^u/(?P<referral_link_path>).*/$', views.logWithReferralLinkPath, name='u-referral-link-path'),
    url(r'^referral/$', views.manageref, name='referral'),

    # demo page
    url(r'^demo.html$', views.demo, name='demo'),
    #static pages
    url(r'^artist.html$', views.artist, name='artist'),
    url(r'^platform.html$', views.platform, name='platform'),
    url(r'^roadmap.html$', views.roadmap, name='roadmap'),
    url(r'^team.html$', views.team, name='team'),
    url(r'^token.html$', views.token, name='token'),
    url(r'^privacy.html$', views.privacy, name='privacy'),
    url(r'^refund.html$', views.refund, name='refund'),
    url(r'^cookies.html$', views.cookies, name='cookies'),
    url(r'^support.html$', views.support, name='support'),
    url(r'^contact.html$', views.contact, name='contact'),
    url(r'^refund.html$', views.refund, name='refund'),
    url(r'^privacy.html$', views.privacy, name='privacy'),
    url(r'^Musician_Services.html$', views.Musician_Services, name='Musician_Services'),

    #url(r'^net_neutrality.html$', views.netneutral, name='netneutral'),

    url(r'^land.html$', views.land , name='land'),
    url(r'^land_general.html$', views.land2 , name='land2'),
    url(r'^lblockchain1/$', views.land3, name='land3'),

    # purchase gift promo code page
    url(r'^purchase-gift-card/$', views.purchaseGiftCard, name='purchase-gift-card'),

    # check uuid in db and if not stored in db, add new one - works for both of logged in user and not user
    url(r'^register-uuid$', views.registerUUID, name='register-uuid'),
    # gift purchase functions
    url(r'^purchase-gift-card/purchase-gift$', views.purchaseGiftPromoCode, name='purchase-gift'),
    url(r'^purchase-gift-card/get-braintree-token$', views.getClientToken, name='get-braintree-token')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
