# crawler/spiders/domain_spider.py

import scrapy
from urllib.parse import urlparse
import dns.resolver
from datetime import datetime

class DomainSpider(scrapy.Spider):
    name = 'domain_crawler'
    
    def __init__(self, start_url=None, *args, **kwargs):
        super(DomainSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else []
        self.visited_urls = set()
        
    def parse(self, response):
        current_domain = urlparse(response.url).netloc
        
        # Extraire tous les liens
        for href in response.css('a::attr(href)').getall():
            try:
                url = response.urljoin(href)
                parsed_url = urlparse(url)
                external_domain = parsed_url.netloc
                
                # Vérifier si c'est un domaine externe
                if external_domain and external_domain != current_domain:
                    if external_domain not in self.visited_urls:
                        self.visited_urls.add(external_domain)
                        
                        # Vérifier le statut DNS
                        dns_status = self.check_dns(external_domain)
                        
                        yield {
                            'url_source': response.url,
                            'domaine_externe': external_domain,
                            'status_http': response.status,
                            'statut_dns': dns_status,
                            'date_scan': datetime.now().isoformat()
                        }
                
                # Continuer le crawling sur le même domaine
                if parsed_url.netloc == current_domain:
                    yield response.follow(url, self.parse)
                    
            except Exception as e:
                self.logger.error(f"Erreur lors du traitement de l'URL {href}: {str(e)}")
    
    def check_dns(self, domain):
        try:
            dns.resolver.resolve(domain)
            return "ACTIVE"
        except:
            return "INACTIVE"
