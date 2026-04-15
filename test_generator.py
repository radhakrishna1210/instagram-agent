import sys
from generator import ContentGenerator
from dotenv import load_dotenv

load_dotenv()

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def test_generator():
    gen = ContentGenerator()

    dummy_article = {
        "title": "OpenAI releases GPT-5 with advanced reasoning",
        "summary": "OpenAI has announced GPT-5, featuring dramatically improved reasoning capabilities and multimodal understanding.",
        "url": "https://example.com/gpt5",
        "source": "TechCrunch",
    }

    print("Testing generate_caption()...")
    caption = gen.generate_caption(dummy_article)
    assert len(caption) > 20, "Caption too short"
    print(f"Caption:\n{caption}\n")

    print("Testing generate_image_url()...")
    url = gen.generate_image_url(dummy_article)
    assert url.startswith("https://image.pollinations.ai"), "Wrong URL"
    assert "1080" in url, "Wrong dimensions"
    print(f"Image URL:\n{url}\n")

    print("Testing generate_content()...")
    content = gen.generate_content(dummy_article)
    assert "caption" in content, "Missing caption key"
    assert "image_url" in content, "Missing image_url key"
    print("All tests PASSED")


if __name__ == "__main__":
    test_generator()
