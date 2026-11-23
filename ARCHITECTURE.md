# Open POS API – Architecture & Request Flow

This document outlines the architectural structure, request lifecycle, and modular design of the Open POS Flask REST API.

---

## 1. Project Structure & File Roles

### Directory Layout
```text
open-pos-api-master/
├── manager.py                   # App entrypoint & CLI commands (create-db, create-admin)
├── .env                         # Environment variables (DB URL, secret keys)
├── requirements.txt             # Project dependencies
├── migrations/                  # Database migration scripts (Flask-Migrate)
└── src/
    ├── __init__.py              # Central module registry & strict import sequence
    ├── config.py                # Environment configurations (Dev, Test, Prod)
    │
    ├── utils/                   # Shared framework core
    │   ├── factory.py           # Application Factory: create_app()
    │   ├── blue_prints.py       # Global API Blueprint (/api/v1)
    │   ├── api.py               # ApiFactory, @api.register(), BaseView, AssociationView
    │   ├── resource.py          # ModelResource & AssociationModelResource base classes
    │   ├── models.py            # db instance & BaseMixin (UUID id, audit timestamps)
    │   ├── schema.py            # ma instance & BaseSchema configuration
    │   ├── security.py          # Flask-Security setup & UserDatastore
    │   ├── methods.py           # Allowed HTTP action definitions (List, Fetch, Create, etc.)
    │   ├── operators.py         # Dynamic query filter operators (Equal, Contains, In, etc.)
    │   ├── exceptions.py        # Centralized custom API exceptions
    │   └── admin.py             # Flask-Admin initialization
    │
    ├── products/                # Catalog, categories, brands, stock
    ├── orders/                  # Orders, items, discounts, payments
    ├── user/                    # Users, roles, permissions, shops, customers
    ├── task/                    # Background & scheduled task management
    └── admin_panel/             # Flask-Admin backoffice views
```

### Role of Key Files

| File | Core Role |
|---|---|
| `manager.py` | Starts the app, loads environment config (`.env`), and defines Flask CLI commands (`create-db`, `create-admin`, `runserver`). |
| `src/__init__.py` | Central import registry that loads models, schemas, views, and security in a strict, non-circular order. |
| `src/utils/factory.py` | Contains `create_app()` factory function to configure Flask, register Blueprints, enable CORS, and bind extensions (`db`, `ma`, `api`, `security`, `admin`). |
| `src/utils/blue_prints.py` | Declares the primary API Blueprint (`pos`) with URL prefix `/api/v1`. |
| `src/utils/api.py` | Defines `ApiFactory` with `@api.register()` decorator and provides base classes `BaseView` and `AssociationView`. |
| `src/utils/security.py` | Configures Flask-Security authentication, tokens, user datastore, and custom registration forms. |

---

## 2. HTTP Request Execution Flow

Every API call follows this end-to-end processing pipeline:

```text
HTTP Request (e.g. POST /api/v1/task)
  │
  ▼
Blueprint (/api/v1)
  │
  ▼
flask_restful Resource (BaseView)
  │
  ▼
auth_token_required (Verifies Authorization token in request header)
  │
  ▼
roles_required / roles_accepted (Checks user role permissions)
  │
  ▼
Handler (get / post / put / patch / delete)
  │
  ▼
Marshmallow Schema (Validates & deserializes JSON via schema.load)
  │
  ▼
SQLAlchemy (Executes ORM query/mutation & commits to PostgreSQL)
  │
  ▼
Marshmallow Schema (Serializes database object via schema.dump)
  │
  ▼
JSON Response (HTTP status code + formatted JSON body)
```

### Step-by-Step Breakdown:
1. **HTTP Request:** Client sends request to `/api/v1/<endpoint>` with optional headers (`Authorization`) and payload.
2. **Blueprint Routing:** `src/utils/blue_prints.py` captures prefix `/api/v1` and dispatches to registered Flask-RESTful resource.
3. **Resource Resolution:** `ApiFactory` resolves the matching `BaseView` or `AssociationView`.
4. **Authentication (`auth_token_required`):** Validates user authentication token from headers. If invalid or missing, immediately returns `401 Unauthorized`.
5. **Role Authorization (`roles_required`):** Verifies if current user has the required role (e.g., `admin`, `owner`). If unauthorized, returns `403 Forbidden`.
6. **Handler Execution:** Calls appropriate HTTP verb method (`post()`, `get()`, `patch()`, `delete()`).
7. **Schema Validation (`schema.load`):** Marshmallow validates incoming payload against schema rules (types, required fields). If invalid, returns `400 Bad Request`.
8. **SQLAlchemy ORM:** Performs database operation (SELECT, INSERT, UPDATE, DELETE) against PostgreSQL.
9. **Schema Serialization (`schema.dump`):** Serializes database model into JSON, applying field masks (`__only`, `__exclude`).
10. **JSON Response:** Returns final JSON payload with appropriate HTTP status code (`200 OK`, `201 Created`, etc.).

---

## 3. ModelResource vs AssociationModelResource

In `src/utils/resource.py`, business logic is divided into two distinct resource base classes:

| Feature | `ModelResource` | `AssociationModelResource` |
|---|---|---|
| **Target Entity** | Primary, standalone models (e.g. `Product`, `Order`, `User`, `Task`) | Many-to-Many junction tables (e.g. `UserRetailShop`, `CustomerAddress`, `RetailShopLocality`) |
| **Core Operations** | Full CRUD: `add_resource`, `fetch_resource`, `update_resource`, `delete_resource`, and filtered list queries | Relationship management: `add_relation`, `update_relation`, `remove_relation` |
| **Permission Scope** | Evaluates permissions on a single entity instance:<br>`has_read_permission(qs)`<br>`has_change_permission(obj)`<br>`has_delete_permission(obj)` | Evaluates permissions across **both** sides of the relationship:<br>`has_change_permission(obj, data)`<br>`has_add_permission(obj, data)` |
| **Query Support** | Filtering, search, ordering, pagination, and CSV export | Links/unlinks two existing entities via foreign keys |

---

## 4. Why Import Order in `src/__init__.py` Matters

Imports in `src/__init__.py` must follow a strict sequential order:

```python
# 1. Config & Core Extensions (db, ma, api, bp)
# 2. Database Models (products, orders, user, task)
# 3. Marshmallow Schemas (products, orders, user, task)
# 4. REST API Views (products, orders, user, task)
# 5. Security & Datastore (security)
# 6. Admin Panel (admin_manager)
```

### Key Reasons:
1. **Cross-Model Foreign Keys:** Models reference each other across packages (e.g., `Order` references `RetailShop` and `User`). All models must be registered in SQLAlchemy's metadata before schemas or queries access them, preventing `NoReferencedTableError`.
2. **Schema Introspection:** Marshmallow schemas (`ModelSchema`) inspect SQLAlchemy model tables and relationships upon declaration. If models are not loaded first, schema initialization fails.
3. **Route Registration via Decorators:** Views use `@api.register()` which executes at import time to bind endpoints to the Blueprint. Models and schemas must be ready before routes are bound.
4. **Preventing Circular Imports:** A strict linear order prevents cyclic dependencies where module A imports B which imports A, avoiding `ImportError: cannot import name ... from partially initialized module`.
5. **Security Datastore Binding:** `security.py` initializes `SQLAlchemyUserDatastore` with `User` and `Role` models. Both models must be in memory before security is configured.

---

## 5. The 4-Layer Module Architecture

Each feature module (`products`, `orders`, `user`, `task`) follows a clean 4-layer separation:

```text
┌────────────────┐     ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│   models.py    │ ──> │   schemas.py   │ ──> │  resources.py  │ ──> │    views.py    │
│ (Database ORM) │     │(Serialization) │     │(Business Logic)│     │(REST Endpoints)│
└────────────────┘     └────────────────┘     └────────────────┘     └────────────────┘
```

1. **Model (`models.py`):** SQLAlchemy ORM table definitions inheriting from `BaseMixin` (UUID `id`, `created_on`, `updated_on`).
2. **Schema (`schemas.py`):** Marshmallow schemas for serialization (`dump`), deserialization (`load`), and input validation.
3. **Resource (`resources.py`):** Business logic layer defining allowed filters, operators, pagination, field projection, and role checks.
4. **View (`views.py`):** REST API endpoints bound via `@api.register()`, exposing GET, POST, PUT, PATCH, DELETE operations.
