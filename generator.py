import google.generativeai as genai
import requests
import os
from typing import Tuple
from PIL import Image
from io import BytesIO

class ContentGenerator:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.pollinations_api_key = os.getenv('POLLINATIONS_API_KEY')
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
    
    def generate_caption(self, article_title: str, article_summary: str) -> str:
        """Generate an Instagram caption using Gemini API."""
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""Create a short, engaging Instagram caption for a tech/AI news post.
            
Title: {article_title}
Summary: {article_summary}

Requirements:
- Maximum 300 characters
- Include 2-3 relevant hashtags
- Make it engaging and conversational
- End with a call-to-action or thought-provoking question

Caption:"""
            
            response = model.generate_content(prompt)
            caption = response.text.strip()
            print(f"[Generator] Caption generated: {caption[:50]}...")
            return caption
        except Exception as e:
            print(f"[Generator] Error generating caption: {e}")
            return f"Check out this tech news: {article_title[:100]} #tech #ai"
    
    def generate_image(self, article_title: str) -> str:
        """Generate an image using Pollinations API."""
        try:
            # Using Pollinations.ai free tier
            prompt = f"Professional tech/AI illustration for: {article_title[:100]}"
            
            # Pollinations.ai endpoint
            api_url = "https://api.pollinations.ai/v1/images/generations"
            
            response = requests.post(
                api_url,
                json={
                    "prompt": prompt,
                    "width": 1080,
                    "height": 1350,
                    "seed": hash(article_title) % 10000
                }
            )
            
            if response.status_code == 200:
                image_url = response.json().get('url')
                print(f"[Generator] Image generated: {image_url}")
                return image_url
            else:
                print(f"[Generator] Error generating image: {response.status_code}")
                return None
        except Exception as e:
            print(f"[Generator] Error with image generation: {e}")
            return None
    
    def generate_content(self, article: dict) -> Tuple[str, str]:
        """Generate both caption and image for an article."""
        caption = self.generate_caption(article['title'], article['summary'])
        image_url = self.generate_image(article['title'])
        return caption, image_url
