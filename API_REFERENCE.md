# Open POS API Reference
This document provides a complete guide to the Open POS API endpoints included in your Postman collection. It explains how to authenticate, how to pass tokens between requests, and details each endpoint's method, parameters, request body, sample responses, and error codes.
---
## 1. Environment & Variables
Set up these variables in your Postman Collection or Environment:
| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `base_url` | `http://127.0.0.1:5000` | Base server URL for root & admin endpoints |
| `auth_base_url` | `http://127.0.0.1:5000/api/v1` | Base URL for REST API v1 endpoints |
---
## 2. Authentication Flow
The API uses **token-based authentication** for REST endpoints and **session/cookie authentication** for Admin Panel views.

### How to use the token in Postman:
1. Call **`POST {{base_url}}/api/v1/login/`** with your credentials.
2. Copy the `authentication_token` string from the JSON response.
3. On protected endpoints (`/api/v1/user`, `/api/v1/role`, etc.), open the **Headers** tab and add:
   - **Key**: `Authorization`
   - **Value**: `<your_authentication_token>`
> Then on protected requests, set the `Authorization` header value to `{{auth_token}}`.
---
## 3. Endpoints Overview
| Request Name | Method | Full URL | Format | Auth Required |
| :--- | :--- | :--- | :--- | :--- |
| **register-user** | `POST` | `{{auth_base_url}}/register/` | JSON | No |
| **login-user** | `POST` | `{{auth_base_url}}/login/` | JSON | No |
| **get-all-user** | `GET` | `{{auth_base_url}}/user` | JSON | Yes (`Authorization`) |
| **get-role** | `GET` | `{{auth_base_url}}/role` | JSON | Yes (`Authorization`) |
| **create-user** | `POST` | `{{base_url}}/admin/user/new/` | `form-data` | Yes (Admin) |
| **create-role** | `POST` | `{{base_url}}/admin/role/new/` | `form-data` | Yes (Admin) |
| **get-products** | `GET` | `{{base_url}}/admin/product` | HTML | Yes (Admin) |
| **get-retail_shop_page** | `GET` | `{{base_url}}/admin/retailshop/` | HTML | Yes (Admin) |
---
## 4. API Endpoint Details
---
### 1. Register User (`register-user`)
Registers a new user account.
- **Method**: `POST`
- **URL**: `http://127.0.0.1:5000/api/v1/register/` (or `{{auth_base_url}}/register/`)
- **Headers**:
  - `Content-Type: application/json`
- **Authentication**: None (Public)
#### Request Body (`raw JSON`)
```json
{
  "email": "ali123456@gmail.com",
  "password": "12345678",
  "name": "Arashad Ali",
  "mobile_number": "9878878787"
}
```
#### Success Response (`200 OK`)
```json
{
  "response": {
    "user": {
      "id": "c1f7a014-bf4c-473d-82d2-5a9e14e1a0b3",
      "email": "ali123456@gmail.com"
    }
  }
}
```
#### Error Codes
| Status Code | Reason | Cause |
| :--- | :--- | :--- |
| `400 Bad Request` | Validation Error | Email already registered, invalid email format, or password missing |
| `409 Conflict` | Integrity Error | Mobile number or email already exists in DB |
---

### 2. Login User (`login-user`)
Authenticates a user and generates an auth token for API calls.

- **Method**: `POST`
- **URL**: `{{base_url}}/api/v1/login/` (or `{{base_url}}/login/`)
- **Headers**:
  - `Content-Type: application/json`
- **Authentication**: None (Public)

#### Request Body (`raw JSON`)
```json
{
  "email": "aliarshad0786@gmail.com",
  "password": "12345678"
}
```
#### Success Response (`200 OK`)
```json
{
  "id": "910cc9da-26e4-45bf-a784-4d395a35a210",
  "authentication_token": "Your Auth Token"
}
```
#### Error Codes
| Status Code | Reason | Description |
| :--- | :--- | :--- |
| `403 Forbidden` | `{"meta": {"code": 403}}` | Incorrect email or password |
| `400 Bad Request` | Missing Fields | Missing email or password in request body |
---

### 3. Get All Users (`get-all-user`)
Retrieves a paginated list of users accessible to the current authenticated user's retail brand.

- **Method**: `GET`
- **URL**: `{{auth_base_url}}/user`
- **Headers**:
  - `Authorization: <authentication_token>`
- **Authentication**: Required (`admin`, `owner`, or `staff` role)
- **Optional Query Parameters**:
  - `page`: Page number (e.g. `1`)
  - `limit`: Items per page (e.g. `10`)
  - `__order_by`: Order by field (`name`, `email`, `-id`)

#### Request Body
None.
#### Success Response (`200 OK`)
```json
{
  "data": [
    {
      "active": true,
      "brand_ids": [
        "1a4b6c8d-1234-4567-89ab-cdef01234567"
      ],
      "email": "aliarshad0786@gmail.com",
      "id": "910cc9da-26e4-45bf-a784-4d395a35a210",
      "name": "Admin User",
      "mobile_number": "9999999999",
      "roles": [
        {
          "id": "e932bce7-d2c9-4b67-938c-3088a8767980",
          "name": "admin"
        }
      ],
      "retail_shops": [
        {
          "id": "d027f329-a1b2-4c3d-9e4f-56789abcdef0",
          "name": "Main Shop"
        }
      ]
    }
  ],
  "success": true,
  "total": 1
}
```
#### Error Codes
| Status Code | Reason | Description |
| :--- | :--- | :--- |
| `401 Unauthorized` | Invalid / Missing Token | Authorization header missing or expired |
| `403 Forbidden` | Permission Denied | User does not have `admin`, `owner`, or `staff` role |
| `404 Not Found` | No Resource Found | No users match the given filter criteria |
---
### 4. Get Roles (`get-role`)
Retrieves all defined roles in the POS system.

- **Method**: `GET`
- **URL**: `{{auth_base_url}}/role`
- **Headers**:
  - `Authorization: <authentication_token>`
- **Authentication**: Required

#### Request Body
None.

#### Success Response (`200 OK`)
```json
{
  "data": [
    {
      "id": "e932bce7-d2c9-4b67-938c-3088a8767980",
      "name": "admin",
      "permissions": [
        {
          "id": "52f95c10-fa92-4f0e-884e-41bcde219a12",
          "name": "create_product"
        }
      ]
    },
    {
      "id": "f821cde9-b1a4-4f32-841d-9102bcf54123",
      "name": "owner",
      "permissions": []
    },
    {
      "id": "cb3eef12-1a7a-4328-a869-e375ee4bccd4",
      "name": "staff",
      "permissions": []
    }
  ],
  "success": true,
  "total": 3
}
```
#### Error Codes
| Status Code | Reason | Description |
| :--- | :--- | :--- |
| `401 Unauthorized` | Token Missing | Missing or invalid `Authorization` header |
| `403 Forbidden` | Forbidden | Insufficient user permissions |

---
### 5. Create User (`create-user`)
Creates a new user via the Flask-Admin model form.

> [!IMPORTANT]
> **Form-Data vs JSON**:
> `/admin/user/new/` is a Flask-Admin Web form endpoint. It requires **`form-data`** (or `x-www-form-urlencoded`), **NOT raw JSON**. Sending raw JSON will fail validation and return the HTML page with status `200 OK` without inserting anything into the database.

- **Method**: `POST`
- **URL**: `{{base_url}}/admin/user/new/`
- **Headers**:
  - `Authorization: <authentication_token>` (and/or Admin session cookie)
- **Body Type**: `form-data`
- **Fields**:
  | Key | Type | Value | Required | Description |
  | :--- | :--- | :--- | :--- | :--- |
  | `name` | Text | `Naman` | Yes | Full Name |
  | `email` | Text | `naman01@gmail.com` | Yes | Unique Email |
  | `mobile_number` | Text | `998383747733` | Yes | Unique Mobile Number |
  | `password` | Text | `naman123` | Yes | User Password |
  | `active` | Text | `y` | No | Checkbox to activate user |
  | `retail_brand` | Text | *(brand UUID)* | No | Selected Retail Brand |

#### Success Response (`302 Found`)
- Redirects to `/admin/user/` after saving user record to PostgreSQL.

#### Error Codes
| Status Code | Result | Description |
| :--- | :--- | :--- |
| `200 OK` (with HTML) | Form Validation Failed | Sent JSON instead of `form-data`, or missing required fields. Renders HTML form with validation messages. |
| `403 Forbidden` | Access Denied | Logged in user does not have `admin` role. |

---

### 6. Create Role (`create-role`)
Creates a new system role using the Admin Panel endpoint.

- **Method**: `POST`
- **URL**: `{{base_url}}/admin/role/new/`
- **Headers**:
  - `Authorization: <authentication_token>` (and/or Admin session cookie)
- **Body Type**: `form-data`
- **Fields**:
  | Key | Type | Value | Description |
  | :--- | :--- | :--- | :--- |
  | `name` | Text | `staff` | Unique role name (e.g. `staff`, `cashier`, `manager`) |

#### Success Response (`302 Found`)
- Redirects to `/admin/role/` upon successful creation.

#### Error Codes
| Status Code | Description |
| :--- | :--- |
| `200 OK` (with HTML) | Role name already exists or field is empty |
| `403 Forbidden` | Current user is not an `admin` |

---

### 7. Get Products Page (`get-products`)
Fetches the Flask-Admin web page for product management.

- **Method**: `GET`
- **URL**: `{{base_url}}/admin/product`
- **Headers**:
  - `Authorization: <authentication_token>`
- **Response**: `200 OK` with full HTML table of products.
---
### 8. Get Retail Shop Page (`get-retail_shop_page`)
Fetches the Flask-Admin web view for retail shops.

- **Method**: `GET`
- **URL**: `{{base_url}}/admin/retailshop/`
- **Headers**:
  - `Authorization: <authentication_token>`
- **Response**: `200 OK` with HTML list of retail shops.

> [!NOTE]
> **REST API Alternative**: For JSON output, use:
> **`GET {{auth_base_url}}/retail_shop`** with `Authorization: <token>`.

---
## 5. Summary of Standard Status Codes
| Code | Status | Meaning |
| :---: | :--- | :--- |
| **`200`** | OK | Request was successful (or form redisplayed with validation error) |
| **`201`** | Created | Resource successfully created (JSON APIs) |
| **`302`** | Found | Redirect after successful form submission in Flask-Admin |
| **`400`** | Bad Request | Missing required parameters or invalid syntax |
| **`401`** | Unauthorized | Token missing, invalid, or expired |
| **`403`** | Forbidden | User credentials or role not permitted for this resource |
| **`404`** | Not Found | Resource or endpoint does not exist |
| **`500`** | Internal Server Error | Unhandled server or database exception |
