from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Bill(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    congress = models.IntegerField()
    number = models.CharField(max_length=50)
    origin_chamber = models.CharField(max_length=50)
    origin_chamber_code = models.CharField(max_length=3)
    title = models.CharField(max_length=200)
    bill_type = models.CharField(max_length=10)
    update_date = models.DateField()
    update_date_including_text = models.DateTimeField()
    url = models.URLField()
    latest_action_date = models.DateField()
    latest_action_text = models.TextField()
    voting_start = models.DateField(blank=True, null=True)
    voting_close = models.DateField(blank=True, null=True)
    schedule_date = models.DateField(blank=True, null=True)
    text = models.TextField()
    advice = models.TextField()

    class Meta:
        ordering = ('-created_at',)
    

class BillVote(models.Model):

    VOTE_CHOICES = [
        ('Y', 'Yea'),
        ('N', 'Nay'),
        ('Pr', 'Present'),
        ('Px', 'Proxy'),
    ]

    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    voter = models.ForeignKey(User, on_delete=models.CASCADE)

    voted_by_fDel = models.BooleanField(default=False)
    your_vote = models.CharField(max_length=2, choices=VOTE_CHOICES, default='Px')
    vote_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)


