import scrapy
from markdownify import markdownify as md
from scrapy.crawler import CrawlerProcess
import time
import os
import json
import re
from concurrent.futures import ThreadPoolExecutor
import sys
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError
from google.cloud import storage

def upload_string_to_gcs(bucket_name, destination_blob_name, content):
    """
    Uploads a string as a blob to the specified Google Cloud Storage bucket.
    """
    client = storage.Client()  # This will use your environment's credentials
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(content)
    print(f"Uploaded content to {destination_blob_name} in bucket {bucket_name}.")

def url_to_filename(url):
    # Remove protocol (http:// or https://)
    url = re.sub(r'^https?://', '', url)
    # if the string ends with a /, remove it
    if url.endswith('/'):
        url = url[:-1]
    # Replace slashes with hyphens
    url = url.replace('/', '-')
    # Remove special characters
    url = re.sub(r'[^a-zA-Z0-9\-]', '', url)
    # Convert to lowercase
    return url.lower() + '.md'

def normalize_name(entry):
    # turn it into snake case
    university = entry['university'].replace(' ', '_').lower()
    # replace the comma with blank in university
    university = university.replace(',', '')
    program = entry['program'].replace(' ', '_').lower()
    name = university + '_' + program
    # replace the , with blank in name
    name = name.replace(',', '')
    name = name.replace('.', '')
    return name

def convert_to_folder_name(string):
    string = string.replace(' ', '_').lower()
    string = re.sub(r'[,.]', '', string)
    return string


class Omni(scrapy.Spider):
    name = "markdown_spider"
    
   
    
    # program_list = [
        
    # #    {
    # #         "university": "New York University",
    # #         "school": "Center for Data Science",
    # #         "program": "MS in Data Science",
    # #         "url": "https://cds.nyu.edu/admissions/masters-in-data-science-overview/"
    # #     },
    #     # {
    #     #     "university": "MIT",
    #     #     "school": "Sloan School of Management",
    #     #     "program": "Master of Fianance (MFin)",
    #     #     "url": "https://mitsloan.mit.edu/mfin/explore-program"
    #     # },
    #     # {
    #     #     "university": "Duke University",
    #     #     "school": "Fuqua School of Business",
    #     #     "program": "Master of Management Studies (MMS)",
    #     #     "url": "https://www.fuqua.duke.edu/programs/mms-foundations-of-business"
    #     # },
        
    #     # {
    #     #     "university": "Stanford University",
    #     #     "school": "School of Engineering",
    #     #     "program": "MS in Computer Science",
    #     #     "url": "https://www.cs.stanford.edu/"
    #     # },
    #     {
    #         "university": "University of California, Berkeley",
    #         "school": "Haas School of Business",
    #         "program": "Master of Financial Engineering",
    #         "url": "https://mfe.haas.berkeley.edu"
    #     },
        
    # ]
    program_list = [
        {
    "university": "Indiana University",
    "school": "Kelley School of Business",
    "program": "MS in Management",
    "url": "https://kelley.iu.edu/programs/ms-management/index.html"
  }
    ]

    # def __init__(self, *args, **kwargs):
    def __init__(self, program_list = None, *args, **kwargs):
        super(Omni, self).__init__(*args, **kwargs)
        self.program_list = program_list
        self.scraped_pages = {}
        self.start_time = {}
        self.evaluated_links = {}
        self.dictionary = {}
        self.max_depth = 2
        self.evaluation_threadhold = 7
        for entry in self.program_list:
            name = normalize_name(entry)
            self.scraped_pages[name] = 0
            self.start_time[name] = time.time()
            starting_url = entry['url'].rstrip('/')
            self.evaluated_links[name] = set([starting_url])
            
    def start_requests(self):
        # Initialize the compiled_data for each start_url
        for entry in self.program_list:
            yield scrapy.Request(url=entry['url'], callback=self.parse, meta={'program_info': entry, 'depth': 0, 'is_start_url': True})


    def parse(self, response):
        entry = response.meta['program_info']
        name = normalize_name(entry)
                
        # Stop if 3 minutes have passed
        # if time.time() - self.start_time[name] > 1800:
        #     self.logger.info('30 minutes have passed. Stopping the spider.')
        #     return

        # Stop if 35 pages have been scraped
        # if self.scraped_pages[name] >= 35:
        #     self.logger.info(f'35 pages have been scraped for {self.name}. Moving to the next start_url.')
        #     return

        self.scraped_pages[name] += 1
        links = []
        html_content = response.body
        self.logger.info('html content' + html_content.decode('utf-8'))
        markdown_content = md(html_content.decode('utf-8'))
        
        output_folder = 'output'
        university_folder = os.path.join(output_folder, convert_to_folder_name(entry['university']))
        school_folder = convert_to_folder_name(entry['school'])
        program_folder = convert_to_folder_name(entry['program'])
        folder_path = os.path.join(university_folder, school_folder, program_folder)
        os.makedirs(folder_path, exist_ok=True)
        os.makedirs(os.path.join(folder_path, 'raw'), exist_ok=True)
        os.makedirs(os.path.join(folder_path, 'ref'), exist_ok=True)
        os.makedirs(os.path.join(folder_path, 'processed'), exist_ok=True)
        file_name = url_to_filename(response.url)
        file_path = os.path.join(folder_path, 'raw', f'{file_name}')
        self.dictionary[file_name] = response.url
        # with open(file_path, 'w') as f:
        #     f.write("# Scraped URLs\n")
        #     # starting URL handling
        #     f.write(f"- {response.url}\n")
            # f.write("\n# Links\n")
            # all links in the page
            # for link in response.css('a::attr(href)').getall():
            #     absolute_link = response.urljoin(link)
            #     # Truncate the # and anything following it
            #     absolute_link = absolute_link.split('#')[0]
            #     #get rid of the trailing /
            #     absolute_link = absolute_link.rstrip('/')
            #     if self.is_relevant(absolute_link):
            #         escaped_link = re.escape(link)
            #         self.logger.info(f'Processing link: {escaped_link}')
            #         try:
            #             link_text = response.css(f'a[href="{escaped_link}"]::text').get()
            #         except Exception as e:
            #             self.logger.error(f'Error processing link: {escaped_link}, error: {e}')
            #             continue
            #         # f.write(f"{link_text}- {absolute_link}\n")
            #         links.append({'text': link_text, 'link': absolute_link})

            # f.write("\n# Content\n")
            # markdown_content = "\n".join([line for line in markdown_content.split("\n") if not re.search(r'\[.*?\]\(.*?\)', line) and line.strip() != ""])
            # # f.write(markdown_content)
            # print(markdown_content)
            # #write to google cloud storage
        
        bucket_name = 'imagined_660'
        destination_blob_name = os.path.join(folder_path, 'raw', f'{file_name}')
        upload_string_to_gcs(bucket_name, destination_blob_name, markdown_content)
            
                    
        # Follow up with the relevant links
        evaluation_results = []
        if response.meta['depth'] >= self.max_depth:
            self.logger.info('Reached the max depth. Stopping the spider.')
            return
            
        for absolute_link in links:
            follow_link = absolute_link['link']
            # if the link is not visited already, evaluate it
            if follow_link not in self.evaluated_links[name] and response.meta['depth'] < self.max_depth and response.meta['is_start_url']: 
                self.logger.info('Evaluating the link' + follow_link)
                self.evaluated_links[name].add(follow_link)
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(self.evaluate_link, follow_link, absolute_link['text'], entry)
                    evaluation = future.result()
                if evaluation['relevance_score'] > self.evaluation_threadhold:
                    evaluation_results.append(evaluation)
        
        
        if evaluation_results:
            evaluation_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            # save evaluation results to a file
            # evaluation_file_path = os.path.join(folder_path, 'ref', f'link_evaluation.json')
            # with open(evaluation_file_path, 'w') as f:
            #     json.dump(evaluation_results, f, indent=4)
            
            # follow the most relevant link
            for evaluation_result in evaluation_results:       
                if evaluation_result['relevance_score'] > self.evaluation_threadhold:
                    self.logger.info(f"Following the link {evaluation_result['link']}")
                    current_depth = response.meta['depth']
                    yield scrapy.Request(evaluation_result['link'], callback=self.parse, meta={'program_info': entry, 'depth': current_depth + 1, 'is_start_url': False})
            
            # write self.dictionary to a file
            # dictionary_file_path = os.path.join(folder_path, 'ref', f'directory.json')
            # with open(dictionary_file_path, 'w') as f:
            #     json.dump(self.dictionary, f, indent=4)
                
    def errback_httpbin(self, failure):
        # Log all failures
        self.logger.error(repr(failure))

        # In case you want to do something special for some errors, you can check the failure
        if failure.check(HttpError):
            # These exceptions come from HttpError spider middleware
            # You can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # This is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

        
       
    def is_relevant(self, link):
        
        
        irrelevant_links = [
        'accessibility', 'harassement', 'volunteer', 'endowment', 'gift', 'registrar', 'privacy', 'contact', 'phd','incoming','staff','calendar','for-employer'
        ]
        if not link.startswith(('http://', 'https://')):
            return False
        if any(irrelevant_link in link for irrelevant_link in irrelevant_links):
            return False
        if '.edu' not in link:
            return False
        return True
    
    def evaluate_link(self, link, embed_text, entry):

        
        return {
            'link': link,
            'relevance_score': 8,
            'reason': 'test'
        }
    


# process = CrawlerProcess()
# process.crawl(Omni)
# process.crawl(Omni, program_list=program_list)
# process.start()