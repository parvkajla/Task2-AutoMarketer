import os
import sys
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from main import run_pipeline

app = Flask(__name__, template_folder="templates", static_folder="output")

# Ensure output directory exists
os.makedirs("output", exist_ok=True)
os.makedirs("templates", exist_ok=True)

@app.route("/")
def index():
    """Render the dashboard UI."""
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def generate():
    """
    Trigger the marketing pipeline for a given URL.
    Expects JSON: { "url": "https://example.com" }
    """
    data = request.json or {}
    url = data.get("url", "").strip()
    
    if not url:
        return jsonify({"success": False, "error": "URL is required"}), 400
        
    try:
        # Run the orchestrator pipeline
        campaign_dir, metadata = run_pipeline(url, "output")
        if not campaign_dir:
            return jsonify({"success": False, "error": "Pipeline execution failed"}), 500
            
        campaign_id = os.path.basename(campaign_dir)
        metadata["campaign_id"] = campaign_id
        
        return jsonify({
            "success": True,
            "campaign_id": campaign_id,
            "metadata": metadata
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/campaigns", methods=["GET"])
def list_campaigns():
    """
    Scan the output directory and return metadata of all previous campaigns.
    Ordered by newest timestamp first.
    """
    campaigns = []
    output_dir = "output"
    
    if not os.path.exists(output_dir):
        return jsonify([])
        
    # List all subdirectories
    for folder in os.listdir(output_dir):
        # Ignore system folders and the 'latest' folder
        if folder == "latest" or not folder.startswith("campaign_"):
            continue
            
        folder_path = os.path.join(output_dir, folder)
        if os.path.isdir(folder_path):
            metadata_path = os.path.join(folder_path, "metadata.json")
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    meta["campaign_id"] = folder
                    campaigns.append(meta)
                except Exception as e:
                    print(f"[Warning] Failed to read metadata in {folder}: {e}")
                    
    # Sort campaigns by timestamp (newest first)
    campaigns.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return jsonify(campaigns)

@app.route("/api/campaigns/<campaign_id>/image")
def get_image(campaign_id):
    """Serve the marketing image of a specific campaign."""
    directory = os.path.join("output", campaign_id)
    if os.path.exists(os.path.join(directory, "marketing_image.png")):
        return send_from_directory(directory, "marketing_image.png")
    return "Image not found", 404

@app.route("/api/campaigns/<campaign_id>/files/<filename>")
def get_file(campaign_id, filename):
    """Serve other campaign files (caption, prompt, scraped text)."""
    directory = os.path.join("output", campaign_id)
    if filename in ["caption.txt", "image_prompt.txt", "scraped_content.txt", "metadata.json"]:
        return send_from_directory(directory, filename)
    return "File not found", 404

if __name__ == "__main__":
    # Start local development server
    port = int(os.environ.get("PORT", 5000))
    print(f"\n==========================================")
    print(f"*** AUTO-MARKETER APP LAUNCHED AT: http://localhost:{port} ***")
    print(f"==========================================\n")
    app.run(host="127.0.0.1", port=port, debug=True)
