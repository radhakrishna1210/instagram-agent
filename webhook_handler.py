"""
Typeform Webhook Handler for Instagram Agent
Listens for form submissions and posts custom content to Instagram
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict
from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn

# Load environment variables
load_dotenv()

# Import our modules
from generator import ContentGenerator
from poster import InstagramPoster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Instagram Agent Webhook",
    description="Receives Typeform submissions and posts to Instagram",
    version="1.0.0"
)

# Webhook secret for validation (optional but recommended)
WEBHOOK_SECRET = os.getenv('TYPEFORM_WEBHOOK_SECRET', '')


def post_from_webhook(topic: str, custom_text: str) -> bool:
    """Post to Instagram using custom content from webhook.
    
    Args:
        topic: Topic/title for the post
        custom_text: Custom text/description for the post
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"[Webhook] Processing submission: {topic}")

        class Payload:
            def __init__(self, topic_value: str, custom_text_value: str):
                self.topic = topic_value
                self.custom_text = custom_text_value

        payload = Payload(topic, custom_text)

        # Create custom article dict from webhook data
        article = {
            "title": payload.topic,
            "summary": payload.custom_text,
            "url": "https://manual-post.local",
            "source": "Manual/Typeform"
        }

        logger.info(f"[Webhook] Generated article dict: {article['title']}")

        # Generate caption and image using Gemini + Pollinations URL
        logger.info(f"[Webhook] Generating caption and image...")
        generator = ContentGenerator()
        content = generator.generate_content(article)
        caption = content["caption"]
        image_url = content["image_url"]
        
        if not caption:
            logger.error("[Webhook] Failed to generate caption")
            return False

        logger.info(f"[Webhook] Caption generated: {caption[:60]}...")

        if not image_url:
            logger.error("[Webhook] Failed to generate image")
            return False

        logger.info(f"[Webhook] Image generated: {image_url[:60]}...")
        
        # Post to Instagram
        logger.info(f"[Webhook] Posting to Instagram...")
        poster = InstagramPoster()
        
        if not poster.check_token_valid():
            logger.error("[Webhook] Instagram token validation failed")
            return False
        
        success = poster.post_to_instagram(image_url, caption)
        
        if success:
            logger.info(f"[Webhook] ✓ Successfully posted!")
            return True
        else:
            logger.error("[Webhook] Failed to post to Instagram")
            return False
            
    except Exception as e:
        logger.error(f"[Webhook] Error processing submission: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Instagram Agent Webhook Handler",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health():
    """Health check for monitoring."""
    try:
        # Verify we can initialize modules
        generator = ContentGenerator()
        poster = InstagramPoster()
        
        return {
            "status": "healthy",
            "generator": "ok",
            "poster": "ok",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, 503


@app.post("/webhook/typeform")
async def handle_typeform_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle incoming Typeform webhook submissions.
    
    Expected JSON structure:
    {
        "form_response": {
            "answers": [
                {"field": {"ref": "topic"}, "text": "My Topic"},
                {"field": {"ref": "custom_text"}, "text": "My custom description"}
            ]
        }
    }
    
    Also accepts simplified format:
    {
        "topic": "My Topic",
        "custom_text": "My custom description"
    }
    """
    try:
        body = await request.json()
        logger.info(f"[Webhook] Received POST request: {str(body)[:200]}...")
        
        # Extract topic and custom_text from request
        topic = None
        custom_text = None
        
        # Format 1: Typeform's native format
        if 'form_response' in body and 'answers' in body['form_response']:
            answers = body['form_response']['answers']
            for answer in answers:
                field_ref = answer.get('field', {}).get('ref', '')
                text = answer.get('text', '')
                
                if field_ref == 'topic':
                    topic = text
                elif field_ref == 'custom_text':
                    custom_text = text
        
        # Format 2: Simplified format
        elif 'topic' in body and 'custom_text' in body:
            topic = body['topic']
            custom_text = body['custom_text']
        
        # Validate we have required fields
        if not topic or not custom_text:
            logger.warning(f"[Webhook] Missing required fields. Topic: {topic}, Text: {custom_text}")
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: 'topic' and 'custom_text'"
            )
        
        logger.info(f"[Webhook] Extracted - Topic: {topic}")
        logger.info(f"[Webhook] Extracted - Text: {custom_text[:80]}...")
        
        # Run posting in background to respond immediately
        background_tasks.add_task(post_from_webhook, topic, custom_text)
        
        return JSONResponse(
            status_code=202,
            content={
                "status": "accepted",
                "message": "Submission received and queued for processing",
                "topic": topic,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Webhook] Error handling request: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/manual")
async def handle_manual_post(
    background_tasks: BackgroundTasks,
    topic: str,
    custom_text: str
):
    """Manual POST endpoint for testing (URL parameters).
    
    Example:
    curl -X POST "http://localhost:8000/webhook/manual?topic=AI+News&custom_text=Check+this+out"
    """
    if not topic or not custom_text:
        raise HTTPException(status_code=400, detail="Missing 'topic' or 'custom_text'")
    
    logger.info(f"[Webhook] Manual post received - Topic: {topic}")
    
    background_tasks.add_task(post_from_webhook, topic, custom_text)
    
    return JSONResponse(
        status_code=202,
        content={
            "status": "accepted",
            "message": "Manual submission queued for processing",
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.get("/docs")
async def docs():
    """API documentation."""
    return {
        "title": "Instagram Agent Webhook API",
        "endpoints": {
            "/": "Health check",
            "/health": "Detailed health check",
            "POST /webhook/typeform": "Typeform webhook handler (JSON)",
            "POST /webhook/manual": "Manual post handler (URL params)",
            "/docs": "This documentation"
        },
        "example_typeform_payload": {
            "form_response": {
                "answers": [
                    {"field": {"ref": "topic"}, "text": "Latest AI Breakthrough"},
                    {"field": {"ref": "custom_text"}, "text": "Scientists announce new AI model"}
                ]
            }
        },
        "example_manual_request": "POST /webhook/manual?topic=Test&custom_text=This+is+a+test",
        "environment_variables": [
            "GEMINI_API_KEY",
            "INSTAGRAM_ACCOUNT_ID",
            "INSTAGRAM_ACCESS_TOKEN",
            "TYPEFORM_WEBHOOK_SECRET (optional)"
        ]
    }


def main():
    """Start the FastAPI server."""
    print("\n" + "=" * 70)
    print("Instagram Agent - Typeform Webhook Handler")
    print("=" * 70 + "\n")
    
    # Validate environment
    required_vars = ['GEMINI_API_KEY', 'INSTAGRAM_ACCOUNT_ID', 'INSTAGRAM_ACCESS_TOKEN']
    missing = [var for var in required_vars if not os.getenv(var) or os.getenv(var).endswith('_here')]
    
    if missing:
        print(f"✗ Missing environment variables: {', '.join(missing)}")
        print("Please ensure all required .env variables are set")
        return
    
    print("✓ Environment validated")
    print("\n" + "-" * 70)
    print("API Endpoints:")
    print("-" * 70)
    print("  GET  http://localhost:8000/")
    print("  GET  http://localhost:8000/health")
    print("  GET  http://localhost:8000/docs")
    print("  POST http://localhost:8000/webhook/typeform")
    print("  POST http://localhost:8000/webhook/manual?topic=...&custom_text=...")
    print("-" * 70 + "\n")
    
    print("Typeform Setup:")
    print("1. Go to your Typeform form settings")
    print("2. Click 'Integrations' → 'Webhooks'")
    print("3. Add webhook URL: https://your-railway-url.up.railway.app/webhook/typeform")
    print("4. Or locally: http://localhost:8000/webhook/typeform")
    print("5. Select fields: topic, custom_text")
    print("6. Save webhook\n")
    
    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == '__main__':
    main()
