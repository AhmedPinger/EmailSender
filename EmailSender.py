import csv
import boto3
from botocore.exceptions import ClientError
import subprocess
import requests
import json
import random
import string

# Get AWS credentials from AWS CLI
aws_access_key = subprocess.check_output(['aws', 'configure', 'get', 'aws_access_key_id'], text=True).strip()
aws_secret_key = subprocess.check_output(['aws', 'configure', 'get', 'aws_secret_access_key'], text=True).strip()

# AWS SES configuration
aws_region = 'us-east-1'  # Virginia region
ses_client = boto3.client('ses', region_name=aws_region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

# Function to send email using AWS SES
def send_email(subject, body, recipient_email):
    try:
        response = ses_client.send_email(
            Source='email@email.com',
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            },
        )
        print(f"Email sent successfully to {recipient_email}. Message ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Error sending email to {recipient_email}: {e.response['Error']['Message']}")

# Function to generate a random password
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

# Function to create a CTFd account
def create_ctfd_account(email, ctfd_api_url, ctfd_api_key):
    password = generate_random_password()

    headers = {
        "Authorization": f"Bearer {ctfd_api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "name": email.split("@")[0],  # Using the part before "@" as the username
        "email": email,
        "password": password,
    }

    response = requests.post(ctfd_api_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print(f"CTFd Account created successfully for {email}. Password: {password}")
        return password
    else:
        print(f"Failed to create CTFd account for {email}. Status code: {response.status_code}")
        print(response.text)
        return None

# Input from the user
list_id = input("Enter HubSpot list ID: ")
main_body_msg = input("Enter main body message: ")

# Fetch first names, last names, and email addresses from HubSpot
url = f'https://api.hubapi.com/contacts/v1/lists/{list_id}/contacts/all'
headers = {
    'Authorization': 'Bearer pat-TheHubSpotToken',
    'Content-Type': 'application/json'
}

params = {
    'count': 250  # Set the count parameter to retrieve up to 250 contacts in a single request
}

hubspot_data = []

while url:
    # Make the request with the count parameter
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    # Append current page data to the list
    hubspot_data.extend({
        'username': contact['properties'].get('firstname', {}).get('value', ''),
        'email': contact['identity-profiles'][0]['identities'][0]['value'],
        'lastname': contact['properties'].get('lastname', {}).get('value', '')
    } for contact in data.get('contacts', []))

    # Get the URL for the next set of results
    next_url = data.get('paging', {}).get('next', {}).get('link')

    # Update the URL for the next request
    url = next_url if next_url else None

    # Check if there are more results
    has_more = data.get('has-more', False)
    if has_more:
        print("Fetching more results...\n")
    else:
        print("All results fetched.\n")

# Print the extracted data
for entry in hubspot_data:
    print(f"{entry['username']}\n{entry['email']}\n{entry['lastname']}\n")

# CTFd registration questions
register_on_ctfd = input("Do you want to register users on CTFd? (yes/no): ").lower()

if register_on_ctfd == "yes":
    # Input for CTFd server URL
    use_existing_ctfd_url = input("Do you want to use the existing CTFd server URL? (yes/no): ").lower()

    if use_existing_ctfd_url == "yes":
        ctfd_server_url = "http://ctfd-server.xyz"
    else:
        ctfd_server_url = input("Enter your new CTFd server URL: ")

    # Input for CTFd server API key
    use_existing_api_key = input("Do you want to use the existing API key? (yes/no): ").lower()

    if use_existing_api_key == "yes":
        ctfd_api_key = "ctfd_RestOfTheKey"
    else:
        ctfd_api_key = input("Enter your new CTFd API key: ")

    # Check if the CTFd server is up
    ctfd_server_up = input("Is the CTFd server up? (yes/no): ").lower()

    while ctfd_server_up != "yes":
        print("Please make sure the CTFd server is up before proceeding.")
        ctfd_server_up = input("Is the CTFd server up now? (yes/no): ").lower()
else:
    ctfd_server_up = "no"  # Default to "no" if not registering on CTFd

# Send credential stack questions
send_cred_stack = input("Do you want to send credential stacks? (yes/no): ").lower()

if send_cred_stack == "yes":
    # Number of stacks for credential link
    num_stacks = int(input("How many stacks for the credential link?: "))
    
    # Iterate to get credential link stacks
    cred_stacks = []
    for i in range(num_stacks):
        cred_stack = input(f"Enter stack {i + 1} as comma-separated values (e.g., 1,2,3): ")
        cred_stacks.append([int(x) if x.isdigit() else x for x in cred_stack.split(',')])
else:
    cred_stacks = None

# Send OpenVPN files question
send_openvpn_files = input("Do you want to send OpenVPN files? (yes/no): ").lower()

# List to store user details
user_details_list = []

# Send email to each recipient in the list
for i, hubspot_entry in enumerate(hubspot_data):
    recipient_email = hubspot_entry['email']
    subject = f"List ID: {list_id} - Email Notification for {hubspot_entry['username']}"
    
    if cred_stacks:
        cred_stack_for_user = [stack[i] if isinstance(stack[i], int) else stack[i] for stack in cred_stacks if i < len(stack)]
        openvpn_link = f"OpenVPN link: https://s3.Region.amazonaws.com/TheBucket/{list_id}/{hubspot_entry['username']}.ovpn" if send_openvpn_files == "yes" else 'N/A'
        ctfd_info = ""
        
        if ctfd_server_up == "yes" and register_on_ctfd == "yes":
            ctfd_password = create_ctfd_account(recipient_email, ctfd_server_url + "/api/v1/users", ctfd_api_key)
            if ctfd_password:
                ctfd_info = f"\nCTFd Server Credentials: {recipient_email}:{ctfd_password}\nCTFd Server URL: {ctfd_server_url}"
        
        user_details_list.append({
            'Email': recipient_email,
            'First Name': hubspot_entry['username'],
            'Last Name': hubspot_entry['lastname'],
            'Cred Stack': cred_stack_for_user if cred_stack_for_user else 'N/A',
            'OpenVPN Link': openvpn_link if send_openvpn_files == "yes" else 'N/A',
            'CTFd Info': ctfd_info if ctfd_info else 'N/A'
        })
        body = f"{main_body_msg}\n\nConnection Details: {cred_stack_for_user}\n\n{openvpn_link}\n{ctfd_info}"
    else:
        user_details_list.append({
            'Email': recipient_email,
            'First Name': hubspot_entry['username'],
            'Last Name': hubspot_entry['lastname'],
            'Cred Stack': 'N/A',
            'OpenVPN Link': f"OpenVPN link: https://s3.Region.amazonaws.com/TheBucket/{list_id}/{hubspot_entry['username']}.ovpn" if send_openvpn_files == "yes" else 'N/A',
            'CTFd Info': 'N/A'
        })
        body = f"{main_body_msg}\n\nOpenVPN link: https://s3.Region.amazonaws.com/TheBucket/{list_id}/{hubspot_entry['username']}.ovpn" if send_openvpn_files == "yes" else f"{main_body_msg}"

    send_email(subject, body, recipient_email)
    print()  # One-line gap

# Write user details to a CSV file
csv_file_path = f'user_details_list_{list_id}.csv'
fieldnames = ['Email', 'First Name', 'Last Name', 'Cred Stack', 'OpenVPN Link', 'CTFd Info']

with open(csv_file_path, mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(user_details_list)

print(f"User details written to {csv_file_path}.")
