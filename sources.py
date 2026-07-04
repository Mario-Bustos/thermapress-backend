RSS_FEEDS = {
    'bbc':     'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn':     'http://rss.cnn.com/rss/edition.rss',
    'fox':     'https://moxie.foxnews.com/google-publisher/latest.xml',
    'nyt':     'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
    'nbc':     'https://feeds.nbcnews.com/nbcnews/public/news',
    'cbs':     'https://www.cbsnews.com/latest/rss/main',
    'ap':      'https://feeds.apnews.com/rss/apf-topnews',
    'reuters': 'https://feeds.reuters.com/reuters/topNews',
}

CATEGORY_KEYWORDS = {
    'sports':        ['sport', 'football', 'soccer', 'basketball', 'nba', 'nfl', 'tennis', 'golf', 'olympic'],
    'science':       ['science', 'research', 'study', 'space', 'nasa', 'discovery', 'biology', 'physics'],
    'technology':    ['technology', 'tech', 'ai', 'artificial intelligence', 'software', 'apple', 'google', 'microsoft', 'startup'],
    'politics':      ['politics', 'government', 'election', 'congress', 'senate', 'president', 'democrat', 'republican', 'policy'],
    'business':      ['business', 'economy', 'market', 'stock', 'trade', 'company', 'corporate', 'finance', 'gdp'],
    'entertainment': ['entertainment', 'movie', 'music', 'celebrity', 'film', 'tv', 'television', 'award', 'hollywood'],
    'health':        ['health', 'medical', 'hospital', 'disease', 'vaccine', 'mental health', 'wellness', 'cancer', 'drug'],
    'world':         ['world', 'international', 'global', 'foreign', 'war', 'conflict', 'diplomacy', 'united nations'],
    'environment':   ['environment', 'climate', 'carbon', 'emission', 'renewable', 'fossil', 'wildfire', 'flood', 'drought'],
    'finance':       ['finance', 'investment', 'crypto', 'bitcoin', 'interest rate', 'inflation', 'federal reserve', 'banking'],
}