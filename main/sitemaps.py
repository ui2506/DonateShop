from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Rule

class MainSitemap(Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        # <str:server_id>
        return Rule.objects.filter(
            game_rules__isnull=False
        ).select_related('server').order_by('id')
     
    def location(self, item):
        # rules/game/<str:server_id>/
        return reverse('server_rules', kwargs={'server_id': item.server.server_id})