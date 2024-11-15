from django.core.management.base import BaseCommand
import requests

class Command(BaseCommand):
    help = 'Make an API request to convert currency'

    def handle(self, *args, **options):
        # Step 1: Obtain token (this is the same as before)
        url_token = 'http://localhost:8000/api/token/'
        credentials = {
            'username': 'elisha.matanga',   # Replace with valid username
            'password': 'Chamgiwadu!45'    # Replace with valid password
        }
        
        response_token = requests.post(url_token, data=credentials)
        
        if response_token.status_code == 200:
            access_token = response_token.json()['access']  # Get the access token from the response
            self.stdout.write(self.style.SUCCESS(f"Obtained Token: {access_token}"))
        else:
            self.stdout.write(self.style.ERROR(f"Failed to get token: {response_token.status_code}"))
            return  # Exit the command if the token is not obtained

        # Step 2: Use the token to make the currency conversion request
        url = 'http://localhost:8000/api/currency/convert'  # Ensure this is the correct endpoint
        headers = {
            'Authorization': f'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMxNjA0NDczLCJpYXQiOjE3MzE1ODY0NzMsImp0aSI6IjJiYzE3N2U1NmU4ZDRlMGU5OGQ5NTYzODY1MjM2NDRjIiwidXNlcl9pZCI6MX0.ha32CyNivM-6_iSGFh1UdjsmPkdBJYbLJ4uH87JjDwg'  # Include the obtained token here
        }

        # Step 3: Provide the required fields for currency conversion
        data = {
            'base_currency': 'USD',  # Correct field name for source currency
            'target_currency': 'EUR',  # Correct field name for target currency
            'amount': 100  # Correct field name for amount to convert
        }

        # Step 4: Make the POST request
        response = requests.post(url, headers=headers, data=data, verify=False)

        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS(f"Conversion Response: {response.json()}"))
        else:
            self.stdout.write(self.style.ERROR(f"Error: {response.status_code}, {response.text}"))


