-- Insert data users
INSERT INTO users (username, email, password_hash) VALUES
('Abdul Hafidz', 'Abdul@example.com', 'hashed_pw_123'),
('Nadas Kahfi', 'Nadas@example.com', 'hashed_pw_456'),
('Hanif Adhi', 'Hanif@example.com', 'hashed_pw_789');

-- Insert data categories
INSERT INTO categories (name, description) VALUES
('Wheels and Tires', 'Aftermarket alloy wheels, rims, and performance tires'),
('Performance Exhaust', 'High performance exhaust systems, headers, and mufflers'),
('Engine Maintenance', 'Engine oils, fluids, hoses, and replacement parts');

-- Insert data products
INSERT INTO products (category_id, name, description, price, stock) VALUES
(1, 'BBS RS 17-inch Alloy Wheels', 'Classic multi-piece wheels for a retro stance', 15000000, 4),
(1, 'Volk Rays TE37 18-inch Forged Wheels', 'Lightweight forged wheels for track use', 25000000, 4),
(2, 'Stainless Steel Catback Exhaust for E36', 'Free-flowing exhaust system for better sound and performance', 5500000, 5),
(3, 'High-Performance 10W-40 Synthetic Oil 1L', 'Premium engine oil for high mileage engines like the M50', 150000, 24),
(3, 'Premium Power Steering Fluid', 'High-quality fluid for smooth steering response', 120000, 15);

-- Insert data orders
INSERT INTO orders (user_id, total_amount) VALUES
(1, 25000000),
(3, 5800000);

-- Insert data order items
INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES
(1, 2, 1, 25000000),
(2, 3, 1, 5500000),
(2, 4, 2, 150000);