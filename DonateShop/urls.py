from django.contrib import admin
from django.urls import path, include

from api.urls import urlpatterns as api_urls
from main.urls import urlpatterns as main_urls
from donate.urls import urlpatterns as donate_urls
from faq.urls import urlpatterns as faq_urls
from admin.urls import urlpatterns as admin_urls

urlpatterns = [
    path('panel/', admin.site.urls),
    path('auth/', include('social_django.urls', namespace='social')),
    path('', include(main_urls)),
    path('donate/', include(donate_urls)),
    path('api/', include(api_urls)),
    path('faq/', include(faq_urls)),
    path('admin/', include(admin_urls))
]