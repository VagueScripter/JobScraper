import requests
import json
import threading
import time
from bs4 import BeautifulSoup

start = time.time()
url = "https://www.cermati.com/karir"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'lxml')
data = json.loads(soup.find('script', type='application/json').text)

final_data = {}
url_list = []
def job_details(job_url, name, dept, location, job_type):
    job_response = requests.get(job_url)
    job_soup = BeautifulSoup(job_response.content, 'lxml')
    
    job_section_id, qualification_section_id = "st-jobDescription", "st-qualifications"
    job_description   = [li.text for li in  job_soup.find("section", {"id": job_section_id}).find_all("li")]
    try:
        job_qualification = [li.text for li in  job_soup.find("section", {"id": qualification_section_id}).find_all("li")]
    except AttributeError:
    	#print("No qualification Details")
    	job_qualification = []
    	
    posted_by =""
    try:
        posted_by = job_soup.find("div", {"class": "media-content"}).find("h3").text
    except AttributeError:
        posted_by =""
    #print("Fetched data for department:",dept," Title was: ",name," Location is:",location," Job type is:",job_type," Posted by :",posted_by)
    
    if dept not in final_data:
        final_data[dept] = []
        final_data[dept].append({
            "title":name,
            "location":location,
            "description":job_description,
            "qualification":job_qualification,
            "job_type":job_type,
            "postedBy":posted_by
            })
    else:
        final_data[dept].append({
            "title":name,
            "location":location,
            "description":job_description,
            "qualification":job_qualification,
            "job_type":job_type,
            "postedBy":posted_by
            })
        json_objectt = json.dumps(final_data, indent = 4)

static_url_job = "https://www.smartrecruiters.com/Cermaticom/"
for job in data['smartRecruiterResult']['all']['content']:
    
    #Setting required variables
    id, name, city, job_type =job['id'], job['name'], job['location']['city'], job['typeOfEmployment']['label']
    
    #To check if department is not present.
    if 'label' in job['department']: dept = job['department']['label']
    else: dept = None
    
    #Building URL
    final_url = f'{static_url_job}{id}/{name}'

    #Fetching Country details
    country = str([field['valueLabel'] for field in job['customField'] if field['fieldId'] == "COUNTRY"][0])
    location = city +", " + country
    #getting job details by requesting the job website
    #job_details(final_url, name, dept, location, job_type)
    url_list.append([final_url, name, dept, location, job_type])
    

thread=[threading.Thread(target=job_details, args=(unpacked[0], unpacked[1], unpacked[2], unpacked[3], unpacked[4])) for unpacked in url_list]
for t in thread:
    t.start()
for x in thread:
     x.join()

json_object = json.dumps(final_data, indent = 4)
with open('output.json', 'w') as f:
    print(json_object, file = f)

end = time.time()
print("Total time to execute script:", end - start)

#Just for testing purpose.
count = 0
for keys in final_data.keys():
    count += len(final_data[keys])
    print(keys," count:",len(final_data[keys]))
print("Total count is:",count)
