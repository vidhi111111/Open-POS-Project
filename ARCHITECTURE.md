# Architecture & Design Overview

This document describes the architectural design, directory organization, request lifecycle, and modular patterns of the Open POS API.

The project is a RESTful point-of-sale backend built with **Flask**, **PostgreSQL**, and **SQLAlchemy**. The application follows a modular, layer-separated structure where domain features are organized into isolated packages with standardized responsibility layers.

---

## 1. Project Directory Structure

```text
open-pos-api-master/
├── manager.py                   # Application entrypoint & Flask CLI commands
├── .env                         # Environment configuration (DB connection, secret keys)
├── requirements.txt             # Project dependencies
├── migrations/                  # Alembic database migration scripts
└── src/
    ├── __init__.py              # Application module initialization & dependency ordering
    ├── config.py                # Environment configurations (Dev, Test, Prod)
    │
    ├── utils/                   # Shared architectural core & framework base classes
    │   ├── factory.py           # Application Factory: create_app()
    │   ├── blue_prints.py       # Central Blueprint definition (prefix: /api/v1)
    │   ├── api.py               # ApiFactory, @api.register(), BaseView, AssociationView
    │   ├── resource.py          # ModelResource & AssociationModelResource base classes
    │   ├── models.py            # db instance & BaseMixin (UUID id, audit timestamps)
    │   ├── schema.py            # ma instance & BaseSchema configuration
    │   ├── security.py          # Flask-Security setup & SQLAlchemyUserDatastore
    │   ├── methods.py           # Allowed HTTP action definitions (List, Fetch, Create, etc.)
    │   ├── operators.py         # Dynamic query filter operators (Equal, Contains, In, etc.)
    │   ├── exceptions.py        # Centralized custom API exceptions
    │   └── admin.py             # Flask-Admin initialization & access controls
    │
    ├── products/                # Product catalog, categories, brands, and stock
    ├── orders/                  # Order management, line items, discounts, and payments
    ├── user/                    # Users, roles, permissions, retail shops, and customers
    ├── task/                    # Asynchronous & scheduled background tasks
    │   └── (Each module contains: models.py, schemas.py, resources.py, views.py)
    │
    └── admin_panel/             # Flask-Admin backoffice configuration
        └── admin_manager.py     # Registers SQLAlchemy models with admin ModelViews
```

---

## 2. The 4-Layer Module Design

Every business module (`products`, `orders`, `user`, `task`) is organized into four standardized layers:

| Layer | File | Role & Responsibility |
|---|---|---|
| **Model** | `models.py` | Defines the database schema using SQLAlchemy ORM. Inherits from `BaseMixin` for automatic UUID primary keys (`id`), `created_on`, and `updated_on` timestamps. |
| **Schema** | `schemas.py` | Handles two-way data transformation with Marshmallow: serializes ORM models to JSON (`dump`), deserializes JSON input to objects (`load`), and validates payloads. |
| **Resource** | `resources.py` | Encapsulates business logic: allowed query filters, pagination boundaries, field masking (`only`/`exclude`), role requirements, and permission checks. |
| **View** | `views.py` | Exposes REST endpoints by subclassing `BaseView` or `AssociationView` and binding them to the API router with the `@api.register()` decorator. |

---

## 3. Application Bootstrap Lifecycle

When the application launches, initialization proceeds in the following sequence:

1. **Environment Loading:** `manager.py` calls `load_dotenv()` to read environment variables from `.env`.
2. **Central Registry Import:** `manager.py` imports `src/__init__.py`. This triggers the registration of base utilities, database models, schemas, and API views in an orderly sequence to resolve cross-model dependencies cleanly without circular import conflicts.
3. **Route Discovery:** During view module imports, the `@api.register()` decorator binds URL endpoints and HTTP methods to the central Blueprint (`/api/v1`).
4. **Application Factory:** `create_app()` in `src/utils/factory.py` instantiates `Flask(__name__)`, loads configuration settings, enables CORS, registers the blueprint, and initializes extensions (`api`, `db`, `ma`, `security`, `admin`).
5. **Runtime Server:** `flask run` spins up the development server at `http://127.0.0.1:5000/`.

---

## 4. HTTP Request Execution Pipeline

Every incoming API call follows a structured execution pipeline from route matching to response delivery:

```text
HTTP Request (e.g. POST /api/v1/product)
   │
   ▼
[ Blueprint Routing ]
   Matches /api/v1 prefix and dispatches to registered endpoint
   │
   ▼
[ View Resolution ]
   Flask-RESTful resolves the target BaseView class
   │
   ▼
[ Authentication Guard ]
   auth_token_required verifies the 'Authentication-Token' header
   │
   ▼
[ Role Authorization ]
   roles_accepted / roles_required confirms user access privileges
   │
   ▼
[ Handler Execution ]
   Executes get, post, put, patch, or delete method in BaseView
   │
   ├── Filter & Permission Hooks: apply_filters(), has_read_permission()
   │
   ▼
[ Schema Validation & Serialization ]
   Marshmallow validates input (schema.load) or formats output (schema.dump)
   │
   ▼
[ Database Transaction ]
   SQLAlchemy ORM commits or rolls back operations in PostgreSQL
   │
   ▼
JSON Response (HTTP Status Code + Serialized Payload)
```

---

## 5. Resource Architecture: Primary vs Association Resources

The business logic in `src/utils/resource.py` separates entities into two specialized base classes:

### ModelResource
- **Purpose:** Used for primary, standalone domain models (e.g., `Product`, `Customer`, `Order`, `User`).
- **Capabilities:** Manages full CRUD operations (`add_resource`, `update_resource`, `delete_resource`, and filtered list queries with pagination and CSV export).
- **Permission Scope:** Permission hooks take only the object instance (`has_read_permission(qs)`, `has_change_permission(obj)`, `has_delete_permission(obj)`), focusing solely on whether the user can manipulate that single record.

### AssociationModelResource
- **Purpose:** Used for many-to-many junction/mapping entities (e.g., `UserRetailShop`, `CustomerAddress`, `RetailShopLocality`).
- **Capabilities:** Focuses specifically on relationship management (`add_relation`, `update_relation`, `remove_relation`).
- **Permission Scope:** Permission hooks take both the object and the incoming request payload (`has_change_permission(obj, data)`, `has_add_permission(obj, data)`), ensuring authorization can evaluate both sides of the relationship before linking or unlinking records.

---

## 6. Shared Utilities Reference (`src/utils/`)

| File | Purpose |
|---|---|
| `factory.py` | `create_app()` factory function to configure and assemble the Flask application. |
| `blue_prints.py` | Declares the global API Blueprint (`pos`) with URL prefix `/api/v1`. |
| `api.py` | `ApiFactory` with the `@api.register()` decorator, plus `BaseView` and `AssociationView` base classes. |
| `resource.py` | Core `ModelResource` and `AssociationModelResource` base classes defining pagination, filtering, and authorization hooks. |
| `models.py` | Initializes SQLAlchemy `db` and defines `BaseMixin` (providing UUID `id`, `created_on`, `updated_on`). |
| `schema.py` | Initializes Marshmallow `ma` and defines `BaseSchema` with session integration. |
| `security.py` | Configures Flask-Security and initializes `SQLAlchemyUserDatastore` with `User` and `Role` models. |
| `methods.py` | Defines allowed endpoint operations (`List`, `Fetch`, `Create`, `Update`, `Delete`, `BulkUpdate`). |
| `operators.py` | Dynamic filter operators used in resource querysets (`Equal`, `Contains`, `In`, `GreaterThan`, etc.). |
| `exceptions.py` | Custom exception hierarchy for structured database and validation error responses. |
| `admin.py` | Sets up Flask-Admin with login-protected views. |

---

## 7. Extending the System (Adding a New Domain Feature)

To add a new entity (for example, `Supplier`):

1. **Model (`models.py`):** Define the table inheriting from `BaseMixin`:
   ```python
   class Supplier(BaseMixin, db.Model):
       name = db.Column(db.String(120), nullable=False)
       contact = db.Column(db.String(50))
   ```
2. **Schema (`schemas.py`):** Define serialization rules:
   ```python
   class SupplierSchema(BaseSchema):
       class Meta:
           model = Supplier
   ```
3. **Resource (`resources.py`):** Define permissions, filters, and limits:
   ```python
   class SupplierResource(ModelResource):
       model = Supplier
       schema = SupplierSchema
       auth_required = True
       roles_accepted = ('admin', 'owner')
   ```
4. **View (`views.py`):** Register the endpoint with the router:
   ```python
   @api.register()
   class SupplierView(BaseView):
       @classmethod
       def get_resource(cls):
           return SupplierResource
   ```
5. **Database Migration:** Generate and apply the migration:
   ```powershell
   flask db migrate -m "add supplier table"
   flask db upgrade
   ```
   The endpoint `/api/v1/supplier` is immediately available with standard CRUD operations.
