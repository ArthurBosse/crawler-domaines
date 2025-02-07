import scrapy
from urllib.parse import urlparse
import dns.resolver
from datetime import datetime
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialisation de colorama
init(autoreset=True)

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
            self.logger.error(f"{Fore.RED}URLs ou clés Supabase manquantes{Style.RESET_ALL}")
            return
            
        # Initialisation avec authentification
        self.supabase = create_client(supabase_url, supabase_key)
        
        # Authentification avec un compte de service
        email = os.getenv('SUPABASE_USER_EMAIL')
        password = os.getenv('SUPABASE_USER_PASSWORD')
        
        if not email or not password:
            self.logger.error(f"{Fore.RED}Credentials d'authentification manquants{Style.RESET_ALL}")
            return
            
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            self.access_token = auth_response.session.access_token
            self.logger.info(f"{Fore.GREEN}Authentification Supabase réussie{Style.RESET_ALL}")
            self.logger.info(f"Session expiration: {auth_response.session.expires_at}")
            self.logger.info(f"User ID: {auth_response.user.id}")
            
            # Configuration du client avec le token d'accès
            self.supabase.postgrest.auth(self.access_token)
            
        except Exception as e:
            self.logger.error(f"{Fore.RED}Erreur d'authentification Supabase: {str(e)}{Style.RESET_ALL}")
        
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
        self.logger.info(f'{Fore.CYAN}Crawling: {current_url}{Style.RESET_ALL}')

        # Extraction des liens
        for href in response.css('a::attr(href)').getall():
            try:
                absolute_url = response.urljoin(href)
                parsed_url = urlparse(absolute_url)
                domain = parsed_url.netloc

                # Vérification du domaine externe
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
                        self.logger.info(f"Tentative d'insertion pour {domain} avec token: {self.access_token[:10]}...")
                        result = self.supabase.table('domaines').insert(data).execute()
                        self.logger.info(f'{Fore.GREEN}Domain checked and inserted: {domain} - HTTP: {http_status}, DNS: {dns_status}{Style.RESET_ALL}')
                    except Exception as e:
                        self.logger.error(f'{Fore.RED}Erreur Supabase pour {domain}: {str(e)}{Style.RESET_ALL}')
                        try:
                            session = self.supabase.auth.get_session()
                            if session:
                                self.access_token = session.access_token
                                self.supabase.postgrest.auth(self.access_token)
                                self.logger.info(f"{Fore.YELLOW}Token rafraîchi, nouvelle tentative d'insertion...{Style.RESET_ALL}")
                                result = self.supabase.table('domaines').insert(data).execute()
                                self.logger.info(f'{Fore.GREEN}Domain inserted after token refresh: {domain}{Style.RESET_ALL}')
                        except Exception as refresh_error:
                            self.logger.error(f'{Fore.RED}Erreur de rafraîchissement du token: {str(refresh_error)}{Style.RESET_ALL}')

                # Suivre tous les liens du même domaine de départ
                start_domain = urlparse(self.start_urls[0]).netloc
                if parsed_url.netloc == start_domain and absolute_url not in self.visited_urls:
                    self.visited_urls.add(absolute_url)
                    self.logger.info(f'{Fore.YELLOW}Following link: {absolute_url}{Style.RESET_ALL}')
                    yield response.follow(absolute_url, self.parse)
                        
            except Exception as e:
                self.logger.error(f'{Fore.RED}Error processing URL {href}: {str(e)}{Style.RESET_ALL}')