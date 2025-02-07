# crawler/pipelines.py

from supabase import create_client

class SupabasePipeline:
    def __init__(self, supabase_url, supabase_key):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            supabase_url=crawler.settings.get('SUPABASE_URL'),
            supabase_key=crawler.settings.get('SUPABASE_KEY')
        )
    
    def open_spider(self, spider):
        self.supabase = create_client(self.supabase_url, self.supabase_key)
    
    def process_item(self, item, spider):
        self.supabase.table('domaines').insert(item).execute()
        return item
