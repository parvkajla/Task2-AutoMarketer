import os
import sys
import json
import argparse
import time
from datetime import datetime
import urllib.parse
import re

from scraper import scrape_website
from llm import generate_campaign_data
from image_generator import generate_image

def slugify(value):
    """Convert a string to a safe directory name."""
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "_", value)

def save_text(filepath, content):
    """Helper to save text content to a file."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def run_pipeline(url, output_root="output"):
    """
    Run the entire marketing automation pipeline end-to-end.
    Returns the campaign directory path and campaign details dictionary.
    """
    start_time = time.time()
    print("=" * 60)
    print(f"STARTING AUTO-MARKETER PIPELINE FOR: {url}")
    print("=" * 60)
    
    # --- Step 1: Scraping ---
    print("\n[1/3] Scraping Website Content...")
    scrape_start = time.time()
    scraped_data = scrape_website(url)
    scrape_duration = time.time() - scrape_start
    
    if not scraped_data:
        print("[-] Scraping failed completely.")
        return None
        
    print(f"[+] Scraping completed in {scrape_duration:.2f}s ({scraped_data['source']})")
    print(f"    Title: {scraped_data['title']}")
    print(f"    Domain: {scraped_data['domain']}")
    print(f"    Content Length: {len(scraped_data['content'])} characters")
    
    # --- Step 2: LLM Campaign Synthesis & Prompt Translation ---
    print("\n[2/3] Chaining LLM for Caption Synthesis & Image Prompt Translation...")
    llm_start = time.time()
    campaign_data = generate_campaign_data(scraped_data)
    llm_duration = time.time() - llm_start
    
    print(f"[+] LLM processing completed in {llm_duration:.2f}s")
    print(f"    Tone: {campaign_data['tone']}")
    print(f"    Marketing Caption: {campaign_data['caption']}")
    print(f"    Image Prompt: {campaign_data['image_prompt'][:120]}...")
    
    # Create unified campaign directory
    domain_slug = slugify(scraped_data["domain"])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    campaign_dir = os.path.join(output_root, f"campaign_{domain_slug}_{timestamp}")
    os.makedirs(campaign_dir, exist_ok=True)
    
    # File paths
    caption_path = os.path.join(campaign_dir, "caption.txt")
    prompt_path = os.path.join(campaign_dir, "image_prompt.txt")
    scraped_path = os.path.join(campaign_dir, "scraped_content.txt")
    image_path = os.path.join(campaign_dir, "marketing_image.png")
    metadata_path = os.path.join(campaign_dir, "metadata.json")
    
    # Save text outputs
    save_text(caption_path, campaign_data["caption"])
    save_text(prompt_path, campaign_data["image_prompt"])
    save_text(scraped_path, scraped_data["content"])
    
    # --- Step 3: Image Generation ---
    print("\n[3/3] Generating Visual Assets...")
    image_start = time.time()
    
    # Pass prompt, caption, and title for PIL fallback
    generated_image = generate_image(
        prompt=campaign_data["image_prompt"],
        caption=campaign_data["caption"],
        title=scraped_data["title"],
        output_path=image_path
    )
    
    image_duration = time.time() - image_start
    total_duration = time.time() - start_time
    
    if generated_image:
        print(f"[+] Image assets generated in {image_duration:.2f}s")
        status = "Success"
    else:
        print("[-] Image generation failed.")
        status = "Success_With_Failed_Image"
        
    # Compile and save metadata
    metadata = {
        "url": url,
        "domain": scraped_data["domain"],
        "title": scraped_data["title"],
        "scrape_source": scraped_data["source"],
        "tone": campaign_data["tone"],
        "caption": campaign_data["caption"],
        "image_prompt": campaign_data["image_prompt"],
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "metrics": {
            "scrape_time_seconds": scrape_duration,
            "llm_time_seconds": llm_duration,
            "image_time_seconds": image_duration,
            "total_time_seconds": total_duration
        },
        "files": {
            "caption": "caption.txt",
            "image_prompt": "image_prompt.txt",
            "scraped_content": "scraped_content.txt",
            "image": "marketing_image.png" if generated_image else None
        }
    }
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
        
    # --- Create / Update "Latest" Soft-cache for easy referencing ---
    latest_dir = os.path.join(output_root, "latest")
    os.makedirs(latest_dir, exist_ok=True)
    
    save_text(os.path.join(latest_dir, "caption.txt"), campaign_data["caption"])
    save_text(os.path.join(latest_dir, "image_prompt.txt"), campaign_data["image_prompt"])
    with open(os.path.join(latest_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
    if generated_image and os.path.exists(image_path):
        import shutil
        shutil.copy2(image_path, os.path.join(latest_dir, "marketing_image.png"))
        
    print("\n" + "=" * 60)
    print("PIPELINE RUN COMPLETED")
    print("=" * 60)
    print(f"    Campaign Output Folder: {campaign_dir}")
    print(f"    Paired Assets:")
    print(f"       - Caption: {caption_path}")
    print(f"       - Image: {image_path if generated_image else 'None (Failed)'}")
    print(f"    Saved 'Latest' Shortcut in: {latest_dir}/")
    print("=" * 60 + "\n")
    
    return campaign_dir, metadata

def main():
    parser = argparse.ArgumentParser(description="Auto-Marketer AI Orchestration Pipeline")
    parser.add_argument(
        "--url", "-u", 
        type=str, 
        help="The website URL to generate the campaign from"
    )
    parser.add_argument(
        "--out", "-o", 
        type=str, 
        default="output", 
        help="Root directory to save generated campaigns (default: output)"
    )
    args = parser.parse_args()
    
    url = args.url
    if not url:
        # Fallback to interactive CLI mode if no argument is passed
        url = input("Enter Website URL: ").strip()
        
    if not url:
        print("[-] Error: URL cannot be empty.")
        sys.exit(1)
        
    campaign_dir, metadata = run_pipeline(url, args.out)
    if not campaign_dir:
        sys.exit(1)

if __name__ == "__main__":
    main()