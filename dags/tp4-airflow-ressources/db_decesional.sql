CREATE TABLE dim_customers (
  customer_id SERIAL PRIMARY KEY,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  phone_number VARCHAR(20),
  address_line1 VARCHAR(255),
  address_line2 VARCHAR(255),
  city VARCHAR(255),
  state VARCHAR(255),
  zip_code VARCHAR(10)
);

CREATE TABLE dim_products (
  product_id SERIAL PRIMARY KEY,
  product_name VARCHAR(255),
  description TEXT,
  category VARCHAR(255),
  price DECIMAL(10, 2)
);

CREATE TABLE dim_employees (
  employee_id SERIAL PRIMARY KEY,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  role VARCHAR(255)
);

CREATE TABLE fact_sales (
  sale_id SERIAL PRIMARY KEY,
  customer_id INTEGER REFERENCES dim_customers(customer_id),
  product_id INTEGER REFERENCES dim_products(product_id),
  employee_id INTEGER REFERENCES dim_employees(employee_id),
  quantity INTEGER NOT NULL,
  discount DECIMAL(10, 2),
  total_amount DECIMAL(10, 2) NOT NULL
);