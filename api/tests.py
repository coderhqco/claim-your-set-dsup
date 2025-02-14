import datetime
from django.test import TestCase, Client
from .models import TestingModel
import datetime
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from vote.models import Group
from vote.models_secdel import SecDel


class TestingModelModelTest(TestCase):
    def setUp(self):
      self.t = TestingModel.objects.create(
        name='Taylor Swift',
        email='erastour@gmail.com',
        is_test=True,
        tagline='I am a singer',
        schedule_date=datetime.date(2019, 1, 1)  # Fix: Use datetime.date instead of datetime.datetime
      )
      global c
      c = Client()

    def test_testing_model_model_exists(self):
      testers = TestingModel.objects.count()

      self.assertEqual(testers, 1)

    def test_user_model_has_attributes(self):
        self.assertEqual(self.t.name, 'Taylor Swift')
        self.assertEqual(self.t.email, 'erastour@gmail.com')
        self.assertEqual(self.t.status, 0)
        self.assertEqual(self.t.is_test, True)
        self.assertEqual(self.t.tagline, 'I am a singer')
        self.assertEqual(self.t.schedule_date, datetime.date(2019, 1, 1))


#secDel API Tests
class SecDelViewTestCase(APITestCase):
    def setUp(self):
        #create a user and authenticate
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client = APIClient()
        self.client.login(username="testuser", password="testpassword")

        #create a group
        self.group = Group.objects.create(
            code="1234",
            district=None,                                          #add a district if necessary
            invitation_code="ABCD1234",
            group_type=1,
        )

        #create a SecDel instance
        self.secdel = SecDel.objects.create(
            circle=self.group,
            user=self.user
        )

    def test_create_secdel(self):
        data = {
            "circle": self.group.id,
            "user": self.user.id
        }
        response = self.client.post("/api/sec-del/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SecDel.objects.count(), 2)                 #one already exists in setUp

    def test_list_secdels(self):
        response = self.client.get("/api/sec-del/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)                     #only 1 record in setUp

    def test_retrieve_secdel(self):
        response = self.client.get(f"/api/sec-del/{self.secdel.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.secdel.id)

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get("/api/sec-del/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
