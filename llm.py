import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_caption(product_text):
    prompt = f"""
You are an expert digital marketer.

Analyze the website information below and create:

1. A short, engaging marketing caption.
2. A strong call-to-action.

Website Information:
{product_text}

Keep the response under 60 words.
"""

    response = model.generate_content(prompt)
    return response.text


def generate_image_prompt(product_text):
    text = product_text[:500]

    return f"""
Professional marketing advertisement banner.

Subject:
{text}

Style:
Modern commercial advertising, premium branding, ultra realistic,
high quality product showcase, clean composition, vibrant colors,
cinematic lighting, depth of field, social media campaign design,
4K resolution, professional photography, detailed background,
award-winning marketing creative.
"""