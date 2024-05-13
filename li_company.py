import requests
import pandas as pd
import json

NEBULA_API_KEY = "fR8Uk9EGuRzFV8uwZ8EmAg"
API_ENDPOINT = 'https://nubela.co/proxycurl/api/v2/linkedin/company/job'

headers = {'Authorization': f'Bearer {NEBULA_API_KEY}'}

def get_jobs(keyword):
    params = {
        'job_type': 'anything',
        'experience_level': 'anything',
        'when': 'anytime',
        'flexibility': 'anything',
        'geo_id': '103644278',  # Geo ID for United States and United Kingdom
        'keyword': keyword,
    }
    response = requests.get(API_ENDPOINT, params=params, headers=headers)
    response.raise_for_status()
    jobs = response.json()
    print(jobs)  # Print the jobs data to see what it looks like

    return jobs

def filter_jobs_for_sophomores_and_class_of_2025(jobs):
    filtered_jobs = []
    for job in jobs['job']:
        if 'description' in job:
            description = job['description'].lower()
            if 'sophomore' in description or 'class of 2025' in description:
                filtered_jobs.append(job)
    return filtered_jobs

def main():
    keywords = ['investment banking internship', 'hedgefund internship']
    all_jobs = []
    for keyword in keywords:
        jobs = get_jobs(keyword)
        filtered_jobs = filter_jobs_for_sophomores_and_class_of_2025(jobs)
        all_jobs.extend(filtered_jobs)

    df = pd.DataFrame(all_jobs)
    df.to_excel('jobs.xlsx', index=False)

if __name__ == "__main__":
    main()
