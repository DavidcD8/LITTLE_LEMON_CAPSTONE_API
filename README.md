
# Little Lemon API

## Introduction

This project is a RESTful API for the Little Lemon restaurant for Meta Backend Proffesional Certificate(Coursera). It enables client applications (web and mobile) to interact with restaurant data, including menu items, orders, and user management. The API supports multiple user roles with different permissions: Manager, Delivery Crew, and Customer.

---

## Project Scope

- Full CRUD operations on menu items with role-based access
- User registration and token-based authentication (using Djoser)
- User group management for Manager and Delivery Crew roles
- Cart and order management for customers
- Filtering, sorting, and pagination on menu items and orders
- API throttling for rate limiting
- Proper HTTP status codes and error handling

---

## Technology Stack

- Django
- Django REST Framework (DRF)
- Djoser (Authentication)
- pipenv (Dependency and virtual environment management)

---

## Setup Instructions

1. Clone the repository

   ```bash
   git clone <repository_url>
   cd LittleLemonAPI
   ```

2. Install dependencies and activate the virtual environment

   ```bash
   pipenv install
   pipenv shell
   ```

3. Run database migrations

   ```bash
   python manage.py migrate
   ```

4. Create a superuser

   ```bash
   python manage.py createsuperuser
   ```

5. Start the development server

   ```bash
   python manage.py runserver
   ```

6. Access the admin panel at [http://localhost:8000/admin](http://localhost:8000/admin)  
   - Create user groups: `Manager`, `Delivery crew`  
   - Add users and assign to groups as needed

---

## User Roles

- **Manager:** Full control over menu items, user group assignments, and order management.
- **Delivery Crew:** Can view and update delivery status of assigned orders.
- **Customer:** Can browse menu items, manage cart, place orders, and view their own orders.

Users without a group are treated as Customers by default.

---

## API Endpoints

### Authentication & User Management (Djoser)

| Endpoint               | Role          | Method | Description                        |
|------------------------|---------------|--------|----------------------------------|
| `/api/users`           | Public        | POST   | Register new user                 |
| `/api/users/users/me/` | Authenticated | GET    | Get current user details          |
| `/token/login/`        | Public        | POST   | Obtain authentication token       |

---

### Menu Items

| Endpoint                  | Role              | Method          | Description                      |
|---------------------------|-------------------|-----------------|---------------------------------|
| `/api/menu-items`          | Customer, Delivery | GET             | List all menu items             |
| `/api/menu-items/{id}`     | Customer, Delivery | GET             | Retrieve a single menu item     |
| `/api/menu-items`          | Manager           | GET, POST       | List and create menu items      |
| `/api/menu-items/{id}`     | Manager           | GET, PUT, PATCH, DELETE | Retrieve, update, or delete item |

Non-managers get `403 Unauthorized` for modifying menu items.

---

### User Group Management (Manager only)

| Endpoint                             | Method | Description                          |
|------------------------------------|--------|------------------------------------|
| `/api/groups/manager/users`         | GET    | List all managers                   |
| `/api/groups/manager/users`         | POST   | Add user to manager group           |
| `/api/groups/manager/users/{id}`    | DELETE | Remove user from manager group      |
| `/api/groups/delivery-crew/users`   | GET    | List delivery crew                  |
| `/api/groups/delivery-crew/users`   | POST   | Add user to delivery crew group     |
| `/api/groups/delivery-crew/users/{id}` | DELETE | Remove user from delivery crew group |

---

### Cart Management (Customer only)

| Endpoint                  | Method | Description                         |
|---------------------------|--------|-----------------------------------|
| `/api/cart/menu-items`     | GET    | View current user's cart items    |
| `/api/cart/menu-items`     | POST   | Add a menu item to cart           |
| `/api/cart/menu-items`     | DELETE | Remove all items from user's cart |

---

### Order Management

| Endpoint                  | Role           | Method        | Description                        |
|---------------------------|----------------|---------------|----------------------------------|
| `/api/orders`             | Customer       | GET, POST     | List user's orders and create order |
| `/api/orders/{orderId}`   | Customer       | GET, PUT, PATCH | Retrieve or update own order      |
| `/api/orders`             | Manager        | GET           | List all orders                   |
| `/api/orders/{orderId}`   | Manager        | DELETE        | Delete an order                  |
| `/api/orders`             | Delivery Crew  | GET           | List orders assigned to delivery crew |
| `/api/orders/{orderId}`   | Delivery Crew  | PATCH         | Update order status (deliveries) |

---

## Additional Features

- Filtering, searching, and pagination on `/api/menu-items` and `/api/orders`
- Throttling for authenticated and anonymous users to limit API requests
- Proper HTTP status codes and error messages for invalid requests

---

## HTTP Status Codes Used

| Status Code | Meaning                          |
|-------------|---------------------------------|
| 200 OK      | Successful GET, PUT, PATCH, DELETE |
| 201 Created | Successful POST request          |
| 401 Forbidden | User authentication failed      |
| 403 Unauthorized | Authorization failed          |
| 400 Bad Request | Validation errors              |
| 404 Not Found | Resource does not exist         |

---
