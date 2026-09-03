from locust import HttpUser, task, between, events
import random
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


PRODUCT_IDS = list(range(8, 28))


def get_db_connection():
    """Get direct database connection for cleanup operations."""
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/revoshop_db')
    return psycopg2.connect(database_url)


@events.test_stop.add_listener
def cleanup_test_data(environment, **kwargs):
    print("\n[CLEANUP] Membersihkan data test dari database...")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Hapus order_items dari orders milik test users
        cur.execute("""
            DELETE FROM order_items
            WHERE order_id IN (
                SELECT o.id FROM orders o
                JOIN users u ON o.user_id = u.id
                WHERE u.email LIKE 'user_%@example.com'
            )
        """)
        order_items_deleted = cur.rowcount

        # Hapus orders milik test users
        cur.execute("""
            DELETE FROM orders
            WHERE user_id IN (
                SELECT id FROM users
                WHERE email LIKE 'user_%@example.com'
            )
        """)
        orders_deleted = cur.rowcount

        # Hapus test users
        cur.execute("DELETE FROM users WHERE email LIKE 'user_%@example.com'")
        users_deleted = cur.rowcount

        # Reset stock products ke nilai awal (optional - restore stock yang berkurang)
        cur.execute("UPDATE products SET stock = 1000 WHERE id BETWEEN 8 AND 28")

        conn.commit()
        cur.close()
        conn.close()

        print(f"[CLEANUP] Selesai! Dihapus: {users_deleted} users, {orders_deleted} orders, {order_items_deleted} order_items")
        print("[CLEANUP] Stock products di-reset ke 1000")

    except Exception as e:
        print(f"[CLEANUP] Error saat cleanup: {e}")
        if conn:
            conn.rollback()
            conn.close()


class ShoppingUser(HttpUser):

    wait_time = between(1, 3)

    def on_start(self):
        # Unique user per Locust instance to avoid conflicts
        user_id = id(self)
        self.email = f"user_{user_id}@example.com"
        self.username = f"testuser_{user_id}"

        # Register - 409 is expected if user already exists
        with self.client.post('/register', json={
            'username': self.username,
            'email': self.email,
            'password': 'secret123',
        }, catch_response=True) as response:
            if response.status_code in (201, 409):
                response.success()
            else:
                response.failure(f"Register failed: {response.status_code}")

        # Login to get JWT token
        with self.client.post('/auth/login', json={
            'email': self.email,
            'password': 'secret123',
        }, catch_response=True) as response:
            if response.status_code == 200:
                token = response.json().get('token')
                if token:
                    self.client.headers.update({
                        'Authorization': f'Bearer {token}'
                    })
                    response.success()
                else:
                    response.failure("Login 200 but no token in response")
            else:
                response.failure(f"Login failed: {response.status_code}")

    @task
    def shopping_journey(self):
        """Full required user journey, executed in sequence:
        1. GET all products
        2. GET a single product
        3. POST a new order
        4. GET the created order
        """
        # 1. GET all products
        with self.client.get("/products", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"GET /products failed: {response.status_code}")

        # 2. GET a single product
        product_id = random.choice(PRODUCT_IDS)
        with self.client.get(
            f"/products/{product_id}", name="/products/<id>", catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # Product id not present in this environment is acceptable
                response.success()
            else:
                response.failure(f"GET /products/<id> failed: {response.status_code}")

        # 3. POST a new order
        order_id = None
        with self.client.post("/orders", json={
            "items": [
                {"product_id": product_id, "quantity": 1}
            ]
        }, catch_response=True) as response:
            if response.status_code == 201:
                order_id = response.json().get("order", {}).get("id")
                response.success()
            elif response.status_code == 400 and "stock" in response.text.lower():
                # Out of stock is not a server error
                response.success()
            elif response.status_code == 404:
                # Chosen product not found -> cannot order it, not a server error
                response.success()
            else:
                response.failure(f"POST /orders failed: {response.status_code} - {response.text}")

        # 4. GET the created order
        if order_id:
            with self.client.get(
                f"/orders/{order_id}", name="/orders/<id>", catch_response=True
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"GET /orders/<id> failed: {response.status_code}")

    @task
    def view_my_orders(self):
        """GET list of user's orders."""
        self.client.get("/orders")
