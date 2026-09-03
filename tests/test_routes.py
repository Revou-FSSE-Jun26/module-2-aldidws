"""
Test semua routes apakah berjalan dengan benar.
Jalankan dengan: pytest tests/test_routes.py -v
"""


# ============================================================
# HEALTH ROUTE
# ============================================================

class TestHealthRoute:
    def test_health_check(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'ok'


# ============================================================
# USER ROUTES
# ============================================================

class TestUserRoutes:
    def test_register_user_success(self, client):
        resp = client.post('/register', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'secret123'
        })
        assert resp.status_code in (201, 409)  # 409 if already exists

    def test_register_user_missing_fields(self, client):
        resp = client.post('/register', json={
            'username': 'incomplete'
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data

    def test_register_duplicate_email(self, client):
        # Register first time
        client.post('/register', json={
            'username': 'dup_user',
            'email': 'duplicate@test.com',
            'password': 'secret123'
        })
        # Register same email again
        resp = client.post('/register', json={
            'username': 'dup_user2',
            'email': 'duplicate@test.com',
            'password': 'secret456'
        })
        assert resp.status_code == 409

    def test_login_success(self, client):
        # Register first
        client.post('/register', json={
            'username': 'loginuser',
            'email': 'login@test.com',
            'password': 'mypassword'
        })
        # Login
        resp = client.post('/auth/login', json={
            'email': 'login@test.com',
            'password': 'mypassword'
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'token' in data
        assert 'user' in data

    def test_login_wrong_password(self, client):
        # Register first
        client.post('/register', json={
            'username': 'wrongpw',
            'email': 'wrongpw@test.com',
            'password': 'correct'
        })
        # Login with wrong password
        resp = client.post('/auth/login', json={
            'email': 'wrongpw@test.com',
            'password': 'incorrect'
        })
        assert resp.status_code == 401

    def test_login_missing_fields(self, client):
        resp = client.post('/auth/login', json={
            'email': 'test@test.com'
        })
        assert resp.status_code == 400

    def test_get_all_users(self, client):
        resp = client.get('/users')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_get_single_user_found(self, client):
        # Register a user first
        reg_resp = client.post('/register', json={
            'username': 'findme',
            'email': 'findme@test.com',
            'password': 'secret'
        })
        if reg_resp.status_code == 201:
            user_id = reg_resp.get_json()['id']
        else:
            # Already exists, get from users list
            users = client.get('/users').get_json()
            user_id = users[0]['id']

        resp = client.get(f'/users/{user_id}')
        assert resp.status_code == 200

    def test_get_single_user_not_found(self, client):
        resp = client.get('/users/99999')
        assert resp.status_code == 404


# ============================================================
# PRODUCT ROUTES
# ============================================================

class TestProductRoutes:
    def test_get_hardcoded_products(self, client):
        resp = client.get('/products/hardcoded')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 5

    def test_get_all_products(self, client):
        resp = client.get('/products')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_create_product_success(self, client):
        resp = client.post('/products', json={
            'name': 'Test Product',
            'price': 50000,
            'stock': 10
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['name'] == 'Test Product'

    def test_create_product_missing_fields(self, client):
        resp = client.post('/products', json={
            'name': 'Incomplete'
        })
        assert resp.status_code == 400

    def test_get_product_by_id(self, client):
        # Create a product first
        create_resp = client.post('/products', json={
            'name': 'Find Me Product',
            'price': 10000,
            'stock': 5
        })
        product_id = create_resp.get_json()['id']

        resp = client.get(f'/products/{product_id}')
        assert resp.status_code == 200
        assert resp.get_json()['name'] == 'Find Me Product'

    def test_get_product_not_found(self, client):
        resp = client.get('/products/99999')
        assert resp.status_code == 404

    def test_update_product(self, client):
        # Create first
        create_resp = client.post('/products', json={
            'name': 'Before Update',
            'price': 10000,
            'stock': 5
        })
        product_id = create_resp.get_json()['id']

        # Update
        resp = client.put(f'/products/{product_id}', json={
            'name': 'After Update',
            'price': 20000
        })
        assert resp.status_code == 200
        assert resp.get_json()['product']['name'] == 'After Update'

    def test_update_product_not_found(self, client):
        resp = client.put('/products/99999', json={'name': 'Ghost'})
        assert resp.status_code == 404

    def test_delete_product(self, client):
        # Create a product to delete
        create_resp = client.post('/products', json={
            'name': 'To Delete',
            'price': 5000,
            'stock': 1
        })
        product_id = create_resp.get_json()['id']

        resp = client.delete(f'/products/{product_id}')
        assert resp.status_code == 200

    def test_delete_product_not_found(self, client):
        resp = client.delete('/products/99999')
        assert resp.status_code == 404


# ============================================================
# CATEGORY ROUTES
# ============================================================

class TestCategoryRoutes:
    # ---------- GET all (happy path) ----------
    def test_get_all_categories(self, client):
        # Seed at least one category so the list is non-trivial
        client.post('/categories', json={'name': 'Seeded Category'})

        resp = client.get('/categories')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Each item should expose the expected shape
        first = data[0]
        assert 'id' in first
        assert 'name' in first

    # ---------- POST (happy path) ----------
    def test_create_category_success(self, client):
        resp = client.post('/categories', json={
            'name': 'Test Category',
            'description': 'A test category'
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['name'] == 'Test Category'
        assert data['description'] == 'A test category'
        assert 'id' in data

    # ---------- POST (error cases) ----------
    def test_create_category_missing_name(self, client):
        resp = client.post('/categories', json={
            'description': 'No name'
        })
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data
        assert 'name' in data['error'].lower()

    def test_create_category_empty_body(self, client):
        resp = client.post('/categories', json={})
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data
        assert data['error']

    # ---------- GET by id (happy path) ----------
    def test_get_category_by_id(self, client):
        # Create category first
        create_resp = client.post('/categories', json={
            'name': 'Findable Category'
        })
        category_id = create_resp.get_json()['id']

        resp = client.get(f'/categories/{category_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['id'] == category_id
        assert data['name'] == 'Findable Category'
        # GET by id must include the category's products list
        assert 'products' in data
        assert isinstance(data['products'], list)

    def test_get_category_by_id_includes_products(self, client):
        # Create category and a product linked to it
        cat_resp = client.post('/categories', json={'name': 'Category With Product'})
        category_id = cat_resp.get_json()['id']

        client.post('/products', json={
            'name': 'Linked Product',
            'price': 12345,
            'stock': 7,
            'category_id': category_id
        })

        resp = client.get(f'/categories/{category_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data['products'], list)
        assert any(p['name'] == 'Linked Product' for p in data['products'])

    # ---------- GET by id (error case) ----------
    def test_get_category_not_found(self, client):
        resp = client.get('/categories/99999')
        assert resp.status_code == 404
        data = resp.get_json()
        assert 'error' in data
        assert data['error']

    # ---------- PUT (happy path) ----------
    def test_update_category(self, client):
        # Create first
        create_resp = client.post('/categories', json={
            'name': 'Old Name',
            'description': 'Old description'
        })
        category_id = create_resp.get_json()['id']

        resp = client.put(f'/categories/{category_id}', json={
            'name': 'New Name',
            'description': 'New description'
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'message' in data
        assert data['category']['name'] == 'New Name'
        assert data['category']['description'] == 'New description'

        # Confirm the change persisted
        get_resp = client.get(f'/categories/{category_id}')
        assert get_resp.get_json()['name'] == 'New Name'

    # ---------- PUT (error cases) ----------
    def test_update_category_not_found(self, client):
        resp = client.put('/categories/99999', json={'name': 'Ghost'})
        assert resp.status_code == 404
        data = resp.get_json()
        assert 'error' in data
        assert data['error']

    def test_update_category_empty_body(self, client):
        create_resp = client.post('/categories', json={'name': 'Keep Me'})
        category_id = create_resp.get_json()['id']

        resp = client.put(f'/categories/{category_id}', json={})
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'error' in data
        assert data['error']

    # ---------- DELETE (happy path) ----------
    def test_delete_category(self, client):
        create_resp = client.post('/categories', json={
            'name': 'To Delete Category'
        })
        category_id = create_resp.get_json()['id']

        resp = client.delete(f'/categories/{category_id}')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'message' in data
        assert data['message']

        # Confirm it is really gone
        get_resp = client.get(f'/categories/{category_id}')
        assert get_resp.status_code == 404

    # ---------- DELETE (error case) ----------
    def test_delete_category_not_found(self, client):
        resp = client.delete('/categories/99999')
        assert resp.status_code == 404
        data = resp.get_json()
        assert 'error' in data
        assert data['error']


# ============================================================
# ORDER ROUTES
# ============================================================

class TestOrderRoutes:
    def test_get_orders_without_token(self, client):
        """Should return 401 without auth token."""
        resp = client.get('/orders')
        assert resp.status_code == 401

    def test_create_order_without_token(self, client):
        """Should return 401 without auth token."""
        resp = client.post('/orders', json={'items': []})
        assert resp.status_code == 401

    def test_get_orders_with_token(self, client, auth_headers):
        """Should return 200 with valid token."""
        resp = client.get('/orders', headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_create_order_missing_items(self, client, auth_headers):
        """Should return 400 when items are missing."""
        resp = client.post('/orders', json={}, headers=auth_headers)
        assert resp.status_code == 400

    def test_create_order_success(self, client, auth_headers):
        """Create a product then place an order."""
        # Create a product with stock
        prod_resp = client.post('/products', json={
            'name': 'Order Test Product',
            'price': 25000,
            'stock': 100
        })
        product_id = prod_resp.get_json()['id']

        # Place order
        resp = client.post('/orders', json={
            'items': [{'product_id': product_id, 'quantity': 2}]
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['order']['total_amount'] == 50000

    def test_create_order_insufficient_stock(self, client, auth_headers):
        """Should return 400 when stock is not enough."""
        # Create a product with low stock
        prod_resp = client.post('/products', json={
            'name': 'Low Stock Item',
            'price': 10000,
            'stock': 1
        })
        product_id = prod_resp.get_json()['id']

        # Try to order more than available
        resp = client.post('/orders', json={
            'items': [{'product_id': product_id, 'quantity': 999}]
        }, headers=auth_headers)
        assert resp.status_code == 400
        assert 'stock' in resp.get_json()['error'].lower()

    def test_create_order_product_not_found(self, client, auth_headers):
        """Should return 404 for non-existent product."""
        resp = client.post('/orders', json={
            'items': [{'product_id': 99999, 'quantity': 1}]
        }, headers=auth_headers)
        assert resp.status_code == 404

    def test_get_order_by_id(self, client, auth_headers):
        """Create an order then retrieve it."""
        # Create product
        prod_resp = client.post('/products', json={
            'name': 'Get Order Product',
            'price': 15000,
            'stock': 50
        })
        product_id = prod_resp.get_json()['id']

        # Create order
        order_resp = client.post('/orders', json={
            'items': [{'product_id': product_id, 'quantity': 1}]
        }, headers=auth_headers)
        order_id = order_resp.get_json()['order']['id']

        # Get order by ID
        resp = client.get(f'/orders/{order_id}', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['id'] == order_id
        assert 'items' in data

    def test_get_order_not_found(self, client, auth_headers):
        resp = client.get('/orders/99999', headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_order(self, client, auth_headers):
        """Create an order then soft-delete it."""
        # Create product
        prod_resp = client.post('/products', json={
            'name': 'Delete Order Product',
            'price': 5000,
            'stock': 50
        })
        product_id = prod_resp.get_json()['id']

        # Create order
        order_resp = client.post('/orders', json={
            'items': [{'product_id': product_id, 'quantity': 1}]
        }, headers=auth_headers)
        order_id = order_resp.get_json()['order']['id']

        # Delete order
        resp = client.delete(f'/orders/{order_id}', headers=auth_headers)
        assert resp.status_code == 200

    def test_delete_order_not_found(self, client, auth_headers):
        resp = client.delete('/orders/99999', headers=auth_headers)
        assert resp.status_code == 404

    def test_invalid_token(self, client):
        """Should return 401 with invalid token."""
        headers = {'Authorization': 'Bearer invalid.token.here'}
        resp = client.get('/orders', headers=headers)
        assert resp.status_code == 401
