import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Initialize Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    # Use gemini-2.5-flash as default fast model
    model = genai.GenerativeModel("gemini-2.5-flash")
else:
    model = None
    print("[Warning] GEMINI_API_KEY not found in environment. Using rule-based fallback.")

def generate_fallback_campaign(title, domain, content):
    """
    Rule-based campaign generator when Gemini API is unavailable.
    """
    clean_title = title.replace(" - Fallback", "").strip()
    words = clean_title.split()
    subject = words[0] if words else "Product"
    
    # Construct a high-quality default caption
    caption = f"Discover the future of {subject} today. Experience premium quality, innovative features, and unmatched service tailored to your needs!"
    cta = f"Visit {domain} to learn more and get started!"
    
    # Construct a high-quality default image prompt
    image_prompt = (
        f"A clean, modern commercial banner for {clean_title}. "
        f"Featuring a premium product display, sleek minimal aesthetic, "
        f"professional studio lighting, smooth color gradients, "
        f"depth of field, high-end commercial style, 8k resolution, photorealistic."
    )
    
    return {
        "tone": "Professional & Clean (Fallback)",
        "caption": f"{caption} {cta}",
        "image_prompt": image_prompt
    }

def generate_campaign_data(scraped_data):
    """
    Analyze brand tone, synthesize a 2-sentence caption + CTA, 
    and translate it into an image generation prompt.
    """
    title = scraped_data.get("title", "Modern Brand")
    content = scraped_data.get("content", "")
    domain = scraped_data.get("domain", "website")
    
    # Check if Gemini model is available
    if not model or not api_key:
        print("[Info] Gemini API not configured. Triggering rule-based fallback campaign.")
        return generate_fallback_campaign(title, domain, content)
        
    prompt = f"""
You are an elite digital marketing specialist and creative art director.
Analyze the following scraped website data (Title, Domain, Content):

Title: {title}
Domain: {domain}
Content: {content[:3000]}

Generate a structured JSON output with the following keys:
1. "tone": Briefly describe the brand's tone (e.g. "Sleek, minimalist, luxurious" or "Vibrant, friendly, energetic").
2. "caption": Create a punchy, engaging 2-sentence marketing caption. Make it sound native to professional ads and match the brand's tone.
3. "cta": A strong call-to-action (e.g., "Elevate your workspace today at domain.com").
4. "image_prompt": A highly detailed prompt for an Image Generation AI (like Stable Diffusion) to create a matching marketing graphic. Avoid text/logos in the image prompt, and focus on physical objects, composition, colors, mood, lighting, and textures that match the tone.

Return raw JSON only, fitting this schema:
{{
  "tone": "string",
  "caption": "string",
  "cta": "string",
  "image_prompt": "string"
}}
"""

    # Retry logic for API calls
    for attempt in range(3):
        try:
            # Set response schema to JSON
            response = model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.7
                }
            )
            
            # Parse response text
            data = json.loads(response.text)
            
            # Combine caption and CTA if separated
            caption_text = data.get("caption", "").strip()
            cta_text = data.get("cta", "").strip()
            if cta_text and cta_text not in caption_text:
                full_caption = f"{caption_text} {cta_text}"
            else:
                full_caption = caption_text
                
            return {
                "tone": data.get("tone", "Professional & Clean"),
                "caption": full_caption,
                "image_prompt": data.get("image_prompt", "")
            }
            
        except Exception as e:
            print(f"[Warning] Gemini API attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
            
    print("[Error] All Gemini API attempts failed. Falling back to rule-based generation.")
    return generate_fallback_campaign(title, domain, content)