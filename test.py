import json
import unittest
from components import app
from datetime import datetime

testapp = app.test_client()
create_url = "/create"
update_url = "/update"
get_url = "/get"
get_specific_file_url = "/get?{query_params}"
delete_url = "/delete"
post_content_type = "application/json"


class TestInvalid(unittest.TestCase):
    def test_invalid_file_type(self):
        resp_register = testapp.post(create_url, data=json.dumps(dict({"fileTypeCode": 100})),
                                     content_type=post_content_type)
        data_register = json.loads(resp_register.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')

    def test_valid_file_type_with_invalid_metadata(self):
        resp_register = testapp.post(create_url, data=json.dumps(dict({"fileTypeCode": 1})),
                                     content_type=post_content_type)
        data_register = json.loads(resp_register.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')

    def test_valid_file_type_with_invalid_duration(self):
        now = datetime.now()
        data = dict({"fileTypeCode": 1,
                     "name": "test_song",
                     "duration": -67,
                     "uploadedTime": now.isoformat()})
        resp_register = testapp.post(create_url, data=json.dumps(data), content_type=post_content_type)
        data_register = json.loads(resp_register.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')

    def test_valid_file_type_with_invalid_time(self):
        now = datetime.now()
        data = dict({"fileTypeCode": 1,
                     "name": "test_song",
                     "duration": 67,
                     "uploadedTime": "12"})
        resp_register = testapp.post(create_url, data=json.dumps(data), content_type=post_content_type)
        data_register = json.loads(resp_register.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')

    def test_valid_file_type_with_invalid_file_type(self):
        now = datetime.now()
        data = dict({"fileTypeCode": 100,
                     "name": "test_song",
                     "duration": 67,
                     "uploadedTime": now.isoformat()})
        resp_register = testapp.post(create_url, data=json.dumps(data), content_type=post_content_type)
        data_register = json.loads(resp_register.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')

    def test_invalid_update_song_file(self):
        now = datetime.now()
        data = dict({"fileTypeCode": 1,
                     "name": "test_song",
                     "duration": 70,
                     "uploadedTime": now.isoformat()})
        resp_register = testapp.patch(update_url, data=json.dumps(data), content_type=post_content_type,
                                      query_string={"id": 1})
        data_register = json.loads(resp_register.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')


class TestValid(unittest.TestCase):
    def test_valid_create_song_file(self):
        now = datetime.now()
        data = dict({"fileTypeCode": 1,
                     "name": "test_song",
                     "duration": 90,
                     "uploadedTime": now.isoformat()})
        resp_register = testapp.post(create_url, data=json.dumps(data), content_type=post_content_type)
        data_register = json.loads(resp_register.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')

    def test_valid_update_song_file(self):
        now = datetime.now()
        data = dict({"fileTypeCode": 1,
                     "name": "test_song_2",
                     "duration": 70,
                     "uploadedTime": now.isoformat()})
        resp_register = testapp.patch(update_url, data=json.dumps(data), content_type=post_content_type,
                                      query_string={"id": 2})
        data_register = json.loads(resp_register.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')

    def test_valid_create_audio_file(self):
        now = datetime.now()
        data = dict({"fileTypeCode": 2,
                     "name": "test_audio",
                     "duration": 100,
                     "uploadedTime": now.isoformat(),
                     "audioBookTitleAuthor": "Author1",
                     "audioBookNarrator": "Narrator1"})
        resp_register = testapp.post(create_url, data=json.dumps(data), content_type=post_content_type)
        data_register = json.loads(resp_register.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')

    def test_valid_update_audio_file(self):
        now = datetime.now()
        data = dict({"fileTypeCode": 2,
                     "name": "test_audio",
                     "duration": 9886,
                     "uploadedTime": now.isoformat(),
                     "audioBookTitleAuthor": "Author134",
                     "audioBookNarrator": "Narrator678"})
        resp_register = testapp.patch(update_url, data=json.dumps(data), content_type=post_content_type,
                                      query_string={"id": 13})
        data_register = json.loads(resp_register.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')

    def test_valid_create_podcast_file(self):
        now = datetime.now()
        data = dict({"fileTypeCode": 3,
                     "name": "podcast_morn_34",
                     "duration": 8989,
                     "uploadedTime": now.isoformat(),
                     "podcastHost": "host876",
                     "podcastParticipants": ["participant1", "participant78"]})
        resp_register = testapp.post(create_url, data=json.dumps(data), content_type=post_content_type)
        data_register = json.loads(resp_register.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')

    def test_valid_update_podcast_file(self):
        now = datetime.now()
        data = dict({"fileTypeCode": 3,
                     "name": "podcast_test_333",
                     "duration": 54,
                     "uploadedTime": now.isoformat(),
                     "podcastHost": "host199",
                     "podcastParticipants": ["participant9", "participant4", "abc"]})
        resp_register = testapp.patch(update_url, data=json.dumps(data), content_type=post_content_type, query_string={"id": 23})
        data_register = json.loads(resp_register.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')

    def test_valid_get_all_files(self):
        response = testapp.get(get_url)
        data_register = json.loads(response.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')

    def test_valid_get_specific_file(self):
        response = testapp.get(get_url, query_string={"id": 24})
        data_register = json.loads(response.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')

    def test_valid_delete_specific_file(self):
        response = testapp.delete(delete_url, query_string={"id": 24})
        data_register = json.loads(response.data.decode())
        print(data_register)
        self.assertTrue(data_register['status_code'] == '200')
