from django.db import models
from django.db.models import F
from django.db.models.functions import Cast
from django.db.models.expressions import Func
from model_utils import FieldTracker
from django.contrib.auth.models import User
# Create your models here.

class JSONIncrement(Func):
    function = "jsonb_set"

    def __init__(self, full_path, value=1, **extra):
        field_name, *key_path_parts = full_path.split("__")

        if not field_name:
            raise ValueError("`full_path` can not be blank.")

        if len(key_path_parts) < 1:
            raise ValueError("`full_path` must contain at least one key.")

        key_path = ",".join(key_path_parts)

        new_value_expr = Cast(
            Cast(F(full_path), IntegerField()) + value,
            CharField()
        )

        expressions = [
            F(field_name),
            Value(f"{{{key_path}}}"),
            Cast(new_value_expr, JSONField())
        ]

        super().__init__(*expressions, output_field=JSONField(), **extra)


class Bill(models.Model):

    dtally = models.JSONField(blank=True, default=dict)
    ntally = models.JSONField(blank=True, default=dict)
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

    @staticmethod
    # @database_sync_to_async  
    def update_district_tally(bill_number,vote_c_before,vote_c_after,district_code):
        path_after = f"dtally__{district_code}__{vote_c_after}"
        path_before = f"dtally__{district_code}__{vote_c_before}"
        Bill.objects.filter(number=bill_number).update(
            JSONIncrement(path_after, value=1),
            JSONIncrement(path_before, value=-1)
        )

    @staticmethod
    # @database_sync_to_async
    def update_national_tally(bill_number,vote_c_before,vote_c_after):
        path_before = f"ntally__{vote_c_before}"
        path_after = f"ntally__{vote_c_after}"
        Bill.objects.filter(number=bill_number).update(
            JSONIncrement(path_after, value=1),
            JSONIncrement(path_before, value=-1)
        )

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
    voted_by = models.BooleanField(default=False)
    your_vote = models.CharField(max_length=2, choices=VOTE_CHOICES, default='Px')
    vote_date = models.DateTimeField()
    last_update = models.DateTimeField()

    update_tracker = FieldTracker(fields=['your_vote'])

    def save(self, *args, **kwargs):
        if self.update_tracker.changed():
            self.last_update = timezone.now()
        super().save(*args, **kwargs)

