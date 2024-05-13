import csv
import logging
import requests

NEBULA_API_KEY = "fR8Uk9EGuRzFV8uwZ8EmAg"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

API_ENDPOINT = 'https://nubela.co/proxycurl/api/v2/linkedin'


def get_profile_with_proxycurl(url):
    headers = {'Authorization': f'Bearer {NEBULA_API_KEY}'}
    try:
        response = requests.get(API_ENDPOINT, params={'url': url}, headers=headers)
        response.raise_for_status()
        profile_data = response.json()
        profile_data['job_title'] = profile_data.get('title', '')
        return profile_data
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for URL: {url}. Error: {e}")
        return None


def format_data(profile_data):
    if profile_data is None:
        return None

    first_name = profile_data.get('first_name', '')
    last_name = profile_data.get('last_name', '')
    full_name = f"{first_name} {last_name}"
    job_title = profile_data.get('title', '')
    company = profile_data.get('company', {})

    educations = []
    for edu in (profile_data.get('education') or []):
        educations.append({
            'school': edu.get('school', ''),
            'degree_name': edu.get('degree_name', ''),
            'field_of_study': edu.get('field_of_study', ''),
            'starts_at': edu.get('starts_at', {}).get('year', ''),
            'ends_at': edu.get('ends_at', {}).get('year', '')
        })

    experiences = []
    for exp in (profile_data.get('experiences') or []):
        experiences.append({
            'title': exp.get('title', ''),
            'company': exp.get('company', {}).get('name', '')
        })

    return {
        'first_name': first_name,
        'last_name': last_name,
        'full_name': full_name,
        'job_title': job_title,
        'company': company.get('name', ''),
        'educations': educations,
        'experiences': experiences
    }

def get_fieldnames(data):
    fieldnames = set()
    for profile in data:
        fieldnames.update(profile.keys())
        fieldnames.remove('educations')
        fieldnames.remove('experiences')
        for i, education in enumerate(profile['educations']):
            fieldnames.update([f'education{i+1}_{k}' for k in education])
        for i, experience in enumerate(profile['experiences']):
            fieldnames.update([f'experience{i+1}_{k}' for k in experience])
    return list(fieldnames)

def read_input_file(input_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            urls = [line.strip() for line in file]
            logging.info(f"Read {len(urls)} URLs from input file: {input_file}")
            return urls
    except FileNotFoundError as e:
        logging.error(f"Input file not found: {input_file}")
    except Exception as e:
        logging.error(f"Failed to read input file: {input_file}. Error: {e}")
    return []

def write_output_csv(output_file, data):
    fieldnames = get_fieldnames(data)
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        for profile in data:
            row = {key: profile.get(key, '') for key in fieldnames if key not in ['educations', 'experiences']}
            for i, education in enumerate(profile['educations']):
                for key, value in education.items():
                    row[f'education{i+1}_{key}'] = value
            for i, experience in enumerate(profile['experiences']):
                for key, value in experience.items():
                    row[f'experience{i+1}_{key}'] = value
            csv_writer.writerow(row)

def main(input_file, output_file):
    urls = read_input_file(input_file)
    print(urls)
    if not urls:
        logging.error(f"No URLs found in input file: {input_file}")
        return

    data = []

    for url in urls:
        profile_data = get_profile_with_proxycurl(url)
        if profile_data is None:
            continue

        formatted_data = format_data(profile_data)
        if formatted_data is not None:
            data.append(formatted_data)
        else:
            logging.warning(f"Skipping URL {url} due to missing or invalid data")


    if not data:
        logging.error("No profile data found, aborting.")
        return

    write_output_csv(output_file, data)
    
    # Send a message using Twilio
    from twilio.rest import Client
    
    account_sid = 'AC23dc34ba5cd621e053baf9e56deee489'
    auth_token = '74ccf8bad2d718bb7db96ec71452dcb0'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_='+15038966022',
        body='Scraping complete!',
        to='+15038966022'
    )

    print(message.sid)
    print("Message sent.")

if __name__ == "__main__":
    input_file = "profiles.txt"
    output_file = "output.csv"
    main(input_file, output_file)