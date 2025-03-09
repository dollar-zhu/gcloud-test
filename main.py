import os
import threading
from flask import Flask, jsonify, request
from scrapy.crawler import CrawlerProcess
from omni.omni.spiders import Omni

app = Flask(__name__)

# Original static program_list (optional)
default_program_list = [
    {
        "id": 220,
        "batch": 101,
        "university": "Johns Hopkins University",
        "school": "Whiting School of Engineering",
        "program": "MSE in Financial Mathematics",
        "url": "https://engineering.jhu.edu/ams/academics/graduate-studies/ms-in-financial-mathematics/"
    }
]

def run_scraper(scrape_program_list):
    # Create a new Scrapy crawler process.
    process = CrawlerProcess()
    # Start crawling with the provided program_list.
    process.crawl(Omni, program_list=scrape_program_list)
    process.start(stop_after_crawl=True)

@app.route("/")
def index():
    return jsonify({"status": "API is up."})

@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.get_json()
    # Validate request, program_list must be provided.
    if not data or 'program_list' not in data:
        return jsonify({"error": "Missing 'program_list' in JSON body."}), 400
    scrape_program_list = data["program_list"]
    # Run the scraper in a separate thread.
    thread = threading.Thread(target=run_scraper, args=(scrape_program_list,))
    thread.start()
    return jsonify({"status": "Scraper started successfully!"})

if __name__ == "__main__":
    # The container must bind to the port defined by the PORT environment variable.
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
