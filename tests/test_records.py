from datetime import datetime
from unittest import TestCase
from unittest.mock import Mock, patch
from pysplit.client import records


class TestRun(TestCase):
    entity_cls = records.Run
    json_data = {'some': 'data', 'start_time': '2017-04-13 12:00:00.000000', 'end_time': datetime(2017, 4, 13, 12, 10, 0)}
    stored_data = json_data.copy()
    stored_data['start_time'] = datetime(2017, 4, 13, 12)
    serialised_data = {
        'start_time': json_data['start_time'],
        'end_time': '2017-04-13 12:10:00.000000'
    }

    def setUp(self):
        self.entity = self.entity_cls(self.json_data)

    @patch('requests.get', return_value=Mock(json=Mock(return_value=[json_data])))
    def test_init(self, mocked_get):
        self.assertEqual(self.entity.data, self.stored_data)
        self.assertEqual(self.entity_cls(0).data, self.stored_data)
        self.assertEqual(self.entity_cls({}).data, {})

    def test_serialise(self):
        self.assertEqual(
            self.entity.serialise(),
            {'start_time': '2017-04-13 12:00:00.000000', 'end_time': '2017-04-13 12:10:00.000000'}
        )

    @patch('requests.post', return_value=Mock(json=Mock(return_value={'id': 0})))
    def test_post(self, mocked_post):
        self.assertEqual(self.entity.post(), 0)
        mocked_post.assert_called_with('http://localhost:5000/api/' + self.entity_cls.schema.name, json=self.serialised_data)

    @patch('requests.patch', return_value=Mock(json=Mock(return_value={'id': 0})))
    def test_patch(self, mocked_patch):
        self.entity.patch()
        mocked_patch.assert_called_with('http://localhost:5000/api/' + self.entity_cls.schema.name, json=self.serialised_data)

    def test_push(self):
        patched_patch = patch.object(self.entity_cls, 'patch')
        patched_post = patch.object(self.entity_cls, 'post', return_value=0)

        with patched_patch as mocked_patch, patched_post as mocked_post:
            self.entity.push()
            mocked_post.assert_called_with()
            self.assertEqual(self.entity.data['id'], 0)
            self.entity.push()
            mocked_patch.assert_called_with()
            self.assertEqual(mocked_post.call_count, 1)
            self.assertEqual(mocked_patch.call_count, 1)


class TestSplit(TestRun):
    entity_cls = records.Split
