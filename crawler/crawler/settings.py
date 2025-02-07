BOT_NAME = "domain_crawler"

SPIDER_MODULES = ["crawler.spiders"]
NEWSPIDER_MODULE = "crawler.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (compatible; DomainCrawler/1.0)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performing at the same time to the same domain
CONCURRENT_REQUESTS_PER_DOMAIN = 16

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 1

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
   "crawler.middlewares.CrawlerDownloaderMiddleware": 543,
}

# Enable or disable spider middlewares
SPIDER_MIDDLEWARES = {
   "crawler.middlewares.CrawlerSpiderMiddleware": 543,
}

# Configure item pipelines
ITEM_PIPELINES = {
   "crawler.pipelines.CrawlerPipeline": 300,
}