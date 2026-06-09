import os
import time
import requests
import urllib3
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# Suppress insecure request warnings for environment fallback (e.g. self-signed cert blocks)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

HF_TOKEN = os.getenv("HF_API_TOKEN")

# Available SD models to fall back
MODEL_URLS = [
    "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
    "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
    "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
]

def generate_local_fallback_image(caption, title, output_path):
    """
    Programmatically creates a premium-looking marketing graphic
    using a curated gradient background and clean glassmorphic typography card.
    Ensure zero-dependency offline rendering capability.
    """
    print("[Info] Generating a local premium graphic fallback using Pillow...")
    width, height = 1024, 1024
    
    # 1. Create base gradient background (Vibrant Purple to Deep Indigo)
    base = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(base)
    
    # Draw soft vertical gradient
    for y in range(height):
        # Interpolate between Indigo (31, 28, 79) and Neon Orchid (131, 56, 236)
        ratio = y / height
        r = int(31 + (131 - 31) * ratio)
        g = int(28 + (56 - 28) * ratio)
        b = int(79 + (236 - 79) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    # Draw a decorative modern geometric accent (glowing orb)
    # Draw a large soft circle in top-right
    overlay_orb = Image.new("RGBA", base.size, (0, 0, 0, 0))
    orb_draw = ImageDraw.Draw(overlay_orb)
    orb_draw.ellipse([600, -100, 1100, 400], fill=(255, 0, 128, 40))
    orb_draw.ellipse([-200, 700, 300, 1200], fill=(0, 180, 216, 40))
    
    # 2. Draw glassmorphic card overlay
    # White card in center with semi-transparency and thin border
    card_margin_x = 100
    card_margin_y = 150
    card_box = [card_margin_x, card_margin_y, width - card_margin_x, height - card_margin_y]
    orb_draw.rounded_rectangle(
        card_box,
        radius=35,
        fill=(255, 255, 255, 20),       # Translucent white
        outline=(255, 255, 255, 70),     # Semi-transparent border
        width=3
    )
    
    # Blend base and orb overlay
    img = Image.alpha_composite(base.convert("RGBA"), overlay_orb)
    final_draw = ImageDraw.Draw(img)
    
    # 3. Load high-quality system fonts (failsafe logic)
    font_paths = [
        "C:\\Windows\\Fonts\\SegoeUIb.ttf",   # Segoe UI Bold
        "C:\\Windows\\Fonts\\Arialbd.ttf",    # Arial Bold
        "C:\\Windows\\Fonts\\Calibrib.ttf",   # Calibri Bold
        "C:\\Windows\\Fonts\\SegoeUI.ttf",    # Segoe UI Regular
        "C:\\Windows\\Fonts\\Arial.ttf",      # Arial Regular
        "C:\\Windows\\Fonts\\Calibri.ttf"     # Calibri Regular
    ]
    
    title_font = None
    body_font = None
    cta_font = None
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                title_font = ImageFont.truetype(path, 46)
                body_font = ImageFont.truetype(path, 32)
                cta_font = ImageFont.truetype(path, 26)
                break
            except Exception:
                continue
                
    if not title_font:
        # Default fallback if no system fonts load
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        cta_font = ImageFont.load_default()
        
    # Helper to get text width safely across Pillow versions
    def get_text_width(text, font):
        if hasattr(font, "getlength"):
            return font.getlength(text)
        elif hasattr(font, "getsize"):
            return font.getsize(text)[0]
        return len(text) * 10
        
    # Helper to get text height safely
    def get_text_height(text, font):
        if hasattr(font, "getbbox"):
            bbox = font.getbbox(text)
            return bbox[3] - bbox[1] if bbox else 24
        elif hasattr(font, "getsize"):
            return font.getsize(text)[1]
        return 24
        
    # 4. Draw Header/Title
    title_text = title.upper()
    if len(title_text) > 30:
        title_text = title_text[:27] + "..."
    title_w = get_text_width(title_text, title_font)
    title_x = (width - title_w) // 2
    final_draw.text((title_x, card_margin_y + 60), title_text, fill=(255, 255, 255, 255), font=title_font)
    
    # Draw decorative thin line below title
    line_y = card_margin_y + 130
    final_draw.line([(width // 2 - 100, line_y), (width // 2 + 100, line_y)], fill=(255, 255, 255, 120), width=2)
    
    # 5. Wrap and Draw Caption (Body Text)
    max_text_width = width - (card_margin_x * 2) - 80
    words = caption.split()
    wrapped_lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        if get_text_width(test_line, body_font) <= max_text_width:
            current_line.append(word)
        else:
            if current_line:
                wrapped_lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        wrapped_lines.append(" ".join(current_line))
        
    # Draw body text lines
    start_y = card_margin_y + 200
    line_spacing = 15
    for idx, line in enumerate(wrapped_lines[:8]):  # Limit lines to prevent overflow
        line_w = get_text_width(line, body_font)
        line_h = get_text_height(line, body_font)
        x = (width - line_w) // 2
        y = start_y + idx * (line_h + line_spacing)
        final_draw.text((x, y), line, fill=(240, 240, 245, 240), font=body_font)
        
    # 6. Draw Call to Action Button at bottom of card
    cta_text = "LEARN MORE"
    cta_w = get_text_width(cta_text, cta_font)
    cta_h = get_text_height(cta_text, cta_font)
    
    btn_w = cta_w + 60
    btn_h = cta_h + 30
    btn_x0 = (width - btn_w) // 2
    btn_y0 = height - card_margin_y - 120
    
    # Draw pill button
    final_draw.rounded_rectangle(
        [btn_x0, btn_y0, btn_x0 + btn_w, btn_y0 + btn_h],
        radius=15,
        fill=(0, 180, 216, 230),  # Bright Cyan highlight
        outline=(255, 255, 255, 255),
        width=1
    )
    
    btn_text_x = btn_x0 + (btn_w - cta_w) // 2
    btn_text_y = btn_y0 + (btn_h - cta_h) // 2 - 2  # slight offset adjustment
    final_draw.text((btn_text_x, btn_text_y), cta_text, fill=(255, 255, 255, 255), font=cta_font)
    
    # Save image to file system
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.convert("RGB").save(output_path, "PNG")
    print(f"[Success] Local premium graphic fallback saved to {output_path}")
    return output_path

def _post_request_with_ssl_fallback(url, headers, json_data, timeout):
    """
    Tries requests.post normally. If it fails with an SSL verification error,
    retries with verify=False.
    """
    try:
        return requests.post(url, headers=headers, json=json_data, timeout=timeout)
    except requests.exceptions.SSLError:
        print("[Warning] SSL Verification failed. Retrying request with verify=False...")
        return requests.post(url, headers=headers, json=json_data, timeout=timeout, verify=False)

def generate_image(prompt, caption, title, output_path="output/marketing_image.png"):
    """
    Generate an image from prompt using Hugging Face Stable Diffusion,
    supporting loading retry logic, multiple model failover, and PIL local fallback.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if not HF_TOKEN:
        print("[Warning] HF_API_TOKEN not found in environment. Utilizing local graphic generator.")
        return generate_local_fallback_image(caption, title, output_path)

    # Iterate through models for fallback
    for model_idx, api_url in enumerate(MODEL_URLS):
        model_name = api_url.split("/models/")[-1]
        print(f"[Info] Attempting image generation with model {model_idx + 1}: {model_name}...")
        
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}"
        }
        
        # Retry loop for model loading (HTTP 503)
        max_retries = 4
        for attempt in range(max_retries):
            try:
                response = _post_request_with_ssl_fallback(
                    api_url,
                    headers=headers,
                    json_data={"inputs": prompt},
                    timeout=45
                )
                
                # Check status code
                if response.status_code == 200:
                    # Validate content is actually a valid image format (PNG/JPEG)
                    content_type = response.headers.get("Content-Type", "").lower()
                    is_image_header = content_type.startswith("image/")
                    
                    # Check magic bytes for JPEG (FF D8) or PNG (89 50 4E 47)
                    has_magic_bytes = (
                        response.content.startswith(b"\x89PNG") or 
                        response.content.startswith(b"\xff\xd8")
                    )
                    
                    if not (is_image_header or has_magic_bytes):
                        print(f"[Warning] Model {model_name} returned non-image content (headers: {content_type}). Likely blocked or intercepted by network filter.")
                        break  # Break retry loop to try next model or fall back
                        
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    print(f"[Success] Image successfully generated and saved via HF model {model_name}!")
                    return output_path
                    
                elif response.status_code == 503:
                    # Model is loading on Hugging Face
                    try:
                        error_data = response.json()
                        estimated_time = error_data.get("estimated_time", 15.0)
                    except Exception:
                        estimated_time = 15.0
                        
                    wait_time = min(estimated_time, 20.0)
                    print(f"[Info] HF Model is loading. Attempt {attempt + 1}/{max_retries}. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    
                else:
                    print(f"[Warning] Model {model_name} failed with HTTP status {response.status_code}.")
                    print(response.text[:200])
                    break  # Break retry loop to try next model
                    
            except requests.exceptions.RequestException as e:
                print(f"[Warning] Request exception for model {model_name}: {e}")
                time.sleep(2)
                
    # If all API attempts fail, trigger local premium graphic rendering
    print("[Error] All Hugging Face image generation models failed or timed out.")
    return generate_local_fallback_image(caption, title, output_path)