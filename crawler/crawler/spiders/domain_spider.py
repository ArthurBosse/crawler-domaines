import scrapy
from urllib.parse import urlparse
import dns.resolver
from datetime import datetime
from supabase import create_client, Client
import os
from dotenv import load_dotenv

class DomainSpider(scrapy.Spider):
    name = "domain_crawler"
    
    def __init__(self, start_url=None, *args, **kwargs):
        super(DomainSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else []
        self.visited_urls = set()
        
        # Chargement des variables d'environnement
        load_dotenv()
        
        # Initialisation de Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            self.logger.error("URLs ou clés Supabase manquantes")
            return
            
        # Initialisation avec authentification
        self.supabase = create_client(supabase_url, supabase_key)
        
        # Authentification avec un compte de service
        email = os.getenv('SUPABASE_USER_EMAIL')
        password = os.getenv('SUPABASE_USER_PASSWORD')
        
        if not email or not password:
            self.logger.error("Credentials d'authentification manquants")
            return
            
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            self.logger.info("Authentification Supabase réussie")
            self.logger.info(f"Session expiration: {auth_response.session.expires_at}")
            self.logger.info(f"User ID: {auth_response.user.id}")
        except Exception as e:
            self.logger.error(f"Erreur d'authentification Supabase: {str(e)}")
        
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
                    
                    try:
                        # Vérification de l'état de l'authentification avant l'insertion
                        session = self.supabase.auth.get_session()
                        if session:
                            self.logger.info(f"Tentative d'insertion avec token valide pour {domain}")
                            result = self.supabase.table('domaines').insert(data).execute()
                            self.logger.info(f'Domain checked and inserted: {domain} - HTTP: {http_status}, DNS: {dns_status}')
                        else:
                            self.logger.error(f"Session invalide lors de l'insertion pour {domain}")
                    except Exception as e:
                        self.logger.error(f'Erreur Supabase pour {domain}: {str(e)}')

                    # Suivre le lien s'il est sur le même domaine
                    if domain == urlparse(current_url).netloc:
                        yield response.follow(href, self.parse)
                        
            except Exception as e:
                self.logger.error(f'Error processing URL {href}: {str(e)}')