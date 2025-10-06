import unittest
import json
from app import app  # импортируем твое Flask-приложение

class PersonsApiTestCase(unittest.TestCase):
    def setUp(self):
        # создаём тестовый клиент Flask
        self.app = app.test_client()
        self.app.testing = True

    def test_add_person(self):
        response = self.app.post(
            '/api/v1/persons',
            data=json.dumps({
                "name": "Тест Тестович",
                "address": "Тестовск",
                "work": "Тестировщик",
                "age": 99
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        # data = json.loads(response.data)
        # self.assertIn("id", data)

    def test_get_all_persons(self):
        response = self.app.get('/api/v1/persons')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_get_person_not_found(self):
        response = self.app.get('/persons/9999')  # несуществующий id
        self.assertEqual(response.status_code, 404)

    def test_delete_person_not_found(self):
        response = self.app.delete('/persons/9999')
        self.assertEqual(response.status_code, 404)

    def test_update_person(self):
        # Сначала создаём человека
        post_response = self.app.post(
            '/api/v1/persons',
            data=json.dumps({
                "name": "Друг Тестовича",
                "address": "Тестовия",
                "work": "Не тестировщик",
                "age": 100
            }),
            content_type='application/json'
        )

        self.assertEqual(post_response.status_code, 201)
        # self.assertEqual(post_response.data, b'')  # тело пустое

        # Извлекаем ID из заголовка Location
        location = post_response.headers.get("Location")
        self.assertIsNotNone(location)
        person_id = int(location.rsplit('/', 1)[-1])

        # Теперь обновляем возраст
        patch_response = self.app.patch(
            f'/api/v1/persons/{person_id}',
            data=json.dumps({"age": 1}),
            content_type='application/json'
        )
        self.assertEqual(patch_response.status_code, 200)
        data = json.loads(patch_response.data)
        self.assertEqual(data["age"], 1)


if __name__ == '__main__':
    unittest.main()
