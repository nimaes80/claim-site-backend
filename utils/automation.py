from rest_framework.test import APITestCase, APIRequestFactory
from random import choice, choices
from utils import test_utils
from rest_framework import status


class AutomationUpdateMixin:
    def test_update(self):
        obj = choice(self.objs)
        url = self.url + f'/{obj.id}/' + self.params

        mock_data = self.get_mock_data()
        response = test_utils.request_view(
            self.api_factory.put, url, self.user, mock_data,
            view=self.viewset, action='update', pk=obj.id)
        # ignore files checking
        mock_data = self.do_ignore(mock_data)

        self.check_item(response, mock_data, status_code=200)


class AutomationCreateMixin:
    def test_create(self):
        mock_data = self.get_mock_data()
        url = self.url + self.params
        response = test_utils.request_view(
            self.api_factory.post, url, self.user, mock_data,
            view=self.viewset, action='create')

        # ignore files checking
        mock_data = self.do_ignore(mock_data)
        self.check_item(response, mock_data, status_code=201)


class AutomationPartialUpdateMixin:
    def test_partial_update(self):
        obj = choice(self.objs)
        url = self.url + f'/{obj.id}/' + self.params

        mock_data = self.get_mock_data(True)

        response = test_utils.request_view(
            self.api_factory.patch, url, self.user, mock_data,
            view=self.viewset, action='partial_update', pk=obj.id)

        # ignore files checking
        mock_data = self.do_ignore(mock_data)

        self.check_item(response, mock_data, status_code=200)


class AutomationRetrieveMixin:
    def test_retrieve(self):
        obj = choice(self.objs)
        url = self.url + f'/{obj.id}/' + self.params
        response = test_utils.request_view(
            self.api_factory.get, url, self.user, None,
            view=self.viewset, action='retrieve', pk=obj.id
        )
        data = self.serializer.get_fields()
        # ignore files checking

        data = self.do_ignore(data)
        response.data = self.do_ignore(response.data)

        self.assert_response_keywords(
            response, data, type='reverse_include'
        )


class AutomationListMixin:
    def test_list(self):
        response = test_utils.request_view(
            self.api_factory.get, self.url, self.user, None,
            view=self.viewset, action='list'
        )
        test_utils.assert_num_of_pages_count_status_code(
            self, response, status.HTTP_200_OK,
            self.CREATE_SIZE/self.PAGE_SIZE, self.CREATE_SIZE
        )


class AutomationDeleteMixin:
    def test_delete(self):
        obj = choice(self.objs)
        url = self.url + f'/{obj.id}/' + self.params
        response = test_utils.request_view(
            self.api_factory.delete, url, self.user, None,
            view=self.viewset, action='destroy', pk=obj.id
        )
        self.assertEqual(response.status_code, 204)


class GenericTestAutomation(APITestCase, test_utils.AssertMixin):
    '''
        Just a simple automation class that provide some solution to make
        our life easier...

        used_model_fields format must like below dictionary
        {
            regulars: [ "foo", "bar", ...], <-- model_factory regular fields
            relateds: [ "foo2", "bar2", ] <-- model_factory related fields( just their id will send to endpoint )
        }

        NOTE:
            serializer object must be initialized.
            used_model_fields must contain required fields for endpoint.
    '''

    viewset = None
    model_factory = None
    CREATE_SIZE = 20
    PAGE_SIZE = 5
    used_model_fields = {
        'regulars': [], 'relateds': [], 'files': [],
    }
    user = None
    url = 'dummy_path/'  # not really need but it is good we have it...
    api_factory = APIRequestFactory()
    serializer = None
    objs = None
    params = ''
    ignore_fields = []

    def do_ignore(self, mock_data):
        for i in self.ignore_fields:
            mock_data.pop(i, None)
        for file_field in self.used_model_fields.get('files', []):
            mock_data.pop(file_field, None)
        return mock_data

    def get_mock_data(self, choice_random_field=False):
        # create fake data without insert to db
        mock_obj = self.model_factory.build()
        regulars = self.used_model_fields.get('regulars', [])
        relateds = self.used_model_fields.get('relateds', [])
        files = self.used_model_fields.get('files', [])

        if choice_random_field:
            if regulars:
                regulars = choices(regulars)
            if relateds:
                relateds = choices(relateds)

        # collect data from determain fields
        mock_data = {}
        for field in regulars:
            mock_data[field] = getattr(mock_obj, field)

        for field in files:
            mock_data[field] = getattr(mock_obj, field)

        for field in relateds:
            relation = getattr(mock_obj, field)
            if relation:
                mock_data[field] = relation.id

        return mock_data


class ModelTestAutomation(
        AutomationCreateMixin, AutomationDeleteMixin, AutomationListMixin,
        AutomationPartialUpdateMixin, AutomationRetrieveMixin, AutomationUpdateMixin,
        GenericTestAutomation):
    """A Automation for ModelViewset classes"""
