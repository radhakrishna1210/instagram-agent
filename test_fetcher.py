"""
Test script for fetcher.py
Tests the NewsFetcher class and prints formatted results.
"""

from fetcher import NewsFetcher


def test_fetcher():
    """Test the NewsFetcher and display results."""
    print("=" * 70)
    print("FETCHER TEST - AI/Tech News Feed")
    print("=" * 70)
    
    try:
        fetcher = NewsFetcher()
        articles = fetcher.fetch_latest_ai_news()
        
        # Check if at least 1 article was returned
        if len(articles) < 1:
            print("\n✗ FAIL: No articles fetched")
            return False
        
        print(f"\n✓ Successfully fetched {len(articles)} articles")
        print("\n" + "-" * 70)
        print("FIRST ARTICLE:")
        print("-" * 70)
        
        first = articles[0]
        
        # Format and print article details
        print(f"\nTitle:\n  {first['title']}")
        print(f"\nSource:\n  {first['source'].replace('_', ' ').title()}")
        
        # Show 100-character preview of summary
        summary = first['summary']
        preview = summary[:100] + "..." if len(summary) > 100 else summary
        print(f"\nSummary Preview (100 chars):\n  {preview}")
        
        print(f"\nURL:\n  {first['url']}")
        
        print("\n" + "-" * 70)
        print("✓ PASS: Fetcher test successful")
        print("-" * 70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ FAIL: Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_fetcher()
    exit(0 if success else 1)
