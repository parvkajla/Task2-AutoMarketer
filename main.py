from scraper import scrape_website
from llm import generate_caption, generate_image_prompt
import os


def save_output(filename, content):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)


def main():
    url = input("Enter Website URL: ").strip()

    print("\nScraping website...")
    data = scrape_website(url)

    if not data:
        print("Failed to scrape website.")
        return

    website_text = f"""
Title: {data['title']}

Content:
{data['content'][:1000]}
"""

    print("Generating marketing caption...")
    caption = generate_caption(website_text)

    print("Generating image prompt...")
    image_prompt = generate_image_prompt(website_text)

    os.makedirs("output", exist_ok=True)

    save_output("output/caption.txt", caption)
    save_output("output/image_prompt.txt", image_prompt)

    print("\nCompleted Successfully!")

    print("\nMarketing Caption:\n")
    print(caption)

    print("\nImage Prompt:\n")
    print(image_prompt)

    print("\nFiles Saved:")
    print("output/caption.txt")
    print("output/image_prompt.txt")


if __name__ == "__main__":
    main()