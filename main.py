from flask import Flask, jsonify
from scrapy.crawler import CrawlerProcess
from omni.omni.spiders import Omni
from twisted.internet import reactor, defer

app = Flask(__name__)

# Sample input for Scrapy


# Scrapy process needs to be run in a separate function
def run_scraper():
    process = CrawlerProcess()
    process.crawl(Omni)  # Run without arguments
    process.crawl(Omni, program_list=program_list)  # Run with arguments
    process.start(stop_after_crawl=False)  # Ensure it doesn't stop the reactor

@app.route("/")
def index():
    """Trigger Scrapy when the Cloud Run service is accessed."""
    try:
        run_scraper()
        return jsonify({"status": "Scraper started successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    

# from omni.omni.spiders import Omni
# from scrapy.crawler import CrawlerProcess

# program_list = [
#         {
#     "university": "Indiana University",
#     "school": "Kelley School of Business",
#     "program": "MS in Management",
#     "url": "https://kelley.iu.edu/programs/ms-management/index.html"
#   }
#     ]


# process = CrawlerProcess()
# process.crawl(Omni)
# process.crawl(Omni, program_list=program_list)
# process.start()


# Issue:
## Google cloud run is failing because of the below error:
# Revision 'test-image2-00001-prq' is not ready and cannot serve traffic.
# The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable within the allocated timeout.
# This can happen when the container port is misconfigured or if the timeout is too short.
# The health check timeout can be extended.
# Logs for this revision might contain more information.
# Logs URL: Open Cloud Logging
# For more troubleshooting guidance, see https://cloud.google.com/run/docs/troubleshooting#container-failed-to-start

# Possible Solution:
## The issue is because the container is not listening on the port 8080.
## Errors building the docker image and linking it with gcr
## Try github continuous run

# What I will do:
## 1: Rebuild the docker image and push it to gcr
## 2: Try to do it in github
