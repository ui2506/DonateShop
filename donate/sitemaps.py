from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Donate

class ShopSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        # <str:server_id>
        return Donate.objects.values_list(
            'server__server_id', flat=True
        ).distinct().order_by('server__server_id')
     
    def location(self, item):
        # <str:server_id>
        return reverse('shop_donate_list', kwargs={'server_id': item})  