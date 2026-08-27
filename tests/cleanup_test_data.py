"""
Script untuk menghapus data dummy/test dari database.
Jalankan manual setelah test selesai:

    python cleanup_test_data.py
"""

from app import create_app, db
from app.models import Product, Category, User, Order, order_items

# Nama-nama product yang dibuat oleh test
TEST_PRODUCT_NAMES = [
    'Test Product',
    'Find Me Product',
    'Before Update',
    'After Update',
    'To Delete',
    'Order Test Product',
    'Low Stock Item',
    'Get Order Product',
    'Delete Order Product',
]

# Nama-nama category yang dibuat oleh test
TEST_CATEGORY_NAMES = [
    'Test Category',
    'Findable Category',
    'Old Name',
    'New Name',
    'To Delete Category',
]

# Email user yang dibuat oleh test
TEST_USER_EMAILS = [
    'newuser@test.com',
    'duplicate@test.com',
    'login@test.com',
    'wrongpw@test.com',
    'findme@test.com',
    'pytest_user@test.com',
]


def cleanup():
    app = create_app()
    with app.app_context():
        print("=== Cleanup Test Data ===\n")

        # 1. Hapus order items yang terkait dengan test products
        test_products = Product.query.filter(Product.name.in_(TEST_PRODUCT_NAMES)).all()
        test_product_ids = [p.id for p in test_products]

        if test_product_ids:
            deleted_items = db.session.execute(
                order_items.delete().where(order_items.c.product_id.in_(test_product_ids))
            )
            print(f"Deleted order_items terkait test products: {deleted_items.rowcount} rows")

        # 2. Hapus orders yang dibuat oleh test users
        test_users = User.query.filter(User.email.in_(TEST_USER_EMAILS)).all()
        test_user_ids = [u.id for u in test_users]

        if test_user_ids:
            # Hapus order_items dari orders milik test users
            test_orders = Order.query.filter(Order.user_id.in_(test_user_ids)).all()
            test_order_ids = [o.id for o in test_orders]

            if test_order_ids:
                deleted_oi = db.session.execute(
                    order_items.delete().where(order_items.c.order_id.in_(test_order_ids))
                )
                print(f"Deleted order_items dari test orders: {deleted_oi.rowcount} rows")

            deleted_orders = Order.query.filter(Order.user_id.in_(test_user_ids)).delete()
            print(f"Deleted test orders: {deleted_orders} rows")

        # 3. Hapus test products
        deleted_products = Product.query.filter(Product.name.in_(TEST_PRODUCT_NAMES)).delete()
        print(f"Deleted test products: {deleted_products} rows")

        # 4. Hapus products tanpa category (anomali dari test)
        no_cat_products = Product.query.filter(Product.category_id == None).delete()
        print(f"Deleted products tanpa category: {no_cat_products} rows")

        # 5. Hapus test categories
        deleted_categories = Category.query.filter(Category.name.in_(TEST_CATEGORY_NAMES)).delete()
        print(f"Deleted test categories: {deleted_categories} rows")

        # 6. Hapus test users
        deleted_users = User.query.filter(User.email.in_(TEST_USER_EMAILS)).delete()
        print(f"Deleted test users: {deleted_users} rows")

        db.session.commit()
        print("\n=== Cleanup selesai! ===")
        print(f"Sisa products: {Product.query.count()}")
        print(f"Sisa categories: {Category.query.count()}")
        print(f"Sisa users: {User.query.count()}")
        print(f"Sisa orders: {Order.query.count()}")


if __name__ == '__main__':
    cleanup()
