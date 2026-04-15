#!/usr/bin/env python3
"""
Instagram Agent - Main Orchestrator
Coordinates the full pipeline: fetch news → generate content → post to Instagram
"""

import os
import json
import logging
import sys

# Fix Windows console encoding for Unicode symbols
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from fetcher import NewsFetcher
from generator import ContentGenerator
from poster import InstagramPoster


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Constants
POSTED_URLS_FILE = 'posted_urls.json'
MAX_URLS_HISTORY = 50


def load_posted_urls() -> list:
    """Load the list of already-posted article URLs from JSON file.
    
    Returns:
        List of previously posted URLs, or empty list if file doesn't exist
    """
    try:
        if os.path.exists(POSTED_URLS_FILE):
            with open(POSTED_URLS_FILE, 'r') as f:
                data = json.load(f)
                urls = data.get('urls', []) if isinstance(data, dict) else data
                logger.debug(f"Loaded {len(urls)} previously posted URLs")
                return urls
        else:
            logger.debug("No posted URLs history found")
            return []
    except Exception as e:
        logger.warning(f"Failed to load posted URLs: {e}")
        return []


def save_posted_url(url: str) -> bool:
    """Add a URL to the posted URLs list and save to JSON file.
    
    Keeps only the last MAX_URLS_HISTORY (50) URLs to prevent unbounded growth.
    
    Args:
        url: Article URL that was successfully posted
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Load current URLs
        urls = load_posted_urls()
        
        # Add new URL if not already present
        if url not in urls:
            urls.append(url)
            logger.debug(f"Added URL to posted history: {url[:50]}...")
        
        # Keep only last 50 URLs
        if len(urls) > MAX_URLS_HISTORY:
            removed_count = len(urls) - MAX_URLS_HISTORY
            urls = urls[-MAX_URLS_HISTORY:]
            logger.debug(f"Trimmed {removed_count} old URLs from history")
        
        # Save to file
        with open(POSTED_URLS_FILE, 'w') as f:
            json.dump({'urls': urls, 'last_updated': datetime.now().isoformat()}, f, indent=2)
        
        logger.debug(f"Saved posted URLs ({len(urls)} total)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save posted URL: {e}")
        return False


def is_already_posted(url: str) -> bool:
    """Check if an article URL has already been posted.
    
    Args:
        url: Article URL to check
        
    Returns:
        True if URL was already posted, False otherwise
    """
    try:
        urls = load_posted_urls()
        is_posted = url in urls
        
        if is_posted:
            logger.info(f"✗ Article already posted: {url[:60]}...")
        
        return is_posted
    except Exception as e:
        logger.warning(f"Error checking posted URL: {e}")
        return False


def setup_logs_file():
    """Ensure logs.txt file exists."""
    if not os.path.exists('logs.txt'):
        with open('logs.txt', 'w') as f:
            f.write("Instagram Agent - Execution Log\n")
            f.write("=" * 80 + "\n\n")


def log_to_file(status: str, article_title: str):
    """Write execution log to logs.txt file.
    
    Args:
        status: SUCCESS or FAILED
        article_title: Title of the article posted/attempted
    """
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        log_entry = f"[{timestamp}] {status} | {article_title}\n"
        
        with open('logs.txt', 'a') as f:
            f.write(log_entry)
    except Exception as e:
        logger.error(f"Failed to write to logs.txt: {e}")


def run_agent():
    """Execute the full Instagram automation pipeline.
    
    Pipeline:
    1. Fetch latest AI/Tech news
    2. Check if article was already posted (duplicate prevention)
    3. Select most recent article
    4. Generate Instagram caption using Gemini
    5. Generate image URL using Pollinations
    6. Post to Instagram
    7. Save URL to prevent duplicates
    8. Log results
    
    Returns:
        True if post was successful, False otherwise
    """
    try:
        logger.info("=" * 70)
        logger.info("Instagram Agent - Starting Execution")
        logger.info("=" * 70)
        
        # Step 1: Fetch News
        logger.info("\n[1/6] Fetching AI & Tech news...")
        fetcher = NewsFetcher()
        articles = fetcher.fetch_latest_ai_news()
        
        if not articles:
            logger.warning("✗ No articles found - exiting")
            log_to_file("FAILED", "No articles fetched")
            return False
        
        logger.info(f"✓ Found {len(articles)} articles")
        
        # Step 2: Check for Duplicates and Select Article
        logger.info("\n[2/6] Checking for duplicates...")
        article = None
        
        for candidate in articles:
            if not is_already_posted(candidate['url']):
                article = candidate
                logger.info(f"✓ Found new article to post")
                break
        
        if not article:
            logger.warning("✗ All fetched articles were already posted - exiting")
            log_to_file("SKIPPED", "All articles already posted")
            return False
        
        # Step 3: Display Selected Article
        logger.info("\n[3/6] Selecting article...")
        logger.info(f"✓ Selected: {article['title']}")
        logger.info(f"  Source: {article['source']}")
        logger.info(f"  Summary: {article['summary'][:100]}...")
        
        # Step 4: Generate Caption + Carousel Images
        logger.info("\n[4/6] Generating caption + carousel slides...")
        generator = ContentGenerator()
        content = generator.generate_carousel_content(article)
        caption    = content["caption"]
        image_urls = content["image_urls"]
        
        if not caption:
            logger.error("\u2717 Failed to generate caption - exiting")
            log_to_file("FAILED", article['title'])
            return False
        
        logger.info(f"\u2713 Caption generated ({len(caption)} chars)")
        logger.info(f"  Caption preview: {caption[:80]}...")
        logger.info(f"\u2713 Carousel images: {len(image_urls)} slides")
        
        # Step 5: Log Image Info
        logger.info("\n[5/6] Image URLs ready...")
        if not image_urls:
            logger.error("\u2717 No images generated - exiting")
            log_to_file("FAILED", article['title'])
            return False
        logger.info(f"\u2713 Cover image: {image_urls[0][:60]}...")
        if len(image_urls) > 1:
            logger.info(f"\u2713 Text slides: {len(image_urls) - 1} additional slides")
        
        # Step 6: Post Carousel to Instagram
        logger.info("\n[6/6] Posting carousel to Instagram...")
        poster = InstagramPoster()
        
        # Verify token is valid before posting
        if not poster.check_token_valid():
            logger.error("✗ Instagram token validation failed - exiting")
            log_to_file("FAILED", article['title'])
            return False
        
        success = poster.post_carousel_to_instagram(image_urls, caption)
        
        if success:
            logger.info("✓ Successfully posted to Instagram!")
            
            # Save URL to prevent duplicate posts
            if save_posted_url(article['url']):
                logger.info(f"✓ Article URL saved to duplicate prevention list")
            
            log_to_file("SUCCESS", article['title'])
            logger.info("\n" + "=" * 70)
            logger.info("Instagram Agent - Execution Complete")
            logger.info("=" * 70 + "\n")
            return True
        else:
            logger.error("✗ Failed to post to Instagram")
            log_to_file("FAILED", article['title'])
            return False
        
    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
        logger.error("Please ensure all required .env variables are set")
        log_to_file("ERROR", f"Configuration Error: {str(e)[:50]}")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        log_to_file("ERROR", f"Exception: {str(e)[:50]}")
        return False


def main():
    """Main entry point for the Instagram Agent."""
    print("\n" + "=" * 70)
    print("Instagram Agent - AI & Tech Content Automation")
    print("=" * 70 + "\n")
    
    # Setup logs file
    setup_logs_file()
    
    # Validate environment
    required_vars = [
        'GEMINI_API_KEY',
        'INSTAGRAM_ACCOUNT_ID',
        'INSTAGRAM_ACCESS_TOKEN'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.endswith('_here') or value.endswith('_id') or value.endswith('_token'):
            missing.append(var)
    
    if missing:
        logger.error(f"Missing or incomplete environment variables: {', '.join(missing)}")
        logger.error("Please update your .env file with valid credentials")
        logger.error("\nSetup Guide:")
        logger.error("1. Get GEMINI_API_KEY from: https://aistudio.google.com/app/apikeys")
        logger.error("2. Get INSTAGRAM_ACCOUNT_ID and INSTAGRAM_ACCESS_TOKEN from:")
        logger.error("   https://developers.facebook.com/docs/instagram-api/getting-started")
        return False
    
    logger.info("✓ Environment validated")
    logger.info(f"✓ Logging to: logs.txt\n")
    
    # Run the agent
    success = run_agent()
    
    if success:
        logger.info("✓ Agent execution successful")
        return True
    else:
        logger.warning("⚠ Agent execution incomplete - check logs for details")
        return False


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n\n⚠ Agent interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
