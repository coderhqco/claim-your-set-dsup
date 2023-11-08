from django.shortcuts import render
from django.http import JsonResponse
from .models import Bill
from curses.ascii import NUL
from bills import models as billModels
from bills import serializers as billSerializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import api_view

from django.http import JsonResponse
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



class BillUpdate(generics.CreateAPIView):
    queryset = billModels.Bill.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = billSerializers.BillSerializer
    def create_update(self, serializer):
        bill_number = self.request.data.get('number')
        
        existing_record = billModels.Bill.objects.filter(number=bill_number).first()
        print(bill_number)
        if existing_record:
            # Update the existing record
            
            serializer.update(existing_record, serializer.validated_data)
        else:
            # Create a new record
            serializer.save()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.create_update(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class BillDelete(generics.DestroyAPIView):
    queryset = billModels.Bill.objects.all()   
    lookup_field = 'number'
    permission_classes = (AllowAny,)

    def delete(self, request, *args, **kwargs):
        bill_number = request.data.get('number')
        response = super().delete(request, *args, **kwargs)

        return response