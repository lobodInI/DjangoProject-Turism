import route.models
from django.test import TestCase, Client, RequestFactory
from route.views import route_add_event, route_add_review, route_info, event_info
from django.contrib.auth.models import User
from unittest.mock import patch


class CollectionMock:
    def find_one(self, *args, **kwargs):
        return {'points': [], 'accepted': [], 'pending': []}


class ClientMongoMock:
    def __init__(self, *args, **kwargs):
        pass

    def close(self):
        pass

    def __getitem__(self, item):
        return {'Stopping point': CollectionMock(),
                'event_users': CollectionMock()}


class TestRoute(TestCase):

    def test_route_filter(self):
        client = Client()
        response_get = client.get('/route/')
        result_1 = response_get.status_code
        self.assertEqual(200, result_1)

        new_place = route.models.Places(name='Lviv',
                                        name_country='Ukraine')
        new_place.save()
        new_route = route.models.Route(starting_point=1,
                                       stopping_point='a1b2c3d4e5f6g7h8',
                                       destination=1,
                                       country='Ukraine',
                                       location='Lviv',
                                       description='test route',
                                       duration=1,
                                       route_type='Car')
        new_route.save()
        response_post_1 = client.post('/route/', {'route_type': 'Car', 'country': 'Ukraine', 'location': 'Lviv'})
        result_post_1 = response_post_1.status_code
        self.assertEqual(200, result_post_1)
        find_items = list(route.models.Route.objects.all())
        result_find = len(find_items)
        self.assertEqual(1, result_find)

        response_post_2 = client.post('/route/', {'route_type': 'Car', 'country': 'ALL', 'location': ''})
        result_post_2 = response_post_2.status_code
        self.assertEqual(200, result_post_2)

        response_post_3 = client.post('/route/', {'route_type': 'ALL', 'country': 'Ukraine', 'location': ''})
        result_post_3 = response_post_3.status_code
        self.assertEqual(200, result_post_3)

        response_post_4 = client.post('/route/', {'route_type': 'ALL', 'country': 'ALL', 'location': 'Lviv'})
        result_post_4 = response_post_4.status_code
        self.assertEqual(200, result_post_4)

        response_post_5 = client.post('/route/', {'route_type': 'Car', 'country': 'ALL', 'location': 'Lviv'})
        result_post_5 = response_post_5.status_code
        self.assertEqual(200, result_post_5)

        response_post_6 = client.post('/route/', {'route_type': 'Car', 'country': 'Ukraine', 'location': ''})
        result_post_6 = response_post_6.status_code
        self.assertEqual(200, result_post_6)

        response_post_7 = client.post('/route/', {'route_type': 'ALL', 'country': 'Ukraine', 'location': 'Lviv'})
        result_post_7 = response_post_7.status_code
        self.assertEqual(200, result_post_7)

        response_post_8 = client.post('/route/', {'route_type': 'Foot', 'country': 'Poland', 'location': 'Warsaw'})
        result_post_8 = response_post_8.status_code
        self.assertEqual(404, result_post_8)

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='review_test',
                                             email='review_test',
                                             password='review_test')

    def test_info_route(self):
        client = Client()
        response_get = client.get('/route/info_route')
        result_get = response_get.status_code
        self.assertEqual(200, result_get)

    @patch('utils.mongo_utils.MongoClient', ClientMongoMock)
    def test_info_route_post(self):
        new_place = route.models.Places(name='Lviv',
                                        name_country='Ukraine')
        new_place.save()
        new_route = route.models.Route(starting_point=1,
                                       stopping_point='111111111111111111111111',
                                       destination=1,
                                       country='Ukraine',
                                       location='Lviv',
                                       description='test route',
                                       duration=1,
                                       route_type='Car')
        new_route.save()
        request = self.factory.post('/route/info_route', data={'id_route': 1})
        response_post = route_info(request)
        result_post = response_post.status_code
        self.assertEqual(200, result_post)
        find_items = list(route.models.Route.objects.all().filter(stopping_point='111111111111111111111111'))
        result_find = find_items[0].id
        self.assertEqual(1, result_find)

    def test_show_review(self):
        client = Client()
        response_get = client.get('/route/review')
        result_1 = response_get.status_code
        self.assertEqual(200, result_1)

        new_review = route.models.Review(route_id=5,
                                         review_text='Perfect travel',
                                         review_rate=9)
        new_review.save()
        client = Client()
        response_post = client.post('/route/review', {'id_route': 5})
        result_2 = response_post.status_code
        self.assertEqual(200, result_2)
        find_items = list(route.models.Review.objects.all().filter(review_text='Perfect travel'))
        result_find = find_items[0].route_id
        self.assertEqual(5, result_find)

    def test_add_review_anonim_user(self):
        client = Client()
        response_get = client.get('/route/review/add')
        result_1 = response_get.status_code
        self.assertEqual(401, result_1)

        response_post = client.post('/route/review/add')
        result_2 = response_post.status_code
        self.assertEqual(401, result_2)

    def test_add_review_authoriz_user(self):
        request_get = self.factory.get(f'/route/review/add')
        request_get.user = self.user
        response = route_add_review(request_get)
        result_1 = response.status_code
        self.assertEqual(200, result_1)

        request_post = self.factory.post(f'/route/review/add', {'id_route': 5,
                                                                'user_review': 'Perfect travel',
                                                                'user_rating': 9})
        request_post.user = self.user
        response = route_add_review(request_post)
        result_2 = response.status_code
        find_items = list(route.models.Review.objects.all().filter(route_id=5))
        result_3 = len(find_items)
        self.assertEqual(200, result_2)
        self.assertEqual(1, result_3)


class TestEvent(TestCase):

    def test_add_event_anonim_user(self):
        client = Client()
        response_get = client.get('/route/add_event')
        result_1 = response_get.status_code
        self.assertEqual(401, result_1)

        response_post = client.post('/route/add_event')
        result_2 = response_post.status_code
        self.assertEqual(401, result_2)

    def setUp(self):
        self.factory = RequestFactory()

        class UserMock:
            def has_perm(self, *args, **kwargs):
                return True

        self.user = UserMock()

    def test_add_event_with_auth_user(self):
        request = self.factory.post('/route/add_event', {'id_route': 10,
                                                         'start_date': "2022-12-12",
                                                         'price': 1111})
        request.user = self.user
        resource = route_add_event(request)
        result_1 = resource.status_code
        self.assertEqual(200, result_1)

        find_items = list(route.models.Event.objects.all().filter(price=1111))
        result_2 = find_items[0].id_route
        self.assertEqual(10, result_2)


class TestEventFixtures(TestCase):
    fixtures = ['route.json']

    def setUp(self):
        self.factory = RequestFactory()

    def test_event_info_get(self):
        request = self.factory.get('/route/info_event')
        response_get = event_info(request)
        result_get = response_get.status_code
        self.assertEqual(200, result_get)

    @patch('utils.mongo_utils.MongoClient', ClientMongoMock)
    def test_event_info_post(self):
        request = self.factory.post('/route/info_event', data={'id_event': 1})
        response_post = event_info(request)
        result_post_1 = response_post.status_code
        self.assertEqual(200, result_post_1)
        find_items = list(route.models.Event.objects.all().filter(id=1))
        result_post_2 = len(find_items)
        self.assertEqual(1, result_post_2)
