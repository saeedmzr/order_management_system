# order_management

Behold My Django Project!

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [Deployment](#deployment)
- [Switching Between Environments](#switching-between-environments)

## Features

- *User Authentication* : JWT token-based authentication

- *Role-Based Access Control* : Admin, staff

- *Order Management* : Create, read, update, and delete orders

- *Product Catalog* : Manage products 

- *Validation* : Comprehensive input validation for all operations

- *Documentation* : API documentation using drf-spectacular

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.10+** installed on your machine.
- **Virtualenv** or another method for managing virtual environments.
- **Docker** and **Docker Compose**.

## Installation

### 1. Clone the Repository

```bash
git clone [https://github.com/saeedmzr/order_management_system]
cd order_management
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

- For development:
    ```bash
    pip install -r requirements/local.txt
    ```

- For production:
    ```bash
    pip install -r requirements/production.txt
    ```

## Environment Variables

Create a `.env` file in the project root directory and add the required environment.
You can copy the `.env.example` file:

```bash
cp .env.example .env
```

To generate a unique `SECRET_KEY` and set it in your `.env` file, use the provided script.

```bash
python generate_secret_key.py
```

This script will:

- Copy the `.env.example` file to `.env` if `.env` does not already exist.
- Generate a unique `SECRET_KEY` and add it to the `.env` file, ensuring you have a secure key for your application.

## Database Migrations

Apply the migrations to set up your database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Deployment

To deploy the project using Docker Compose, run this:

- For development:
    ```bash
    docker compose up --build -d
    ```

- For production:
    ```bash
    docker compose -f docker-compose-production.yml up --build -d
    ```

## Switching Between Environments

To switch between development and production settings, modify the environment variable `DJANGO_SETTINGS_MODULE` when
running the application.

- For development:
    ```bash
    export DJANGO_SETTINGS_MODULE=order_management.settings.local
    ```

- For production:
    ```bash
    export DJANGO_SETTINGS_MODULE=order_management.settings.production
    ```



## API Endpoints
### Authentication
POST ```/api/auth/login/``` - Obtain JWT tokens

POST ```/api/auth/refresh/``` - Refresh access token

POST ```/api/auth/register/``` - Register new user

### Users
GET ```/api/users/``` - List users (admin only)

POST ```/api/users/``` - Create user (admin only)

GET ```/api/users/{id}/``` - Retrieve user

PATCH ```/api/users/{id}/``` - Update user

DELETE ```/api/users/{id}/``` - Delete user (admin only)

### Products
GET ```/api/products/``` - List all products

POST ```/api/products/``` - Create product (admin only)

GET ```/api/products/{id}/``` - Retrieve product

PATCH ```/api/products/{id}/``` - Update product (admin only)

DELETE ```/api/products/{id}/``` - Delete product (admin only)

### Orders
GET ```/api/orders/``` - List orders (own orders for customers, all for admin)

POST ```/api/orders/``` - Create new order

GET ```/api/orders/{id}/``` - Retrieve order details

PATCH ```/api/orders/{id}/``` - Update order (owner or admin)

DELETE ```/api/orders/{id}/``` - Delete order (owner or admin)