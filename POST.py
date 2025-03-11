import requests

data_to_send = {
    "program_list": [{
    "id": 153,
    "batch": 100,
    "university": "Duke University",
    "school": "Pratt School of Engineering",
    "program": "Master of Engineering in Biomedical Engineering",
    "url": "https://bme.duke.edu/admissions/masters/"
  }]}

# Local IP
response = requests.post('http://127.0.0.1:8080/scrape', json=data_to_send)
# Internal IP
# response = requests.post('http://10.128.0.2:8080/scrape', json=data_to_send)
# External IP
# response = requests.post('http://34.57.172.11:8080/scrape', json=data_to_send)

print(response.text)