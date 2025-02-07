import scrapy
from urllib.parse import urlparse, urldefrag
import dns.resolver
from datetime import datetime
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style
import logging
from logging.handlers import RotatingFileHandler

# Initialisation de colorama
init(autoreset=True)

class DomainSpider(scrapy.Spider):
    name = "domain_crawler"
    
    def __init__(self, start_url=None, *args, **kwargs):
        super(DomainSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else []
        self.visited_urls = set()
        
        # Configuration du logger personnalisé
        self.setup_logger()
        
        # Chargement des variables d'environnement
        load_dotenv()
        
        # Initialisation de Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            self.file_logger.error("URLs ou clés Supabase manquantes")
            self.logger.error(f"{Fore.RED}URLs ou clés Supabase manquantes{Style.RESET_ALL}")
            return
            
        # Initialisation avec authentification
        self.supabase = create_client(supabase_url, supabase_key)
        
        # Authentification avec un compte de service
        email = os.getenv('SUPABASE_USER_EMAIL')
        password = os.getenv('SUPABASE_USER_PASSWORD')
        
        if not email or not password:
            self.file_logger.error("Credentials d'authentification manquants")
            self.logger.error(f"{Fore.RED}Credentials d'authentification manquants{Style.RESET_ALL}")
            return
            
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            self.access_token = auth_response.session.access_token
            self.file_logger.info("Authentification Supabase réussie")
            self.logger.info(f"{Fore.GREEN}Authentification Supabase réussie{Style.RESET_ALL}")
            self.logger.info(f"Session expiration: {auth_response.session.expires_at}")
            self.logger.info(f"User ID: {auth_response.user.id}")
            
            # Configuration du client avec le token d'accès
            self.supabase.postgrest.auth(self.access_token)
            
        except Exception as e:
            error_msg = f"Erreur d'authentification Supabase: {str(e)}"
            self.file_logger.error(error_msg)
            self.logger.error(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
        
        # Configuration du crawler
        self.custom_settings = {
            'CONCURRENT_REQUESTS': 100,
            'DOWNLOAD_DELAY': 1,
            'ROBOTSTXT_OBEY': True,
        }

    def setup_logger(self):
        # Création du dossier logs s'il n'existe pas
        os.makedirs('logs', exist_ok=True)
        
        # Configuration du logger pour le fichier
        self.file_logger = logging.getLogger('crawler_file_logger')
        self.file_logger.setLevel(logging.INFO)
        
        # Handler pour le fichier de log avec rotation
        file_handler = RotatingFileHandler(
            'logs/crawler.log',
            maxBytes=100*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # Format personnalisé pour les logs
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Ajout du handler au logger
        self.file_logger.addHandler(file_handler)

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
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Log de la page en cours
        crawl_msg = f"PAGE CRAWLÉE: {current_url} - {timestamp}"
        self.file_logger.info(crawl_msg)
        self.logger.info(f'{Fore.CYAN}{crawl_msg}{Style.RESET_ALL}')

        # Extraction des liens
        external_domains = set()
        for href in response.css('a::attr(href)').getall():
            try:
                # Supprimer l'ancre de l'URL
                url_without_fragment, _ = urldefrag(response.urljoin(href))
                
                # Si l'URL contient une ancre, on l'ignore
                if '#' in href:
                    anchor_msg = f"URL ignorée (ancre): {href}"
                    self.file_logger.info(anchor_msg)
                    self.logger.info(f'{Fore.YELLOW}{anchor_msg}{Style.RESET_ALL}')
                    continue
                
                parsed_url = urlparse(url_without_fragment)
                domain = parsed_url.netloc

                # Vérification du domaine externe
                if domain and domain not in self.visited_urls:
                    self.visited_urls.add(domain)
                    external_domains.add(domain)
                    
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
                        success_msg = f"Domaine enregistré: {domain} - HTTP: {http_status}, DNS: {dns_status}"
                        self.file_logger.info(success_msg)
                        self.logger.info(f'{Fore.GREEN}{success_msg}{Style.RESET_ALL}')
                    except Exception as e:
                        error_msg = f"Erreur Supabase pour {domain}: {str(e)}"
                        self.file_logger.error(error_msg)
                        self.logger.error(f'{Fore.RED}{error_msg}{Style.RESET_ALL}')
                        try:
                            session = self.supabase.auth.get_session()
                            if session:
                                self.access_token = session.access_token
                                self.supabase.postgrest.auth(self.access_token)
                                refresh_msg = "Token rafraîchi, nouvelle tentative d'insertion..."
                                self.file_logger.info(refresh_msg)
                                self.logger.info(f"{Fore.YELLOW}{refresh_msg}{Style.RESET_ALL}")
                                result = self.supabase.table('domaines').insert(data).execute()
                                success_msg = f"Domaine enregistré après rafraîchissement: {domain}"
                                self.file_logger.info(success_msg)
                                self.logger.info(f'{Fore.GREEN}{success_msg}{Style.RESET_ALL}')
                        except Exception as refresh_error:
                            error_msg = f"Erreur de rafraîchissement du token: {str(refresh_error)}"
                            self.file_logger.error(error_msg)
                            self.logger.error(f'{Fore.RED}{error_msg}{Style.RESET_ALL}')

                # Suivre tous les liens du même domaine de départ
                start_domain = urlparse(self.start_urls[0]).netloc
                if parsed_url.netloc == start_domain and url_without_fragment not in self.visited_urls:
                    self.visited_urls.add(url_without_fragment)
                    follow_msg = f"Suivi du lien: {url_without_fragment}"
                    self.file_logger.info(follow_msg)
                    self.logger.info(f'{Fore.YELLOW}{follow_msg}{Style.RESET_ALL}')
                    yield response.follow(url_without_fragment, self.parse)
                        
            except Exception as e:
                error_msg = f"Erreur de traitement de l'URL {href}: {str(e)}"
                self.file_logger.error(error_msg)
                self.logger.error(f'{Fore.RED}{error_msg}{Style.RESET_ALL}')
        
        # Log des domaines externes trouvés sur la page
        if external_domains:
            domains_msg = f"Domaines externes trouvés sur {current_url}:\n" + "\n".join(f"- {domain}" for domain in external_domains)
            self.file_logger.info(domains_msg)