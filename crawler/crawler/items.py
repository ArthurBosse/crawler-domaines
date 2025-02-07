import scrapy

class DomainItem(scrapy.Item):
    url_source = scrapy.Field()
    domaine_externe = scrapy.Field()
    status_http = scrapy.Field()
    statut_dns = scrapy.Field()
    date_scan = scrapy.Field()