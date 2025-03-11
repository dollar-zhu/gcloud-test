import os
import threading
import time
from flask import Flask, jsonify, request
import requests
from scrapy.crawler import CrawlerProcess
from omni.omni.spiders import Omni

# First, import your Flask app and functions from main.py
from main import app, run_scraper
# Local IP
local_IP = 'http://127.0.0.1:8080/scrape'
internal_IP = 'http://10.128.0.2:8080/scrape',
external_IP = 'http://34.57.172.11:8080/scrape'

def flask_thread_function():
    """Function to run Flask server in a thread"""
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def send_request():
    """Function to send the POST request"""
    # Wait a few seconds for the Flask server to start up
    time.sleep(2)
    
    data_to_send = {
        "program_list": [{
            "id": 153,
            "batch": 100,
            "university": "Duke University",
            "school": "Pratt School of Engineering",
            "program": "Master of Engineering in Biomedical Engineering",
            "url": "https://bme.duke.edu/admissions/masters/"
        }]
    }
    
    print("Sending POST request to the server...")
    try:
        response = requests.post(internal_IP, json=data_to_send)
        print(f"Server response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Failed to connect to server. Make sure the server started properly.")

if __name__ == "__main__":
    # Start Flask in a background thread
    print("Starting Flask server...")
    server_thread = threading.Thread(target=flask_thread_function)
    server_thread.daemon = True  # This ensures the thread exits when the main program exits
    server_thread.start()
    
    # Send the request
    send_request()
    
    # Keep the main program running to allow the scraper to complete
    print("\nServer is still running. Press Ctrl+C to exit when scraping is done...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")