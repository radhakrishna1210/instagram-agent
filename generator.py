import base64
import io
import os
import re
import random
import textwrap
from urllib.parse import quote

import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class ContentGenerator:
    CAPTION_PROMPT = (
        "You are an Instagram content creator for a developer-focused AI niche page "
        "with 100k+ followers. Write a high-value Instagram caption for this "
        "software engineering news article. Rules: Start with a powerful hook "
        "(mentioning coding agents, LLMs, or dev tools). Use 3-5 short punchy "
        "sentences explained from a developer's perspective. Be conversational "
        "and insightful. End with a CTA (e.g., 'Would you use this in your workflow?'). "
        "Do NOT include any hashtags. Keep total under 200 words."
    )

    HASHTAG_PROMPT = (
        "You are a viral growth expert for developer communities on Instagram. "
        "Generate exactly 30 hashtags for an article about AI in coding/SWE. "
        "Include: #softwareengineering #coding #ai #llm #developer #python "
        "#javascript #codingagents #automation #devtools #github #copilot "
        "and other trending tags for this niche. Output ONLY the hashtags on one line."
    )

    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)

    # ------------------------------------------------------------------
    # Caption
    # ------------------------------------------------------------------

    def generate_caption(self, article: dict) -> str:
        """Generate an Instagram caption + 30 viral hashtags for a news article."""
        title   = article["title"]
        summary = article["summary"]
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")

            # ── Caption body (no hashtags) ──────────────────────────────────
            caption_prompt = (
                f"{self.CAPTION_PROMPT}\n\n"
                f"Article title: {title}\n"
                f"Article summary: {summary}\n"
                f"Source: {article.get('source', 'Unknown')}\n"
                "Return only the final caption text. No hashtags."
            )
            caption_resp = model.generate_content(caption_prompt)
            caption_body = (caption_resp.text or "").strip()

            # ── Hashtags (30 viral, topic-specific) ────────────────────────
            hashtag_prompt = (
                f"{self.HASHTAG_PROMPT}\n\n"
                f"Article title: {title}\n"
                f"Article summary: {summary[:400]}\n"
                "Return ONLY the 30 hashtags on one line."
            )
            hashtag_resp = model.generate_content(hashtag_prompt)
            raw_tags = (hashtag_resp.text or "").strip()

            # Sanitise: keep only tokens that start with #
            tags = [t for t in raw_tags.split() if t.startswith("#")]
            # Enforce Instagram's 30-hashtag limit
            tags = tags[:30]
            hashtag_line = " ".join(tags)

            if caption_body and hashtag_line:
                full_caption = f"{caption_body}\n\n{hashtag_line}"
                print(f"[Generator] ✓ Caption: {len(caption_body)} chars, {len(tags)} hashtags")
                return full_caption

            raise ValueError("Gemini returned empty caption or hashtags")

        except Exception as e:
            print(f"[Generator] Error generating caption: {e}")
            return (
                f"Exciting developments in AI! {title} "
                "#AI #Tech #ArtificialIntelligence #MachineLearning "
                "#Innovation #Future #TechNews #AINews #DeepLearning "
                "#DataScience #Automation #DigitalTransformation "
                "#EmergingTech #FutureTech #TechInnovation "
                "#AIRevolution #SmartTech #TechTrends #AITools "
                "#MachineIntelligence #AIUpdates #TechWorld "
                "#GenerativeAI #LargeLanguageModels #NeuralNetworks "
                "#AIResearch #ComputerScience #BigData #CloudAI #GenAI"
            )

    # ------------------------------------------------------------------
    # Image prompt (Gemini → article-relevant visual description)
    # ------------------------------------------------------------------

    def _generate_image_prompt(self, article: dict) -> str:
        """Ask Gemini for a specific image prompt based on the article content."""
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = (
                "Write a short Stable Diffusion image prompt (max 20 words) that visually "
                "represents this tech news article. Focus on the core concept or technology. "
                "Style: photorealistic OR cinematic digital art, 4k, no text, no watermark.\n\n"
                f"Title: {article['title']}\n"
                f"Summary: {article.get('summary', '')[:300]}\n"
                "Return ONLY the image prompt, nothing else."
            )
            response = model.generate_content(prompt)
            result = (response.text or "").strip()
            if result:
                print(f"[Generator] Image prompt: {result}")
                return result
        except Exception as e:
            print(f"[Generator] Gemini image prompt failed: {e}")
        # Fallback: derive a simple prompt from the title
        return f"{article['title']}, cinematic digital art, 4k, tech aesthetic"

    def generate_image_url(self, article: dict) -> str:
        """Build a Pollinations URL using an article-relevant image prompt."""
        topic_prompt = self._generate_image_prompt(article)
        full_prompt = f"{topic_prompt}, no text, no watermark, no logo"
        encoded = quote(full_prompt)
        seed = random.randint(1, 9999)
        return (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=1080&height=1080&nologo=true&seed={seed}"
        )

    # ------------------------------------------------------------------
    # Image hosting
    # ------------------------------------------------------------------

    def _upload_image(self, buf: io.BytesIO) -> str | None:
        """Upload image bytes to Cloudinary and return a public URL."""
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key    = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")
        if not all([cloud_name, api_key, api_secret]):
            print("[Generator] Cloudinary credentials not set — skipping upload")
            return None
        try:
            import time, hashlib
            timestamp = str(int(time.time()))
            signature_str = f"timestamp={timestamp}{api_secret}"
            signature = hashlib.sha1(signature_str.encode()).hexdigest()

            buf.seek(0)
            resp = requests.post(
                f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload",
                data={
                    "api_key":   api_key,
                    "timestamp": timestamp,
                    "signature": signature,
                },
                files={"file": ("image.jpg", buf, "image/jpeg")},
                timeout=60,
            )
            resp.raise_for_status()
            url = resp.json()["secure_url"]
            return url
        except Exception as e:
            print(f"[Generator] Cloudinary upload failed: {e}")
            return None

    # ------------------------------------------------------------------
    # Designed fallback graphic (no external download needed)
    # ------------------------------------------------------------------

    def _make_designed_image(self, article: dict) -> "Image.Image":
        """Create a fully designed 1080x1080 graphic using Pillow."""
        from PIL import Image, ImageDraw, ImageFont

        w, h = 1080, 1080
        img = Image.new("RGB", (w, h), (10, 10, 30))
        draw = ImageDraw.Draw(img)

        # Background gradient (dark navy → dark purple)
        for y in range(h):
            r = int(10 + 30 * y / h)
            g = int(10 + 5  * y / h)
            b = int(30 + 60 * y / h)
            draw.line([(0, y), (w, y)], fill=(r, g, b))

        # Decorative diagonal lines
        for i in range(0, w, 120):
            draw.line([(i, 0), (i + 300, h)], fill=(255, 255, 255, 15), width=1)
        draw.rectangle([(0, 0), (w, 8)],     fill=(30, 144, 255))
        draw.rectangle([(0, h - 8), (w, h)], fill=(30, 144, 255))

        # Fonts
        font_pairs = [
            ("C:/Windows/Fonts/arialbd.ttf",  "C:/Windows/Fonts/arial.ttf"),
            ("C:/Windows/Fonts/calibrib.ttf", "C:/Windows/Fonts/calibri.ttf"),
            ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
        bold_font = small_font = tag_font = None
        for bold_path, reg_path in font_pairs:
            try:
                bold_font  = ImageFont.truetype(bold_path, 58)
                small_font = ImageFont.truetype(reg_path,  30)
                tag_font   = ImageFont.truetype(bold_path, 30)
                break
            except OSError:
                continue
        if bold_font is None:
            bold_font = small_font = tag_font = ImageFont.load_default()

        # "AI & TECH" pill at top
        draw.rounded_rectangle([(40, 30), (200, 72)], radius=10, fill=(30, 144, 255))
        draw.text((55, 38), "AI & TECH", fill=(255, 255, 255), font=tag_font)

        # Headline centered in the middle
        title = article.get("title", "")
        lines = textwrap.wrap(title, width=24)[:4]
        line_h = 72
        total_h = len(lines) * line_h
        y = (h - total_h) // 2 - 40

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=bold_font)
            tw = bbox[2] - bbox[0]
            x = (w - tw) // 2
            draw.text((x + 3, y + 3), line, fill=(0, 0, 80),     font=bold_font)  # shadow
            draw.text((x,     y),     line, fill=(255, 255, 255), font=bold_font)
            y += line_h

        # Divider line
        draw.rectangle([(w // 2 - 80, y + 20), (w // 2 + 80, y + 24)], fill=(30, 144, 255))

        # Source at bottom
        source = article.get("source", "").replace("_", " ").title()
        src_text = f"Source: {source}"
        bbox = draw.textbbox((0, 0), src_text, font=small_font)
        sw = bbox[2] - bbox[0]
        draw.text(((w - sw) // 2, h - 70), src_text, fill=(160, 200, 255), font=small_font)

        return img

    # ------------------------------------------------------------------
    # Text overlay on downloaded Pollinations image
    # ------------------------------------------------------------------

    def _create_image_with_text(self, base_url: str, article: dict) -> str:
        """Download base image, overlay headline + source, upload, return URL."""
        try:
            from PIL import Image, ImageDraw, ImageFont

            print("[Generator] Downloading base image...")
            resp = requests.get(base_url, timeout=90)
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
            w, h = img.size

            # Dark gradient on bottom half for legibility
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            ov_draw = ImageDraw.Draw(overlay)
            grad_start = h // 2
            for y in range(grad_start, h):
                alpha = int(220 * (y - grad_start) / (h - grad_start))
                ov_draw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
            img = Image.alpha_composite(img, overlay).convert("RGB")
            draw = ImageDraw.Draw(img)

            # Fonts
            font_size, small_size = 54, 28
            font_pairs = [
                ("C:/Windows/Fonts/arialbd.ttf",  "C:/Windows/Fonts/arial.ttf"),
                ("C:/Windows/Fonts/calibrib.ttf", "C:/Windows/Fonts/calibri.ttf"),
                ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]
            bold_font = small_font = None
            for bold_path, reg_path in font_pairs:
                try:
                    bold_font  = ImageFont.truetype(bold_path, font_size)
                    small_font = ImageFont.truetype(reg_path,  small_size)
                    break
                except OSError:
                    continue
            if bold_font is None:
                bold_font = small_font = ImageFont.load_default()

            # Wrap headline — max 3 lines of ~26 chars
            title = article.get("title", "")
            lines = textwrap.wrap(title, width=26)[:3]
            line_h = font_size + 16
            text_block_h = len(lines) * line_h
            y = h - text_block_h - 80

            # Blue accent bar on left edge
            draw.rectangle([(46, y), (53, y + text_block_h - 8)], fill=(30, 144, 255))

            # Headline with drop shadow
            for line in lines:
                draw.text((68, y + 3), line, fill=(0, 0, 0),       font=bold_font)  # shadow
                draw.text((66, y),     line, fill=(255, 255, 255),  font=bold_font)
                y += line_h

            # Source label at very bottom
            source = article.get("source", "").replace("_", " ").title()
            draw.text((50, h - 50), f"AI & Tech  •  {source}", fill=(160, 200, 255), font=small_font)

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=92)
            buf.seek(0)

            hosted = self._upload_image(buf)
            if hosted:
                print(f"[Generator] ✓ Image with text hosted: {hosted}")
                return hosted

        except Exception as e:
            print(f"[Generator] Pollinations overlay failed: {e}")

        # Fallback: build a fully designed graphic locally
        print("[Generator] Building designed graphic locally...")
        try:
            img = self._make_designed_image(article)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=92)
            buf.seek(0)

            hosted = self._upload_image(buf)
            if hosted:
                print(f"[Generator] ✓ Designed image hosted: {hosted}")
                return hosted
        except Exception as e2:
            print(f"[Generator] Designed image fallback also failed: {e2}")

        print("[Generator] Using plain Pollinations URL as last resort")
        return base_url

    # ------------------------------------------------------------------
    # Carousel helpers
    # ------------------------------------------------------------------

    def _split_caption_into_slides(self, caption: str) -> list:
        """Split caption into text segments for carousel slides.

        Hashtag lines are stripped entirely — hashtags belong only in
        the caption text sent to Instagram, not on any image slide.
        Returns a list of strings; each becomes one text slide.
        """
        lines = caption.strip().split("\n")
        content_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            words = stripped.split()
            # Skip pure hashtag lines
            if words and all(w.startswith("#") for w in words):
                continue
            content_lines.append(stripped)

        # Parse content into sentences
        content_text = " ".join(content_lines)
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", content_text) if s.strip()]

        slides = []

        if len(sentences) <= 2:
            # Short caption — one text slide
            slides.append("\n\n".join(sentences))
        elif len(sentences) <= 5:
            # Medium — two content slides
            mid = len(sentences) // 2
            slides.append("\n\n".join(sentences[:mid]))
            slides.append("\n\n".join(sentences[mid:]))
        else:
            # Long — three content slides
            chunk = len(sentences) // 3
            slides.append("\n\n".join(sentences[:chunk]))
            slides.append("\n\n".join(sentences[chunk:chunk * 2]))
            slides.append("\n\n".join(sentences[chunk * 2:]))

        return slides

    def _make_text_slide(
        self,
        text: str,
        slide_num: int,
        total_slides: int,
        article: dict,
        bg_url: str = None,
    ) -> "Image.Image":
        """Create a 1080×1080 text slide with a relevant background image.

        Downloads bg_url (a topic-relevant Pollinations image), applies a
        strong dark overlay for readability, then draws bullet-point text
        on top.  Falls back to a charcoal gradient if the download fails.

        Args:
            text:         Text body for this slide (sentences separated by \n\n)
            slide_num:    Current slide number (1-indexed, slide 1 = cover)
            total_slides: Total number of slides in the carousel
            article:      Article dict (used for source label)
            bg_url:       Pollinations image URL to use as background
        """
        from PIL import Image, ImageDraw, ImageFont

        ACCENT   = (30, 144, 255)    # dodger blue
        BG_DARK  = (10, 14, 20)      # fallback solid bg
        TXT_MAIN = (245, 245, 245)   # bright white
        TXT_DIM  = (120, 160, 210)   # muted blue-grey for labels

        w, h = 1080, 1080

        # ── 1. Background ────────────────────────────────────────────────
        if bg_url:
            try:
                resp = requests.get(bg_url, timeout=90)
                resp.raise_for_status()
                base = Image.open(io.BytesIO(resp.content)).convert("RGBA")
                base = base.resize((w, h), Image.LANCZOS)
                print(f"[Generator] BG image loaded for slide {slide_num}")
            except Exception as e:
                print(f"[Generator] BG download failed ({e}) — using gradient")
                base = None
        else:
            base = None

        if base is None:
            # Charcoal gradient fallback
            base = Image.new("RGBA", (w, h), BG_DARK)
            base_draw = ImageDraw.Draw(base)
            for y in range(h):
                t = y / h
                r = int(10 + 8 * t)
                g = int(14 + 7 * t)
                b = int(20 + 18 * t)
                base_draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

        # ── 2. Dark overlay (65 % black) for text legibility ─────────────
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 166))
        img = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

        # ── 3. Accent bars ────────────────────────────────────────────────
        draw.rectangle([(0, 0),     (w, 5)],  fill=ACCENT)
        draw.rectangle([(0, h - 5), (w, h)],  fill=ACCENT)

        # ── 4. Fonts ──────────────────────────────────────────────────────
        font_pairs = [
            ("C:/Windows/Fonts/arialbd.ttf",  "C:/Windows/Fonts/arial.ttf"),
            ("C:/Windows/Fonts/calibrib.ttf", "C:/Windows/Fonts/calibri.ttf"),
            ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
        bold_font = body_font = small_font = tag_font = None
        for bold_path, reg_path in font_pairs:
            try:
                bold_font  = ImageFont.truetype(bold_path, 44)
                body_font  = ImageFont.truetype(reg_path,  36)
                small_font = ImageFont.truetype(reg_path,  24)
                tag_font   = ImageFont.truetype(bold_path, 26)
                break
            except OSError:
                continue
        if bold_font is None:
            bold_font = body_font = small_font = tag_font = ImageFont.load_default()

        # ── 5. "AI & TECH" pill ───────────────────────────────────────────
        draw.rounded_rectangle([(40, 28), (195, 68)], radius=10, fill=ACCENT)
        draw.text((56, 35), "AI & TECH", fill=(255, 255, 255), font=tag_font)

        # ── 6. Left accent bar ────────────────────────────────────────────
        draw.rectangle([(44, 110), (50, h - 100)], fill=(30, 144, 255, 80))

        # ── 7. Bullet-point text ──────────────────────────────────────────
        raw_points = [
            p.strip()
            for p in re.split(r"[\n]+|(?<=[.!?])\s+", text)
            if p.strip()
        ]
        points = raw_points[:6]  # cap at 6 bullets

        y        = 120
        bullet_x = 70
        text_x   = 112
        line_h   = 50
        gap      = 20   # space between bullet points

        for point in points:
            # Blue bullet dot
            draw.ellipse(
                [(bullet_x, y + 14), (bullet_x + 12, y + 26)],
                fill=ACCENT,
            )

            # Wrapped text
            wrapped = textwrap.wrap(point, width=28)
            for wline in wrapped[:3]:
                draw.text((text_x, y), wline, fill=TXT_MAIN, font=body_font)
                y += line_h

            y += gap

            if y > h - 140:
                break

        # ── 8. Slide counter (bottom-right) ───────────────────────────────
        counter = f"{slide_num} / {total_slides}"
        bbox = draw.textbbox((0, 0), counter, font=small_font)
        tw = bbox[2] - bbox[0]
        draw.text((w - tw - 40, h - 50), counter, fill=TXT_DIM, font=small_font)

        # ── 9. Source label (bottom-left) ─────────────────────────────────
        source = article.get("source", "").replace("_", " ").title()
        draw.text((40, h - 50), f"AI & Tech  •  {source}", fill=TXT_DIM, font=small_font)

        return img

    # ------------------------------------------------------------------
    # Public entry points
    # ------------------------------------------------------------------

    def generate_content(self, article: dict) -> dict:
        """Generate caption and single image-with-text for an article."""
        caption   = self.generate_caption(article)
        base_url  = self.generate_image_url(article)
        image_url = self._create_image_with_text(base_url, article)
        return {"caption": caption, "image_url": image_url}

    def generate_carousel_content(self, article: dict) -> dict:
        """Generate a carousel: cover photo + text-on-bg slides from caption.

        - Slide 1: Article photo + headline overlay (existing cover logic)
        - Slides 2+: Topic-relevant background image + bullet text overlay
        - Hashtags are NEVER placed on any image slide (caption only)

        Returns:
            {
                "caption":    str,
                "image_urls": list[str],  # [cover_url, slide2_url, ...]
            }
        """
        # 1. Generate caption + cover image
        caption   = self.generate_caption(article)
        base_url  = self.generate_image_url(article)
        cover_url = self._create_image_with_text(base_url, article)

        # 2. Split caption into slide text segments (no hashtags)
        segments = self._split_caption_into_slides(caption)
        total_slides = 1 + len(segments)  # cover + text slides

        image_urls = [cover_url]

        # 3. Reuse the same topic prompt for all bg images (different seeds)
        topic_prompt = self._generate_image_prompt(article)
        bg_base_prompt = quote(
            f"{topic_prompt}, cinematic, 4k, no text, no watermark, no logo"
        )

        # 4. Build each text slide with its own background image
        for i, segment in enumerate(segments):
            slide_num = i + 2  # slide 1 = cover
            seed      = random.randint(1, 99999)
            bg_url    = (
                f"https://image.pollinations.ai/prompt/{bg_base_prompt}"
                f"?width=1080&height=1080&nologo=true&seed={seed}"
            )
            print(f"[Generator] Generating BG for slide {slide_num}/{total_slides}...")
            try:
                img = self._make_text_slide(
                    text=segment,
                    slide_num=slide_num,
                    total_slides=total_slides,
                    article=article,
                    bg_url=bg_url,
                )
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=92)
                buf.seek(0)
                hosted = self._upload_image(buf)
                if hosted:
                    print(f"[Generator] ✓ Slide {slide_num}/{total_slides} hosted")
                    image_urls.append(hosted)
                else:
                    print(f"[Generator] ✗ Slide {slide_num} upload failed — skipping")
            except Exception as e:
                print(f"[Generator] ✗ Error building slide {slide_num}: {e}")

        print(f"[Generator] ✓ Carousel ready: {len(image_urls)} slides")
        return {"caption": caption, "image_urls": image_urls}
