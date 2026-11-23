# Open POS REST API Reference & Postman Guide

A streamlined, practical guide for using and testing the Open POS REST API with Postman. This document covers authentication, all core endpoints, the Task module (CRUD, filtering, ordering, and field masking via query parameters), and instructions for capturing the required error response screenshots.

---

## 1. Quick Setup & Postman Variables

Set up these collection-level variables in Postman so your URLs remain clean and dynamic:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `base_url` | `http://127.0.0.1:5000` | Root host for Flask-Admin routes (`/admin/...`) |
| `auth_base_url` | `http://127.0.0.1:5000/api/v1` | Base URL for versioned REST API endpoints (`/api/v1/...`) |
| `auth_token` | *(Leave empty)* | Auto-saved by the `login-user` test script |
| `user_id` | *(Leave empty)* | Auto-saved by `login-user` |
| `task_id` | *(Leave empty)* | Auto-saved by `create-task` |

---

## 2. Authentication: How to Get & Attach Your Token

Most REST endpoints require you to be authenticated:

1. **Login Request:** Send a `POST` request to `{{auth_base_url}}/login/` with your credentials:
   ```json
   {
     "email": "admin@pos.com",
     "password": "admin123"
   }
   ```
2. **Auto-Save Token (Postman Test Script):**
   In your `login-user` request, under the **Scripts > Post-response** (or **Tests**) tab:
   ```javascript
   const res = pm.response.json();
   if (res.authentication_token) {
       pm.collectionVariables.set("auth_token", res.authentication_token);
   }
   if (res.id) {
       pm.collectionVariables.set("user_id", res.id);
   }
   ```
3. **Attach Header:**
   All protected requests include:
   - `Authentication-Token: {{auth_token}}`
   - `Authorization: {{auth_token}}`

---

## 3. Endpoints Overview (Clean Collection)

The collection contains 13 streamlined requests matching your exact Postman workspace:

| # | Request Name | Method | URL Path | Auth Required? | Payload |
|---|:--- |:---: |:--- |:---: |:--- |
| 1 | **register-user** | `POST` | `{{auth_base_url}}/register/` | No | raw JSON |
| 2 | **login-user** | `POST` | `{{auth_base_url}}/login/` | No | raw JSON |
| 3 | **get-products** | `GET` | `{{base_url}}/admin/product` | Yes (Admin) | None (HTML) |
| 4 | **get-retail_shop_page** | `GET` | `{{base_url}}/admin/retailshop/` | Yes (Admin) | None (HTML) |
| 5 | **get-all-user** | `GET` | `{{auth_base_url}}/user` | Yes (`admin`/`owner`) | None (Query Params) |
| 6 | **get-role** | `GET` | `{{auth_base_url}}/role` | Yes | None |
| 7 | **create-user** | `POST` | `{{base_url}}/admin/user/new/` | Yes (Admin) | `form-data` |
| 8 | **create-role** | `POST` | `{{base_url}}/admin/role/new/` | Yes (Admin) | `form-data` |
| 9 | **create-task** | `POST` | `{{auth_base_url}}/tasks/` | Yes | raw JSON |
| 10 | **get-task** | `GET` | `{{auth_base_url}}/tasks/` | Yes | None (Query Params) |
| 11 | **get-task-byId** | `GET` | `{{auth_base_url}}/task/{{task_id}}/` | Yes | None |
| 12 | **update-task-byId** | `PATCH` | `{{auth_base_url}}/task/{{task_id}}/` | Yes | raw JSON |
| 13 | **delete-task** | `DELETE`| `{{auth_base_url}}/task/{{task_id}}/` | Yes | None |

---

## 4. Query Parameters in `get-task` & `get-all-user`

Instead of creating separate requests for filtering and pagination, use the **Params** tab in Postman to enable or disable query parameters via checkboxes:

### Available Query Parameters for `get-task` (`GET {{auth_base_url}}/tasks/`):

| Parameter Key | Value Example | Checkbox | Purpose |
|:--- |:--- |:---: |:--- |
| `__only` | `title,id` | **Checked** | **Field Masking:** Returns only the specified attributes in the JSON response. |
| `__page` | `1` | Unchecked | **Pagination:** Specific page number to display (default: 1). |
| `__limit` | `10` | Unchecked | **Page Size:** Maximum items per page (default: 50, max: 100). |
| `__status__equal` | `pending` | Unchecked | **Exact Filter:** Filters tasks by status (`pending`, `in_progress`, `done`). |
| `__order_by` | `-created_on` | Unchecked | **Ordering:** Sorts by column name. Prefix with `-` for descending order. |
| `__title__contains` | `Report` | Unchecked | **Search:** Case-sensitive substring search in title. |

> [!TIP]
> **Example URL with `__only`**:
> `{{auth_base_url}}/tasks/?__only=title,id`
> Returns only `id` and `title` without `description`, `created_on`, or `user_id`.

---

## 5. Detailed Endpoint Reference

### 1. Register User (`register-user`)
- **Method:** `POST`
- **URL:** `{{auth_base_url}}/register/`
- **Body (`raw JSON`):**
  ```json
  {
    "email": "staff01@pos.com",
    "password": "password123",
    "name": "Staff Member",
    "mobile_number": "9876500001"
  }
  ```
- **Success (`200 OK`):**
  ```json
  {
    "response": {
      "user": {
        "id": "c1f7a014-bf4c-473d-82d2-5a9e14e1a0b3",
        "email": "staff01@pos.com"
      }
    }
  }
  ```

---

### 2. Login User (`login-user`)
- **Method:** `POST`
- **URL:** `{{auth_base_url}}/login/`
- **Body (`raw JSON`):**
  ```json
  {
    "email": "admin@pos.com",
    "password": "admin123"
  }
  ```
- **Success (`200 OK`):**
  ```json
  {
    "id": "552c97d8-1a93-420f-b56f-8d5a5045d6dc",
    "authentication_token": "WyI1NTJjOTdkOC0xYTkzLTQyMGYtYjU2Zi04ZDVhNTA0NWQ2ZGMi...=="
  }
  ```

---

### 3. Get All Users (`get-all-user`)
- **Method:** `GET`
- **URL:** `{{auth_base_url}}/user`
- **Headers:** `Authentication-Token: {{auth_token}}`
- **Success (`200 OK`):** Returns paginated list of user records.

---

### 4. Create Task (`create-task`)
- **Method:** `POST`
- **URL:** `{{auth_base_url}}/tasks/`
- **Headers:**
  - `Authentication-Token: {{auth_token}}`
  - `Content-Type: application/json`
- **Body (`raw JSON`):**
  ```json
  {
    "title": "Prepare End of Month Sales Report",
    "description": "Compile report for retail brand shops",
    "status": "pending",
    "due_date": "2026-11-30T18:00:00",
    "user_id": "{{user_id}}"
  }
  ```
- **Success (`201 Created`):**
  ```json
  {
    "data": [
      {
        "id": "7b822d87-34f1-4db4-bb14-9b841a1a5209",
        "title": "Prepare End of Month Sales Report",
        "status": "pending",
        "due_date": "2026-11-30T18:00:00",
        "user_id": "552c97d8-1a93-420f-b56f-8d5a5045d6dc",
        "created_on": "2026-11-20T12:15:30.123456"
      }
    ],
    "message": "Resource added successfully",
    "success": true
  }
  ```

---

### 5. Get Tasks (`get-task`)
- **Method:** `GET`
- **URL:** `{{auth_base_url}}/tasks/?__only=title,id`
- **Headers:** `Authentication-Token: {{auth_token}}`
- **Success (`200 OK`):**
  ```json
  {
    "data": [
      {
        "id": "7b822d87-34f1-4db4-bb14-9b841a1a5209",
        "title": "Prepare End of Month Sales Report"
      }
    ],
    "success": true,
    "total": 1
  }
  ```

---

### 6. Get Task by ID (`get-task-byId`)
- **Method:** `GET`
- **URL:** `{{auth_base_url}}/task/{{task_id}}/`
- **Headers:** `Authentication-Token: {{auth_token}}`
- **Success (`200 OK`):** Returns full task JSON object.

---

### 7. Update Task by ID (`update-task-byId`)
- **Method:** `PATCH` (or `PUT`)
- **URL:** `{{auth_base_url}}/task/{{task_id}}/`
- **Headers:**
  - `Authentication-Token: {{auth_token}}`
  - `Content-Type: application/json`
- **Body (`raw JSON`):**
  ```json
  {
    "status": "in_progress",
    "description": "Report compilation started, numbers verified"
  }
  ```
- **Success (`200 OK`):** Returns updated task object.

---

### 8. Delete Task (`delete-task`)
- **Method:** `DELETE`
- **URL:** `{{auth_base_url}}/task/{{task_id}}/`
- **Headers:** `Authentication-Token: {{auth_token}}`
- **Success (`204 No Content`):** Empty body with status 204.

---

