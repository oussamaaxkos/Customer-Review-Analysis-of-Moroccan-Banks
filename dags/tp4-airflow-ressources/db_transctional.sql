CREATE TABLE customers (
  customer_id SERIAL PRIMARY KEY,
  first_name VARCHAR(255) NOT NULL,
  last_name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE,
  phone_number VARCHAR(20),
  address_line1 VARCHAR(255),
  address_line2 VARCHAR(255),
  city VARCHAR(255),
  state VARCHAR(255),
  zip_code VARCHAR(10)
);

CREATE TABLE products (
  product_id SERIAL PRIMARY KEY,
  product_name VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(255),
  price DECIMAL(10, 2) CHECK (price > 0)
);

CREATE TABLE employees (
  employee_id SERIAL PRIMARY KEY,
  first_name VARCHAR(255) NOT NULL,
  last_name VARCHAR(255) NOT NULL,
  role VARCHAR(255)
);

CREATE TABLE sales (
  sale_id SERIAL PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
  product_id INTEGER NOT NULL REFERENCES products(product_id),
  employee_id INTEGER NOT NULL REFERENCES employees(employee_id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  sale_date DATE NOT NULL,
  discount DECIMAL(10, 2) CHECK (discount >= 0 AND discount <= 1),
  total_amount DECIMAL(10, 2) NOT NULL
);
