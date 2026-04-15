"""
News Fetcher Module for Instagram Agent
Fetches AI & Tech news from multiple RSS feeds with keyword filtering.
"""

import feedparser
import os
from datetime import datetime
from typing import List, Dict
from urllib.parse import urlparse


class NewsFetcher:
    """Fetches and filters AI/Tech news from multiple RSS feed sources."""
    
    # AI & Coding related keywords for filtering
    AI_KEYWORDS = {
        'ai', 'artificial intelligence', 'machine learning', 'gpt', 'llm',
        'claude', 'gemini', 'llama', 'mistral', 'openai', 'anthropic',
        'coding agent', 'software engineering', 'developer tool',
        'copilot', 'devin', 'programming', 'code generation',
        'automation', 'deep learning', 'transformer', 'neural',
        'nlp', 'agentic', 'swe-agent', 'devops', 'backend', 'frontend'
    }
    
    # RSS feed sources
    FEEDS = {
        'techcrunch': 'https://techcrunch.com/feed/',
        'mit_tech_review': 'https://www.technologyreview.com/feed/',
        'the_verge': 'https://www.theverge.com/rss/index.xml'
    }
    
    def __init__(self):
        """Initialize the NewsFetcher with feed sources."""
        self.timeout = 10
    
    def _contains_ai_keywords(self, text: str) -> bool:
        """Check if text contains AI-related keywords.
        
        Args:
            text: Text to check (title or summary)
            
        Returns:
            True if any AI keyword is found (case-insensitive)
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.AI_KEYWORDS)
    
    def _parse_feed(self, feed_name: str, feed_url: str, max_articles: int = 3) -> List[Dict]:
        """Parse a single RSS feed and filter for AI content.
        
        Args:
            feed_name: Name of the feed source
            feed_url: URL of the RSS feed
            max_articles: Maximum articles to fetch from this feed
            
        Returns:
            List of filtered article dictionaries
        """
        articles = []
        
        try:
            print(f"[Fetcher] Fetching from {feed_name}...")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                print(f"[Fetcher] Warning: Feed parse issues from {feed_name}")
            
            if not feed.entries:
                print(f"[Fetcher] No entries found in {feed_name}")
                return articles
            
            for entry in feed.entries[:10]:  # Check top 10 to find 3 matching
                if len(articles) >= max_articles:
                    break
                
                title = entry.get('title', 'No title')
                summary = entry.get('summary', '')
                url = entry.get('link', '')
                
                # Filter by AI keywords
                if self._contains_ai_keywords(title) or self._contains_ai_keywords(summary):
                    article = {
                        'title': title,
                        'summary': summary[:300] if summary else 'No summary',
                        'url': url,
                        'source': feed_name,
                        'published': entry.get('published', '')
                    }
                    articles.append(article)
            
            print(f"[Fetcher] Found {len(articles)} AI-related articles from {feed_name}")
            return articles
            
        except Exception as e:
            print(f"[Fetcher] Error fetching from {feed_name}: {e}")
            return []
    
    def fetch_latest_ai_news(self) -> List[Dict]:
        """Fetch the latest AI/Tech news from all configured feeds.
        
        Returns:
            List of article dictionaries with keys: title, summary, url, source
        """
        all_articles = []
        
        for feed_name, feed_url in self.FEEDS.items():
            articles = self._parse_feed(feed_name, feed_url, max_articles=3)
            all_articles.extend(articles)
        
        print(f"[Fetcher] Total articles fetched: {len(all_articles)}")
        return all_articles
    
    def get_random_article(self) -> Dict:
        """Get a random AI/Tech article from the feeds.
        
        Returns:
            Random article dictionary or None if no articles found
        """
        import random
        articles = self.fetch_latest_ai_news()
        return random.choice(articles) if articles else None
    
    def get_articles_by_source(self, source: str) -> List[Dict]:
        """Get articles from a specific source.
        
        Args:
            source: Source name (techcrunch, mit_tech_review, the_verge)
            
        Returns:
            List of articles from that source
        """
        if source not in self.FEEDS:
            print(f"[Fetcher] Unknown source: {source}")
            return []
        
        return self._parse_feed(source, self.FEEDS[source])


def main():
    """Test the NewsFetcher with sample output."""
    print("=" * 60)
    print("Instagram Agent - News Fetcher Test")
    print("=" * 60)
    
    fetcher = NewsFetcher()
    
    # Fetch all AI news
    articles = fetcher.fetch_latest_ai_news()
    
    if articles:
        print(f"\n✓ Successfully fetched {len(articles)} articles:\n")
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   Summary: {article['summary'][:100]}...")
            print(f"   URL: {article['url']}\n")
    else:
        print("✗ No articles found")
    
    # Test random article
    random_article = fetcher.get_random_article()
    if random_article:
        print(f"\nRandom article: {random_article['title']}")


if __name__ == '__main__':
    main()
