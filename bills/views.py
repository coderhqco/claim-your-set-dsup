from django.shortcuts import render
from django.http import JsonResponse
from .models import Bill
# Create your views here.
# create response from bill to send to front end 
def get_bills(request):
    bills = Bill.objects.all()
    bill_data = []
    for bill in bills:
        bill_data.append({
            'congress': bill.congress,
            'bill_number': bill.number,
            'origin_chamber': bill.origin_chamber,
            'origin_chamber_code': bill.origin_chamber_code,
            'title': bill.title,
            'bill_type': bill.bill_type,
            'update_date': bill.update_date,
            'update_date_including_text': bill.update_date_including_text,
            'url': bill.url,
            'latest_action_date': bill.latest_action_date,
            'latest_action_text': bill.latest_action_text,
            'district_tally': bill.dtally,
            'national_tally': bill.ntally,
            'id': bill.id,
            'voting_start': bill.voting_start,
            'voting_close': bill.voting_close,
            'schedule_date': bill.schedule_date,
            'text': bill.text,
            'advice': bill.advice,
        })
    return JsonResponse(bill_data, safe=False)