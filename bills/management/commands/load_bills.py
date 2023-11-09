from django.core.management.base import BaseCommand
from django.core.management import call_command
import requests
from bills.models import Bill


# to use this command, install requests with: pip install requests
# load the database by running: python manage.py load_bills
class Command(BaseCommand):
    help = 'Loads the first 100 bills from the Congress.gov API'
    
    def handle(self, *args, **kwargs):
        response = requests.get('https://api.congress.gov/v3/bill?api_key=DnseTQ0IKk3LXX4UuEkN4uyZROywuYAx0fZeQeSp&limit=250')
        bills = response.json()['bills']

        for bill in bills:
            Bill.objects.create(
                congress=bill['congress'],
                number=bill['number'],
                origin_chamber=bill['originChamber'],
                origin_chamber_code=bill['originChamberCode'],
                title=bill['title'],
                bill_type=bill['type'],
                # update_date=bill['updateDate'],
                # update_date_including_text=bill['updateDateIncludingText'],
                url=bill['url'],
                latest_action_date=bill['latestAction']['actionDate'],
                latest_action_text=bill['latestAction']['text'],
            )