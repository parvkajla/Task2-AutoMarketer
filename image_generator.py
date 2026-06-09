def generate_image_prompt(product_text):
    lines = product_text.split("\n")
    title = lines[0] if lines else "Product"

    return f"""
Premium marketing advertisement for {title}.

Modern branding,
professional commercial photography,
cinematic lighting,
high-detail composition,
social media advertising campaign,
ultra realistic,
vibrant colors,
4K quality,
award-winning design,
high conversion marketing creative.
"""