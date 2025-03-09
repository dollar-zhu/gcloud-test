import requests

data_to_send = {
    "program_list": [{
    "id": 75,
    "batch": 100,
    "university": "Stanford University",
    "school": "Graduate School of Education",
    "program": "Master in Policy, Organization, and Leadership Studies (POLS)",
    "url": "https://ed.stanford.edu/pols"
  }]}
# Internal IP
response = requests.post('http://10.128.0.2:8080/scrape', json=data_to_send)
# External IP
response = requests.post('http://34.57.172.11:8080/scrape', json=data_to_send)

print(response.text)