

test_users = {
    'manager': {
        'username': 'adminuser',
        'password': 'adminpassword',
        'role': 'manager',
    },
    'chef': {
        'username': 'chefuser',
        'password': 'chefpassword',
        'role': 'chef',
    },
    'waiter': {
        'username': 'waiteruser',
        'password': 'waiterpassword',
        'role': 'waiter',
    },
    'cashier': {
        'username': 'cashieruser',
        'password': 'cashierpassword',
        'role': 'cashier',
    }
}
class TestUserRoles(BaseTestCase):
    def getLoginToken(self, user):
        user = test_users.get(user)
        if not user:
            raise ValueError(f"User role '{user}' not found in test users.")
        response = self.client.post('/login', json={
            'username': user['username'],
            'password': user['password']
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        return data['token']
    
    def test_manager_access(self):
        token = self.getLoginToken('manager')
        self.client.set_header('Authorization', f'Bearer {token}')
        response = self.client.get('/api/manager')
        self.assertEqual(response.status_code, 200)
        self.assertIn('data', response.get_json())