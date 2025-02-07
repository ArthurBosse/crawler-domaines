import scrapy
from urllib.parse import urlparse
import dns.resolver
import aiohttp
from datetime import datetime
from supabase import create_client, Client
import asyncio

class DomainSpider(scrapy.Spider):
    name = "domain_crawler"
    
    def __init__(self, start_url=None, *args, **kwargs):
        super(DomainSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else []
        self.visited_urls = set()
        
        # Initialisation de Supabase
        supabase_url = "https://rtvnevavydjycfwoxatd.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0dm5ldmF2eWRqeWNmd294YXRkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg3OTYyMTgsImV4cCI6MjA1NDM3MjIxOH0.uwZPcBmLPNgmhm6xoKc2HPWtqUTY0VGaJscZ7l9HfKE"
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Configuration du crawler
        self.custom_settings = {
            'CONCURRENT_REQUESTS': 16,
            'DOWNLOAD_DELAY': 1,
            'ROBOTSTXT_OBEY': True,
        }

    def check_domain_status(self, domain):
        # Vérification DNS
        try:
            dns_result = dns.resolver.resolve(domain, 'A')
            dns_status = 'ACTIVE'
        except Exception as e:
            dns_status = str(e)

        # Vérification HTTP
        try:
            # Utilisation de requests au lieu de aiohttp pour la simplicité
            import requests
            response = requests.get(f'http://{domain}', timeout=10)
            http_status = response.status_code
        except Exception as e:
            http_status = str(e)

        return http_status, dns_status

    def parse(self, response):
        current_url = response.url
        self.logger.info(f'Crawling: {current_url}')

        # Extraction des liens externes
        for href in response.css('a::attr(href)').getall():
            try:
                parsed_url = urlparse(response.urljoin(href))
                domain = parsed_url.netloc

                if domain and domain not in self.visited_urls:
                    self.visited_urls.add(domain)
                    
                    # Vérification du domaine
                    http_status, dns_status = self.check_domain_status(domain)
                    
                    # Enregistrement dans Supabase
                    data = {
                        'url_source': current_url,
                        'domaine_externe': domain,
                        'status_http': str(http_status),
                        'statut_dns': dns_status,
                        'date_scan': datetime.now().isoformat()
                    }
                    
                    self.supabase.table('domaines').insert(data).execute()
                    
                    self.logger.info(f'Domain checked: {domain} - HTTP: {http_status}, DNS: {dns_status}')

                    # Suivre le lien s'il est sur le même domaine
                    if domain == urlparse(current_url).netloc:
                        yield response.follow(href, self.parse)
                        
            except Exception as e:
                self.logger.error(f'Error processing URL {href}: {str(e)}')