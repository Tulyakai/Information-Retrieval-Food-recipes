import unittest
import requests
unittest.TestLoader.sortTestMethodsUsing = None

class FlaskTestCase(unittest.TestCase):
    base_url = 'http://127.0.0.1:5000'

    def testRegister(self):
        res = requests.post('http://127.0.0.1:5000/register', json={'username': 'test', 'password': 'test'})
        self.assertEqual(200 ,res.status_code)

    def testRegisterFail(self):
        res = requests.post('http://127.0.0.1:5000/register')
        self.assertEqual(400 ,res.status_code)

    def testLogin(self):
        res = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'})
        self.assertEqual(200, res.status_code)

    def testLoginFail(self):
        res = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'tllest'})
        self.assertEqual(400, res.status_code)

    def testSearchTitle(self):
        token = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'}).json()['token']
        res = requests.post('http://127.0.0.1:5000/search-title', json={'query': 'chicken'}, headers={'Authorization': token})
        self.assertEqual(200, res.status_code)

    def testSearchTitleFailToken(self):
        res = requests.post('http://127.0.0.1:5000/search-title', json={'query': 'chicken'})
        self.assertEqual(403, res.status_code)

    def testSearchTitleFailBody(self):
        token = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'}).json()['token']
        res = requests.post('http://127.0.0.1:5000/search-title', headers={'Authorization': token})
        self.assertEqual(500, res.status_code)

    def testSearchIngredients(self):
        token = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'}).json()['token']
        res = requests.post('http://127.0.0.1:5000/search-ingredients', json={'query': 'chicken'}, headers={'Authorization': token})
        self.assertEqual(200, res.status_code)

    def testSearchIngredientsFailToken(self):
        res = requests.post('http://127.0.0.1:5000/search-ingredients', json={'query': 'chicken'})
        self.assertEqual(403, res.status_code)

    def testSearchTitleFailBody(self):
        token = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'}).json()['token']
        res = requests.post('http://127.0.0.1:5000/search-ingredients', headers={'Authorization': token})
        self.assertEqual(500, res.status_code)

    def testGetMenuId(self):
        token = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'}).json()['token']
        res = requests.get('http://127.0.0.1:5000/getMenu/1', headers={'Authorization': token})
        self.assertEqual(200, res.status_code)

    def testGetMenuIdFailToken(self):
        res = requests.get('http://127.0.0.1:5000/getMenu/11')
        self.assertEqual(403, res.status_code)

    def testGetMenuIdFailNotFound(self):
        token = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'}).json()['token']
        res = requests.get('http://127.0.0.1:5000/getMenu/11111111', headers={'Authorization': token})
        self.assertEqual(404, res.status_code)

    def testGetAllMenu(self):
        token = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'}).json()['token']
        res = requests.get('http://127.0.0.1:5000/getAllMenu/1', headers={'Authorization': token})
        self.assertEqual(200, res.status_code)

    def testGetAllFailToken(self):
        res = requests.get('http://127.0.0.1:5000/getAllMenu/1')
        self.assertEqual(403, res.status_code)

    def testAddBookmark(self):
        data = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'})
        token = data.json()['token']
        user_id = data.json()['user']['id']
        res = requests.post('http://127.0.0.1:5000/add-bookmark', json={'user_id': user_id, 'menu_id':3}, headers={'Authorization': token})
        self.assertEqual(200, res.status_code)

    def testAddBookmarkFailToken(self):
        data = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'})
        user_id = data.json()['user']['id']
        res = requests.post('http://127.0.0.1:5000/add-bookmark', json={'user_id': user_id, 'menu_id':2})
        self.assertEqual(403, res.status_code)

    def testAddBookmarkFailBody(self):
        data = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'})
        token = data.json()['token']
        res = requests.post('http://127.0.0.1:5000/add-bookmark', headers={'Authorization': token})
        self.assertEqual(500, res.status_code)

    def testGetBookmark(self):
        data = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'})
        token = data.json()['token']
        user_id = data.json()['user']['id']
        res = requests.get('http://127.0.0.1:5000/get-bookmark', json={'user_id': user_id, 'menu_id':2}, headers={'Authorization': token})
        self.assertEqual(200, res.status_code)

    def testGetBookmarkFailToken(self):
        data = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'})
        user_id = data.json()['user']['id']
        res = requests.get('http://127.0.0.1:5000/get-bookmark', json={'user_id': user_id})
        self.assertEqual(403, res.status_code)

    def testGetBookmarkFailBody(self):
        data = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'})
        token = data.json()['token']
        res = requests.get('http://127.0.0.1:5000/get-bookmark', headers={'Authorization': token})
        self.assertEqual(500, res.status_code)

    def testSearchBookmark(self):
        data = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'})
        token = data.json()['token']
        user_id = data.json()['user']['id']
        res = requests.post('http://127.0.0.1:5000/search-bookmark', json={'user_id': user_id, 'query': 'chicken'} , headers={'Authorization': token})
        self.assertEqual(200, res.status_code)

    def testSearchBookmarkFailToken(self):
        data = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'})
        user_id = data.json()['user']['id']
        res = requests.post('http://127.0.0.1:5000/search-bookmark', json={'user_id': user_id, 'query': 'chicken'} )
        self.assertEqual(403, res.status_code)

    def testSearchBookmarkFailBody(self):
        data = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'})
        token = data.json()['token']
        user_id = data.json()['user']['id']
        res = requests.post('http://127.0.0.1:5000/search-bookmark', json={'user_id': user_id,},headers={'Authorization': token})
        self.assertEqual(500, res.status_code)

    def testRemoveBookmark(self):
        data = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'})
        token = data.json()['token']
        user_id = data.json()['user']['id']
        res = requests.post('http://127.0.0.1:5000/remove-bookmark', json={'user_id': user_id, 'menu_id':3}, headers={'Authorization': token})
        self.assertEqual(200, res.status_code)

    def testRemoveBookmarkFailToken(self):
        data = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'})
        user_id = data.json()['user']['id']
        res = requests.post('http://127.0.0.1:5000/remove-bookmark', json={'user_id': user_id, 'menu_id':3})
        self.assertEqual(403, res.status_code)

    def testRemoveBookmarkFailBody(self):
        data = requests.post('http://127.0.0.1:5000/auth', json={'username': 'test', 'password': 'test'})
        token = data.json()['token']
        res = requests.post('http://127.0.0.1:5000/remove-bookmark', headers={'Authorization': token})
        self.assertEqual(500, res.status_code)

if __name__ == '__main__':
    unittest.main()
