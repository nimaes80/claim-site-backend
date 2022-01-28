from datetime import datetime
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.test import force_authenticate

from account.models import User


def equal_assertion(object_ref, list_assertions=None):
    list_assertions = object_ref.list_of_assertions if list_assertions is None else list_assertions
    for pair in list_assertions:
        object_ref.assertEqual(pair[0], pair[1])


def assert_object_not_found_404(test_ref, response):
    list_of_assertions = [
        [response.status_code, status.HTTP_404_NOT_FOUND],
        [response.data['detail'], 'Not found.'],
        [response.data['detail'].code, 'not_found']
    ]
    equal_assertion(test_ref, list_of_assertions)


def assert_number_of_objects(test_ref, response, object_count, list_of_object_ids, id_or_pk='id'):
    list_of_ids = []
    for index in range(len(response.data.get('data'))):
        list_of_ids.append(response.data.get('data')[index][id_or_pk])
    list_of_assertions = [
        [response.status_code, status.HTTP_200_OK],
        [response.data.get('count'), object_count]
    ]
    equal_assertion(test_ref, list_of_assertions)
    if list_of_object_ids[0] != list_of_ids[0]:
        list_of_ids.reverse()
    test_ref.assertCountEqual(list_of_ids, list_of_object_ids)


def assert_num_of_pages_count_status_code(test_ref, response, status_code, num_of_pages, object_count):
    list_of_assertions = [
        [response.status_code, status_code],
        [response.data['num_of_pages'], num_of_pages],
        [response.data['count'], object_count]
    ]
    equal_assertion(test_ref, list_of_assertions)


def assert_deleted_object(test_ref, response, object_ref=None):
    test_ref.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    if object_ref:
        test_ref.assertTrue(object_ref.deleted)


def assert_unauthenticated(test_ref, response):
    list_of_assertions = [
        [response.status_code, status.HTTP_401_UNAUTHORIZED],
        [response.data['detail'], 'Authentication credentials were not provided.'],
        [response.data['detail'].code, 'not_authenticated']
    ]
    equal_assertion(test_ref, list_of_assertions)
    test_ref.assertTrue(response.exception)


def assert_name_project(test_ref, response, status_code, name, project_pk):
    list_of_assertions = [
        [response.status_code, status_code],
        [response.data.get('name'), name],
        [response.data.get('project'), project_pk],
    ]
    equal_assertion(test_ref, list_of_assertions)


def assert_name_project_var_type(test_ref, response, project_pk, name, var_type, status_code):
    list_of_assertions = [
        [response.status_code, status_code],
        [response.data.get('name'), name],
        [response.data.get('project'), project_pk],
        [response.data.get('var_type'), var_type]
    ]
    equal_assertion(test_ref, list_of_assertions)


def assert_access_token_and_expiration(test_ref, response):
    test_ref.assertTrue(response.data.get('access'))
    test_ref.assertIsInstance(response.data.get('access'), str)
    test_ref.assertTrue(response.data.get('expire_date'))


def assert_invalid_token(test_ref, response):
    detail = response.data['detail']
    code = response.data['code']
    list_of_assertions = [
        [response.status_code, status.HTTP_401_UNAUTHORIZED],
        [detail, 'Token is invalid or expired'],
        [detail.code, 'token_not_valid'],
        [code, 'token_not_valid'],
        [code.code, 'token_not_valid']
    ]
    equal_assertion(test_ref, list_of_assertions)


def request_view(factory_method, url, user, data, view, action=None,
                 authenticated=True, request_format='multipart', **kwargs):
    request = factory_method(path=url, data=data, format=request_format)

    if authenticated:
        force_authenticate(request, user)
    if action:
        response = view.as_view({request.method.lower(): action})(request, **kwargs)
    else:
        response = view.as_view()(request, **kwargs)
    return response


def create_user(username, email, password):
    return User.objects.create(username=username, email=email, password=make_password(password))


def create_admin(username, email, password):
    return User.objects.create(username=username, email=email, is_staff=True, is_superuser=True, is_active=True,
                               password=make_password(password))


def create_active_user(username, email, password):
    return User.objects.create(username=username, email=email, is_active=True,
                               password=make_password(password))


def create_inactive_user(username, email, password):
    return User.objects.create(username=username, email=email, is_active=False,
                               password=make_password(password))


class AssertMixin:
    def assert_response(self, response, data, status_code=200, type='exact'):
        self.assertEqual(response.status_code, status_code)
        if type == 'exact':
            self.assertEqual(response.data, data)
        elif type == 'include':
            for item in data.keys():
                self.assertEqual(data[item], response.data.get(item))
        elif type == 'exclude':
            self.assertTrue(all(item not in response.data.items() for item in data.items()))

    def check_item(self, response, data, status_code=200):
        self.assertEqual(response.status_code, status_code)
        for i in data.keys():
            if isinstance(data[i], datetime):
                data[i] = data[i].strftime("%Y-%m-%dT%H:%M:%SZ")

            self.assertEqual(response.data[i], data[i])

    def assert_response_keywords(self, response, data, status_code=200, type='exact'):
        self.assertEqual(response.status_code, status_code)
        if type == 'exact':
            self.assertListEqual(list(response.data.keys()), list(data))
        elif type == 'include':
            for i in data:
                if i not in response.data.keys():
                    self.assertEqual(True, False)
                    return
            self.assertEqual(True, True)
        elif type == 'exclude':
            for i in data:
                if i in response.data.keys():
                    self.assertEqual(True, False)
                    return
            self.assertEqual(True, True)
