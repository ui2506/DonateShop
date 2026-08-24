from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class FaqSitemap(Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return ['default', 'buy_donate', 'replenish', 'use_donate']

    def location(self, item):
        return reverse('show_faq', kwargs={'name': item})