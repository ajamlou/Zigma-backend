from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Advert
from user.models import UserProfile
from rest_framework import status
from rest_framework.test import APIRequestFactory as factory

class AdvertTest(APITestCase):
    def setUp(self):

        #Skapa en dummy-user som kan lägga upp adverts
        self.test_user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        UserProfile.objects.create(user=self.test_user)

        login_url = reverse('api-token-auth')
        self.create_url = reverse('advert-list')
        user_data = {
            'username':'testuser',
            'password':'testpassword'
        }
        response = self.client.post(login_url , user_data, format='json')
        self.auth_token = response.data['token']
        self.user_id = response.data['id']

        #Skapa en initial Advert
        self.initial_advert = Advert.objects.create(book_title='old title', price=120, owner=self.test_user)

    def test_create_advert(self):
        advert_data={
        'book_title':'new title',
        'price':150,
        'contact_info':'a@a.se'
        }
        self.client.force_authenticate(user=self.test_user)
        #Skapa en advert
        response = self.client.post(self.create_url, advert_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        #Säkerställ att vi har 2 adverts i db
        self.assertEqual(Advert.objects.count(), 2)

    def test_search_db(self):
        advert_data={
        'book_title':'new title',
        'price':150,
        'contact_info':'a@a.se'
        }
        self.client.force_authenticate(user=self.test_user)
        #Skapa en advert
        response = self.client.post(self.create_url, advert_data, format='json')
        #sök i db efter strängen 'title', bör hitta 2
        self.assertEqual(Advert.objects.filter(book_title__icontains='title').count(), 2)
        #Bör bara finnas 1 som heter old
        self.assertEqual(Advert.objects.filter(book_title__icontains='old').count(), 1)
        #och 1 som heter new
        self.assertEqual(Advert.objects.filter(book_title__icontains='new').count(), 1)

    def test_destroy_advert_fail(self):
        advert_data={
        'book_title':'new title',
        'price':150,
        'contact_info':'a@a.se'
        }
        #Skapa en advert
        self.client.force_authenticate(user=self.test_user)
        response = self.client.post(self.create_url, advert_data, format='json')

        self.client.force_authenticate(user=None)
        destroy_url = reverse('advert-detail', kwargs={'pk':self.initial_advert.id})
        response = self.client.delete(destroy_url)

        #Kolla så att vi får status = 401
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        #Kolla så att alla adverts finns kvar
        self.assertEqual(Advert.objects.filter(book_title__icontains='title').count(), 2)

    def test_destroy_advert_success(self):
        advert_data={
        'book_title':'new title',
        'price':150,
        'contact_info':'a@a.se'
        }
        self.client.force_authenticate(user=self.test_user)
        #Skapa en advert
        response = self.client.post(self.create_url, advert_data, format='json')

        self.client.force_authenticate(user=self.test_user)
        destroy_url = reverse('advert-detail', kwargs={'pk':self.initial_advert.id})
        response = self.client.delete(destroy_url)

        self.assertEqual(Advert.objects.filter(book_title__icontains='title').count(), 1)
        #Bör bara finnas 1 som heter old
        self.assertEqual(Advert.objects.filter(book_title__icontains='old').count(), 0)
        #och 1 som heter new
        self.assertEqual(Advert.objects.filter(book_title__icontains='new').count(), 1)
