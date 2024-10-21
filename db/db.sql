CREATE DATABASE IF NOT EXISTS employee_data;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type VARCHAR(10) DEFAULT 'employee',  -- Using VARCHAR for user_type
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Create a table for user roles
CREATE TABLE  users_role (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL,
    role VARCHAR(50) NOT NULL
);