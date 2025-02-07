# crawler/settings.py

BOT_NAME = 'domain_crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

# Respecter robots.txt
ROBOTSTXT_OBEY = True

# Configuration des délais
DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS = 16

# Middleware personnalisé pour la gestion des erreurs
DOWNLOADER_MIDDLEWARES = {
    'crawler.middlewares.CustomDownloaderMiddleware': 543,
}

# Pipeline pour Supabase
ITEM_PIPELINES = {
    'crawler.pipelines.SupabasePipeline': 300,
}

# Configuration Supabase
SUPABASE_URL = "https://rtvnevavydjycfwoxatd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0dm5ldmF2eWRqeWNmd294YXRkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg3OTYyMTgsImV4cCI6MjA1NDM3MjIxOH0.uwZPcBmLPNgmhm6xoKc2HPWtqUTY0VGaJscZ7l9HfKE"  # Utilisez une nouvelle clé API sécurisée
