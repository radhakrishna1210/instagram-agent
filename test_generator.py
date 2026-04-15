"""
Test script for generator.py
Tests caption and image generation functions.
"""

from generator import ContentGenerator


def test_generator():
    """Test the ContentGenerator with dummy article data."""
    print("=" * 70)
    print("GENERATOR TEST - Caption & Image Generation")
    print("=" * 70)
    
    try:
        generator = ContentGenerator()
        
        # Create dummy article dict
        dummy_article = {
            'title': 'OpenAI Announces GPT-5: Revolutionary Multimodal AI Model',
            'summary': 'OpenAI has unveiled GPT-5, featuring advanced reasoning capabilities, improved context handling up to 1 million tokens, and breakthrough performance in code generation and scientific problem-solving.',
            'url': 'https://example.com/openai-gpt5',
            'source': 'techcrunch'
        }
        
        print(f"\nDummy Article:")
        print(f"  Title: {dummy_article['title']}")
        print(f"  Summary: {dummy_article['summary'][:80]}...\n")
        
        # Test 1: Generate Caption
        print("-" * 70)
        print("TEST 1: Generate Caption")
        print("-" * 70)
        
        caption = generator.generate_caption(dummy_article)
        
        if caption:
            print(f"\n✓ Caption Generated ({len(caption)} chars):")
            print(f"\n{caption}\n")
            caption_pass = True
        else:
            print("\n✗ Failed to generate caption\n")
            caption_pass = False
        
        # Test 2: Generate Image URL
        print("-" * 70)
        print("TEST 2: Generate Image URL")
        print("-" * 70)
        
        image_url = generator.generate_image_url(dummy_article['title'])
        
        if image_url:
            print(f"\n✓ Image URL Generated:")
            print(f"{image_url}\n")
            
            # Verify URL format
            if image_url.startswith('https://image.pollinations.ai'):
                print("✓ URL format is correct (starts with https://image.pollinations.ai)")
                image_pass = True
            else:
                print("✗ URL format is incorrect (does not start with https://image.pollinations.ai)")
                image_pass = False
        else:
            print("\n✗ Failed to generate image URL\n")
            image_pass = False
        
        # Final Result
        print("\n" + "=" * 70)
        if caption_pass and image_pass:
            print("✓ PASS: All tests passed")
            result = True
        else:
            print("✗ FAIL: One or more tests failed")
            if not caption_pass:
                print("  - Caption generation failed")
            if not image_pass:
                print("  - Image URL generation failed")
            result = False
        
        print("=" * 70 + "\n")
        return result
        
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("Ensure GEMINI_API_KEY is set in your .env file\n")
        return False
    except Exception as e:
        print(f"\n✗ Error during test: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_generator()
    exit(0 if success else 1)
