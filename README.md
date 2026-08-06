# RevoShop Database Setup

This repository contains the relational database design for RevoShop, an online store platform (featuring a car parts and modifications theme for the sample data). This project is part of the Full Stack Software Engineering (FSSE) Module 2 assignment.

## 📁 File Structure

- `schema.sql`: Contains Data Definition Language (DDL) scripts to create the database tables (`users`, `categories`, `products`, `orders`, `order_items`) and establish their relationships.
- `seed.sql`: Contains Data Manipulation Language (DML) scripts to populate the tables with initial sample data.
- `queries.sql`: Contains a sample testing query that combines `WHERE`, `ORDER BY`, and `LIMIT` clauses.
- `ERD_RevoShop.png`: A screenshot of the Entity-Relationship Diagram (ERD) illustrating the database schema.

## 🛠️ System Requirements

Before running the scripts in this repository, ensure you have the following installed:
1. **PostgreSQL** (local database server).
2. An SQL database management tool such as **DBeaver** or **pgAdmin**.

## 🐘 PostgreSQL Installation

1. **Install PostgreSQL 16+**. During the installation, make sure to set a password for the `postgres` superuser and note it down.
2. **Verify the installation** by running the following command in your terminal/command prompt:
   ```bash
   psql -U postgres -c "SELECT version();"
   ```

## 🚀 Local Setup Guide

Follow these steps to set up and load the database locally on your machine:

1. **Create a New Database**
   - Open DBeaver or pgAdmin.
   - Create a new database named `revoshop_db`.
   - Ensure you are connected to the `revoshop_db` database before proceeding to the next steps.

2. **Create the Table Schema**
   - Open the `schema.sql` file in your SQL Editor.
   - Execute the entire script to create the table structures and their relationships.

3. **Insert Sample Data**
   - Open the `seed.sql` file in your SQL Editor.
   - Execute the script to insert sample users, categories, products, orders, and order items into the newly created tables.

4. **Test the Queries (Optional)**
   - Open the `queries.sql` file in your SQL Editor.
   - Run the query to verify that the data has been successfully inserted and can be retrieved according to the specified conditions (e.g., retrieving the top 2 most expensive products in a specific category).