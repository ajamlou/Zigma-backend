from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import UserProfile
from rest_framework import status
from rest_framework.test import APIRequestFactory as factory

class AccountsTest(APITestCase):
    def setUp(self):
        # Skapa en initial test user
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        UserProfile.objects.create(user=self.test_user)

        # URL för å skapa acc
        self.create_url = reverse('user-list')
        self.login_url = reverse('api-token-auth')

    def test_create_user(self):
        """
        Ensure we can create a new user and a valid token is created with it.
        """
        data = {
            'username': 'foobar',
            'email': 'foobar@example.com',
            'password': 'somepassword',
            'profile_picture': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFhAJ/wlseKgAAAABJRU5ErkJggg=='
            }

        response = self.client.post(self.create_url , data, format='json')

        # Kolla så att 2 users finns i db
        self.assertEqual(User.objects.count(), 2)
        # status =201 bör returneras
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Vi vill få tillbaka id, username och email
        self.assertEqual(response.data['id'], 2)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])

        #Vi vill inte få tillbaka vårt password
        self.assertFalse('password' in response.data)

        #vi bör ha 2 user profiles, en som skapades explicit i setup och en implicit i denna metod
        self.assertEqual(UserProfile.objects.count(),2)

        #Kolla så vi har en bild reggad hos user foobar
        self.assertEqual(bool(UserProfile.objects.get(user=response.data['id']).image), True)

    def test_fail_create_user_same_username(self):
        data = {
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'somepassword',}

        response = self.client.post(self.create_url , data, format='json')

        # Kolla så att 1 user finns i db
        self.assertEqual(User.objects.count(), 1)
        # status =400 bör returneras
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fail_create_user_same_email(self):
        data = {
            'username': 'testuser2',
            'email': 'test@example.com',
            'password': 'somepassword',}

        response = self.client.post(self.create_url , data, format='json')

        # Kolla så att 1 user finns i db
        self.assertEqual(User.objects.count(), 1)
        # status =400 bör returneras
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        data = {
            'username':'testuser',
            'password':'testpassword'
        }
        response = self.client.post(self.login_url , data, format='json')

        #Se till så vi for status = 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #Och att en token returneras
        self.assertTrue('token' in response.data)

    def test_login_fail_wrong_username(self):
        data = {
            'username':'wrongusername',
            'password':'testpassword'
        }
        response = self.client.post(self.login_url , data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_fail_wrong_password(self):
        data = {
            'username':'testuser',
            'password':'wrongpassword'
        }
        response = self.client.post(self.login_url , data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
