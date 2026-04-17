"""
Instagram Poster Module for Instagram Agent
Posts images to Instagram using Meta Graph API (requires Business/Creator account)
"""

import os
import time
import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class InstagramPoster:
    """Posts images and captions to Instagram using Meta Graph API."""
    
    # Meta Graph API version
    API_VERSION = 'v19.0'
    GRAPH_API_BASE = f'https://graph.facebook.com/{API_VERSION}'
    
    def __init__(self):
        """Initialize InstagramPoster with credentials from .env"""
        self.account_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.client_id = os.getenv('FACEBOOK_APP_ID')
        self.client_secret = os.getenv('FACEBOOK_APP_SECRET')
        
        if not self.account_id or not self.access_token:
            raise ValueError(
                "INSTAGRAM_ACCOUNT_ID and INSTAGRAM_ACCESS_TOKEN must be set in .env file. "
                "This requires a Meta Business or Creator account linked to Instagram."
            )
        
        print(f"[Poster] Initialized with account ID: {self.account_id}")
    
    def check_token_valid(self) -> bool:
        """Verify that the access token is still valid and has required permissions.
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            url = f"{self.GRAPH_API_BASE}/me"
            params = {'access_token': self.access_token}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[Poster] ✓ Token valid for user: {data.get('name', 'Unknown')}")
                return True
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"[Poster] ✗ Token validation failed: {error_msg}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"[Poster] ✗ Network error checking token: {e}")
            return False
        except Exception as e:
            print(f"[Poster] ✗ Error validating token: {e}")
            return False
    
    def get_token_expiry_days(self) -> Optional[int]:
        """Get the number of days remaining before the access token expires.
        
        Queries the Graph API to check token expiry information.
        
        Returns:
            Number of days until expiry (int), or None if unable to determine
        """
        try:
            url = f"{self.GRAPH_API_BASE}/debug_token"
            params = {
                'input_token': self.access_token,
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                expires_at = data.get('expires_at', 0)
                
                if expires_at == 0:
                    print("[Poster] ⚠ Token has no expiry date (never expires)")
                    return None
                
                # Convert Unix timestamp to datetime
                expiry_datetime = datetime.fromtimestamp(expires_at)
                now = datetime.now()
                days_remaining = (expiry_datetime - now).days
                
                print(f"[Poster] Token expires on: {expiry_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"[Poster] Days remaining: {days_remaining}")
                
                return days_remaining
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"[Poster] ✗ Failed to check token expiry: {error_msg}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"[Poster] ✗ Network error checking token expiry: {e}")
            return None
        except Exception as e:
            print(f"[Poster] ✗ Error checking token expiry: {e}")
            return None
    
    def refresh_access_token(self) -> bool:
        """Refresh the long-lived access token before it expires.
        
        Calls the Meta Graph API to exchange the current long-lived token for a new one.
        Requires FACEBOOK_APP_ID and FACEBOOK_APP_SECRET in .env file.
        
        Returns:
            True if token was refreshed successfully, False otherwise
        """
        try:
            # Check if app credentials are available
            if not self.client_id or not self.client_secret:
                print("[Poster] ✗ FACEBOOK_APP_ID and FACEBOOK_APP_SECRET required for token refresh")
                print("[Poster] Add these to your .env file from https://developers.facebook.com/apps")
                return False
            
            url = f"{self.GRAPH_API_BASE}/oauth/access_token"
            
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'fb_exchange_token': self.access_token
            }
            
            print("[Poster] Refreshing access token...")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                new_token = data.get('access_token')
                expires_in = data.get('expires_in', 0)  # Seconds
                
                if not new_token:
                    print("[Poster] ✗ No token in response")
                    return False
                
                # Calculate expiry date
                expiry_date = (datetime.now() + timedelta(seconds=expires_in)).strftime('%Y-%m-%d %H:%M:%S')
                expiry_days = expires_in // 86400
                
                print(f"[Poster] ✓ Token refreshed successfully!")
                print(f"[Poster] New token: {new_token[:20]}...{new_token[-10:]}")
                print(f"[Poster] Expires in: {expiry_days} days ({expiry_date})")
                print(f"\n[Poster] Update your .env file with:")
                print(f"INSTAGRAM_ACCESS_TOKEN={new_token}")
                
                return True
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"[Poster] ✗ Failed to refresh token: {error_msg}")
                print(f"[Poster] Status code: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print("[Poster] ✗ Request timeout refreshing token")
            return False
        except requests.exceptions.RequestException as e:
            print(f"[Poster] ✗ Network error refreshing token: {e}")
            return False
        except Exception as e:
            print(f"[Poster] ✗ Error refreshing token: {e}")
            return False
    
    def _create_media_container(self, image_url: str, caption: str) -> Optional[str]:
        """Create a media container on Instagram.
        
        Step 1 of the posting process. Creates a container that holds the image
        and caption before publishing.
        
        Args:
            image_url: URL of the image to post
            caption: Caption text for the post
            
        Returns:
            creation_id (string) if successful, None if failed
        """
        try:
            url = f"{self.GRAPH_API_BASE}/{self.account_id}/media"
            
            payload = {
                'image_url': image_url,
                'caption': caption,
                'access_token': self.access_token
            }
            
            print(f"[Poster] Creating media container...")
            response = requests.post(url, data=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                creation_id = data.get('id')
                print(f"[Poster] ✓ Media container created: {creation_id}")
                return creation_id
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"[Poster] ✗ Failed to create media container: {error_msg}")
                print(f"[Poster] Status code: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("[Poster] ✗ Request timeout creating media container")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[Poster] ✗ Network error creating media container: {e}")
            return None
        except Exception as e:
            print(f"[Poster] ✗ Error creating media container: {e}")
            return None
    
    def _publish_media_container(self, creation_id: str) -> Optional[Dict]:
        """Publish a media container to Instagram.
        
        Step 2 of the posting process. Publishes the created container,
        making the post visible on the Instagram feed.
        
        Args:
            creation_id: The media container ID from _create_media_container()
            
        Returns:
            Response dict with media_id if successful, None if failed
        """
        try:
            url = f"{self.GRAPH_API_BASE}/{self.account_id}/media_publish"
            
            payload = {
                'creation_id': creation_id,
                'access_token': self.access_token
            }
            
            print(f"[Poster] Publishing media container...")
            response = requests.post(url, data=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                media_id = data.get('id')
                print(f"[Poster] ✓ Media published successfully: {media_id}")
                return {'media_id': media_id, 'creation_id': creation_id}
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                print(f"[Poster] ✗ Failed to publish media: {error_msg}")
                print(f"[Poster] Status code: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("[Poster] ✗ Request timeout publishing media")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[Poster] ✗ Network error publishing media: {e}")
            return None
        except Exception as e:
            print(f"[Poster] ✗ Error publishing media: {e}")
            return None
    
    def post_to_instagram(self, image_url: str, caption: str) -> bool:
        """Post an image with caption to Instagram using Meta Graph API.
        
        This is a two-step process:
        1. Create a media container with image_url and caption
        2. Publish the container to make it live
        
        Args:
            image_url: URL of the image to post (must be publicly accessible)
            caption: Caption text for the post (max 2,200 characters)
            
        Returns:
            True if post was successful, False otherwise
        """
        try:
            # Validate inputs
            if not image_url or not isinstance(image_url, str):
                print("[Poster] ✗ Invalid image_url provided")
                return False
            
            if not caption or not isinstance(caption, str):
                print("[Poster] ✗ Invalid caption provided")
                return False
            
            # Step 1: Create media container
            creation_id = self._create_media_container(image_url, caption)
            
            if not creation_id:
                print("[Poster] ✗ Failed to create media container, aborting")
                return False
            
            # Step 2: Publish media container
            publish_result = self._publish_media_container(creation_id)
            
            if not publish_result:
                print("[Poster] ✗ Failed to publish media container")
                return False
            
            # Success!
            media_id = publish_result['media_id']
            post_url = f"https://www.instagram.com/p/{media_id}/"
            
            print(f"[Poster] ✓ Post published successfully!")
            print(f"[Poster] 📱 View post: {post_url}")
            
            return True
            
        except Exception as e:
            print(f"[Poster] ✗ Unexpected error during posting: {e}")
            return False

    # ------------------------------------------------------------------
    # Carousel posting
    # ------------------------------------------------------------------

    def _create_carousel_item(self, image_url: str) -> Optional[str]:
        """Create a single carousel-item media container.

        Args:
            image_url: Public URL of the image for this slide

        Returns:
            creation_id string if successful, None otherwise
        """
        try:
            url = f"{self.GRAPH_API_BASE}/{self.account_id}/media"
            payload = {
                "image_url":        image_url,
                "is_carousel_item": "true",
                "access_token":     self.access_token,
            }
            response = requests.post(url, data=payload, timeout=30)
            if response.status_code == 200:
                creation_id = response.json().get("id")
                print(f"[Poster] ✓ Carousel item created: {creation_id}")
                return creation_id
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
            print(f"[Poster] ✗ Carousel item failed: {error_msg}")
            return None
        except Exception as e:
            print(f"[Poster] ✗ Error creating carousel item: {e}")
            return None

    def _wait_for_media_ready(
        self,
        media_id: str,
        max_wait_seconds: int = 90,
        poll_interval: int = 5,
    ) -> bool:
        """Poll the Graph API until a media container reaches FINISHED status.

        Instagram processes uploaded images asynchronously. Attempting to publish
        before processing completes causes a 400 "Media ID is not available" error.

        Args:
            media_id:         The container ID to poll.
            max_wait_seconds: Abort after this many seconds (default 90).
            poll_interval:    Seconds between status checks (default 5).

        Returns:
            True if the container is FINISHED, False on timeout or error.
        """
        url = f"{self.GRAPH_API_BASE}/{media_id}"
        params = {
            "fields": "status_code,status",
            "access_token": self.access_token,
        }
        deadline = time.time() + max_wait_seconds
        while time.time() < deadline:
            try:
                resp = requests.get(url, params=params, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get("status_code", data.get("status", ""))
                    print(f"[Poster] Media {media_id} status: {status}")
                    if status == "FINISHED":
                        return True
                    if status in ("ERROR", "EXPIRED"):
                        print(f"[Poster] ✗ Media {media_id} entered terminal error state: {status}")
                        return False
                else:
                    print(f"[Poster] ⚠ Status check HTTP {resp.status_code} for {media_id}")
            except Exception as e:
                print(f"[Poster] ⚠ Status poll error: {e}")
            time.sleep(poll_interval)
        print(f"[Poster] ✗ Timed out waiting for media {media_id} to be ready")
        return False

    def _create_carousel_container(
        self, children_ids: List[str], caption: str
    ) -> Optional[str]:
        """Create a carousel (album) media container referencing child IDs.

        Args:
            children_ids: List of media container IDs (from _create_carousel_item)
            caption:      Caption text for the post

        Returns:
            carousel container creation_id if successful, None otherwise
        """
        try:
            url = f"{self.GRAPH_API_BASE}/{self.account_id}/media"
            payload = {
                "media_type":   "CAROUSEL",
                "children":     ",".join(children_ids),
                "caption":      caption,
                "access_token": self.access_token,
            }
            response = requests.post(url, data=payload, timeout=30)
            if response.status_code == 200:
                creation_id = response.json().get("id")
                print(f"[Poster] ✓ Carousel container created: {creation_id}")
                return creation_id
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
            print(f"[Poster] ✗ Carousel container failed: {error_msg}")
            return None
        except Exception as e:
            print(f"[Poster] ✗ Error creating carousel container: {e}")
            return None

    def post_carousel_to_instagram(
        self, image_urls: List[str], caption: str
    ) -> bool:
        """Post a carousel (multiple-image) post to Instagram.

        Flow:
        1. Create a carousel-item container for every image URL
        2. Create a parent carousel container with all child IDs
        3. Publish the carousel container

        Falls back to single-image post if:
        - Only 1 URL is provided
        - Carousel container creation fails
        - Fewer than 2 items are successfully created

        Instagram requires 2–10 images per carousel.

        Args:
            image_urls: List of public image URLs [cover, slide2, ...]
            caption:    Caption for the post

        Returns:
            True if published successfully, False otherwise
        """
        if not image_urls:
            print("[Poster] ✗ No image URLs provided")
            return False

        # Single-image fallback
        if len(image_urls) == 1:
            print("[Poster] Only 1 image — posting as single photo")
            return self.post_to_instagram(image_urls[0], caption)

        # Enforce Instagram's 10-slide carousel limit
        image_urls = image_urls[:10]
        print(f"[Poster] Building carousel with {len(image_urls)} slides...")

        # Step 1: Create carousel item containers
        children_ids = []
        for i, img_url in enumerate(image_urls):
            print(f"[Poster] Creating item {i + 1}/{len(image_urls)}...")
            cid = self._create_carousel_item(img_url)
            if cid:
                children_ids.append(cid)
            else:
                print(f"[Poster] ⚠ Slide {i + 1} skipped (upload/container error)")
            # Brief pause to respect API rate limits
            time.sleep(0.5)

        if len(children_ids) < 2:
            print("[Poster] ✗ Not enough carousel items — falling back to single photo")
            return self.post_to_instagram(image_urls[0], caption)

        # Step 1b: Wait for ALL child items to finish processing.
        # Instagram processes images asynchronously. Publishing before each child
        # reaches FINISHED status causes: 400 "Media ID is not available".
        print(f"[Poster] Waiting for {len(children_ids)} carousel items to finish processing...")
        all_ready = True
        for cid in children_ids:
            if not self._wait_for_media_ready(cid):
                print(f"[Poster] ⚠ Item {cid} did not reach FINISHED — skipping it")
                all_ready = False

        if not all_ready:
            # Re-filter to only confirmed-ready IDs
            ready_ids = []
            for cid in children_ids:
                url = f"{self.GRAPH_API_BASE}/{cid}"
                try:
                    r = requests.get(url, params={"fields": "status_code", "access_token": self.access_token}, timeout=10)
                    if r.status_code == 200 and r.json().get("status_code") == "FINISHED":
                        ready_ids.append(cid)
                except Exception:
                    pass
            if len(ready_ids) < 2:
                print("[Poster] ✗ Too few items ready — falling back to single photo")
                return self.post_to_instagram(image_urls[0], caption)
            children_ids = ready_ids

        # Step 2: Create parent carousel container
        carousel_id = self._create_carousel_container(children_ids, caption)
        if not carousel_id:
            print("[Poster] ✗ Carousel container failed — falling back to single photo")
            return self.post_to_instagram(image_urls[0], caption)

        # Step 2b: Wait for the carousel container itself to be ready
        print(f"[Poster] Waiting for carousel container {carousel_id} to be ready...")
        if not self._wait_for_media_ready(carousel_id):
            print("[Poster] ✗ Carousel container not ready in time — aborting")
            return False

        # Step 3: Publish
        result = self._publish_media_container(carousel_id)
        if result:
            media_id = result["media_id"]
            print(f"[Poster] ✓ Carousel published! Slides: {len(children_ids)}")
            print(f"[Poster] 📱 View post: https://www.instagram.com/p/{media_id}/")
            return True

        print("[Poster] ✗ Carousel publish failed")
        return False


def main():
    """Test the InstagramPoster with dummy data."""
    print("=" * 70)
    print("POSTER TEST - Instagram Meta Graph API")
    print("=" * 70)
    
    try:
        poster = InstagramPoster()
        
        # Test 1: Check token validity
        print("\n" + "-" * 70)
        print("TEST 1: Validate Access Token")
        print("-" * 70)
        
        if poster.check_token_valid():
            print("✓ Token validation passed\n")
        else:
            print("✗ Token validation failed")
            print("Please ensure INSTAGRAM_ACCOUNT_ID and INSTAGRAM_ACCESS_TOKEN are correct in .env\n")
            return False
        
        # Test 2: Check token expiry
        print("-" * 70)
        print("TEST 2: Check Token Expiry")
        print("-" * 70)
        
        days_remaining = poster.get_token_expiry_days()
        if days_remaining is not None:
            if days_remaining < 7:
                print(f"⚠ Token expires in {days_remaining} days - consider refreshing soon\n")
            else:
                print(f"✓ Token has {days_remaining} days remaining\n")
        else:
            print("⚠ Unable to determine token expiry\n")
        
        # Test 3: Refresh token (optional)
        print("-" * 70)
        print("TEST 3: Refresh Token (Optional)")
        print("-" * 70)
        
        if poster.client_id and poster.client_secret:
            print("Attempting to refresh token...\n")
            if poster.refresh_access_token():
                print("✓ Token refresh successful\n")
            else:
                print("⚠ Token refresh failed (this may be normal if token is new)\n")
        else:
            print("⚠ Skipping token refresh - FACEBOOK_APP_ID or FACEBOOK_APP_SECRET not set\n")
            print("To enable token refresh, add these to your .env:")
            print("  FACEBOOK_APP_ID=your_app_id")
            print("  FACEBOOK_APP_SECRET=your_app_secret\n")
        
        # Test 4: Post dummy content
        print("-" * 70)
        print("TEST 4: Post to Instagram (Dry Run)")
        print("-" * 70)
        
        dummy_image_url = "https://via.placeholder.com/1080x1350.png?text=AI+Tech"
        dummy_caption = """🚀 The Future of AI is Here!

Just discovered this breakthrough in AI technology. This could change everything we know about machine learning.

Check out more tech insights on our page! 🤖

#AI #Technology #MachineLearning #GPT #Innovation #FutureTech #ArtificialIntelligence"""
        
        print(f"\nDummy Image URL: {dummy_image_url}")
        print(f"Dummy Caption: {dummy_caption[:80]}...\n")
        
        success = poster.post_to_instagram(dummy_image_url, dummy_caption)
        
        if success:
            print("\n✓ PASS: Post was successful")
        else:
            print("\n⚠ Post failed - this is expected if using placeholder image URL")
            print("In production, use real image URLs from Pollinations.ai")
        
        print("\n" + "=" * 70 + "\n")
        return True
        
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nSetup required:")
        print("1. Convert Instagram account to Creator/Business account")
        print("2. Create a Facebook App on developers.facebook.com")
        print("3. Get long-lived access token from Meta")
        print("4. Add INSTAGRAM_ACCOUNT_ID and INSTAGRAM_ACCESS_TOKEN to .env\n")
        return False
    except Exception as e:
        print(f"\n✗ Error during test: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
