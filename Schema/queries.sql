SELECT name, price, stock 
FROM products 
WHERE category_id = 1 
ORDER BY price DESC 
LIMIT 2;