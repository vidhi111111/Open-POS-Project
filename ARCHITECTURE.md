# Open POS API – Architecture & Database Reference

This document outlines the architectural structure, request lifecycle, data layer, and migration workflow of the Open POS Flask REST API.

---

## 1. Project Directory & File Roles

### Directory Layout
```text
open-pos-api-master/
├── manager.py                   # App entrypoint & CLI commands (create-db, create-admin)
├── .env                         # Environment variables (DB URL, secret keys)
├── requirements.txt             # Pinned project dependencies
├── migrations/                  # Alembic database migration scripts (Flask-Migrate)
└── src/
    ├── __init__.py              # Central module registry & strict import sequence
    ├── config.py                # Environment configurations (Dev, Test, Prod)
    │
    ├── utils/                   # Shared architectural core & base classes
    │   ├── factory.py           # Application Factory: create_app()
    │   ├── blue_prints.py       # Global API Blueprint (/api/v1)
    │   ├── api.py               # ApiFactory, @api.register(), BaseView, AssociationView
    │   ├── resource.py          # ModelResource & AssociationModelResource base classes
    │   ├── models.py            # db instance, BaseMixin (UUID id, audit timestamps)
    │   ├── schema.py            # ma instance & BaseSchema configuration
    │   ├── security.py          # Flask-Security setup & UserDatastore
    │   ├── methods.py           # Allowed HTTP action definitions (List, Fetch, Create, etc.)
    │   ├── operators.py         # Dynamic query filter operators (Equal, Contains, In, etc.)
    │   ├── exceptions.py        # Centralized custom API exceptions
    │   └── admin.py             # Flask-Admin backoffice setup
    │
    ├── products/                # Product catalog, categories, brands, stock
    ├── orders/                  # Orders, line items, discounts, payments
    ├── user/                    # Users, roles, permissions, shops, customers
    ├── task/                    # Background & scheduled task management
    └── admin_panel/             # Flask-Admin ModelView registrations
```

### Role of Key Files

| File | Core Role |
|---|---|
| `manager.py` | App entrypoint; loads `.env`, binds Flask CLI commands (`create-db`, `create-admin`, `runserver`), and instantiates the application. |
| `src/__init__.py` | Central import registry that loads models, schemas, views, and security in a strict, non-circular order. |
| `src/utils/factory.py` | Contains `create_app()` factory function to configure Flask, register Blueprints, enable CORS, and bind extensions (`db`, `ma`, `api`, `security`, `admin`). |
| `src/utils/blue_prints.py` | Declares the primary API Blueprint (`pos`) with URL prefix `/api/v1`. |
| `src/utils/api.py` | Defines `ApiFactory` with the `@api.register()` decorator and provides base classes `BaseView` and `AssociationView`. |
| `src/utils/security.py` | Configures Flask-Security authentication, token handling, user datastore, and custom registration forms. |

---

## 2. HTTP Request Execution Pipeline

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
auth_token_required (Verifies Authorization / Authentication-Token header)
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

### Pipeline Stages:
1. **Routing:** `blue_prints.py` catches `/api/v1` and dispatches to the registered Flask-RESTful endpoint.
2. **Authentication (`auth_token_required`):** Checks `Authentication-Token` / `Authorization` header. If missing or invalid, returns `401 Unauthorized`.
3. **Authorization (`roles_required`):** Verifies user role (e.g., `admin`, `owner`). If unauthorized, returns `403 Forbidden`.
4. **Handler Execution:** Calls the target HTTP verb method (`get`, `post`, `patch`, `delete`).
5. **Schema Validation (`schema.load`):** Validates input types and required fields. On invalid input, raises `ValidationError` returning `400 Bad Request`.
6. **SQLAlchemy ORM:** Performs transactional database operations against PostgreSQL.
7. **Serialization (`schema.dump`):** Formats output, applies field masks (`__only`, `__exclude`), and conceals sensitive fields (e.g., `password`).
8. **JSON Response:** Delivers final payload with status code (`200 OK`, `201 Created`, etc.).

---

## 3. Resource Architecture: ModelResource vs AssociationModelResource

In `src/utils/resource.py`, business logic is cleanly separated into two distinct base classes:

| Feature | `ModelResource` | `AssociationModelResource` |
|---|---|---|
| **Target Entity** | Primary, standalone models (e.g. `Product`, `Order`, `User`, `Task`) | Many-to-Many junction tables (e.g. `UserRetailShop`, `CustomerAddress`, `RetailShopLocality`) |
| **Core Operations** | Full CRUD: `add_resource`, `fetch_resource`, `update_resource`, `delete_resource`, and filtered list queries | Relationship management: `add_relation`, `update_relation`, `remove_relation` |
| **Permission Scope** | Evaluates permissions on a single entity instance:<br>`has_read_permission(qs)`<br>`has_change_permission(obj)`<br>`has_delete_permission(obj)` | Evaluates permissions across **both** sides of the relationship:<br>`has_change_permission(obj, data)`<br>`has_add_permission(obj, data)` |
| **Query Support** | Filtering, search, ordering, pagination, and CSV export | Links/unlinks two existing entities via foreign keys |

---

## 4. Why Import Order in `src/__init__.py` Matters

Imports in `src/__init__.py` follow a strict sequential order:

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

1. **Model (`models.py`):** SQLAlchemy ORM table definitions inheriting from `BaseMixin`.
2. **Schema (`schemas.py`):** Marshmallow schemas for serialization (`dump`), deserialization (`load`), and input validation.
3. **Resource (`resources.py`):** Business logic layer defining allowed filters, operators, pagination, field projection, and role checks.
4. **View (`views.py`):** REST API endpoints bound via `@api.register()`, exposing GET, POST, PUT, PATCH, DELETE operations.

---

## 6. Database & Migrations

### 6.1 BaseMixin & Dynamic Table Naming (`src/utils/models.py`)

All models inherit from `BaseMixin`:

```python
def to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class BaseMixin(object):
    @declared_attr
    def __tablename__(self):
        return to_underscore(self.__name__)

    id = db.Column(UUID(as_uuid=False), primary_key=True, server_default=text("uuid_generate_v4()"))
    created_on = db.Column(db.TIMESTAMP, server_default=text("current_timestamp"))
    updated_on = db.Column(db.TIMESTAMP, onupdate=db.func.current_timestamp(),
                           server_default=text("current_timestamp"))
```

- **Automatic Table Names:** Converts PascalCase class names to snake_case PostgreSQL table names (e.g., `UserRetailShop` ➔ `user_retail_shop`, `PrinterConfig` ➔ `printer_config`).
- **Standardized Primary Key:** Automatically equips every table with a PostgreSQL UUID primary key (`uuid_generate_v4()`).
- **Audit Timestamps:** Automatically tracks `created_on` and auto-updating `updated_on` timestamps.

---

### 6.2 Marshmallow: `load()`, `dump()`, and `ValidationError` (`src/user/schemas.py`)

Schemas inherit from `BaseSchema` (wrapping `ModelSchema`):

```python
class UserSchema(BaseSchema):
    class Meta:
        model = User
        exclude = ('updated_on', 'password')

    id = ma.UUID(dump_only=True)
    email = ma.Email(required=True)
    name = ma.String(load=True)
```

| Method / Exception | Purpose & Usage in API |
|---|---|
| **`schema.load(data)`** | **Deserialization & Validation:** Converts incoming JSON payloads into validated Python dictionaries or model instances. Validates data types, email formats, and required constraints. |
| **`schema.dump(obj)`** | **Serialization:** Converts SQLAlchemy ORM model instances into JSON-serializable dictionaries. Masks sensitive attributes (e.g., `exclude=('password',)`), embeds nested relations, and respects `dump_only=True`. |
| **`ValidationError`** | **Error Handling:** Raised by Marshmallow whenever `load()` encounters invalid, missing, or malformed fields. `BaseView` catches `ValidationError` and transforms it into a standard `400 Bad Request` JSON response: `{"errors": {"<field>": ["<reason>"]}}`. |

---

### 6.3 User & UserProfile Relationship Structure (`src/user/models.py`)

In Open POS API, the user entity and its profile relations are structured as follows:

1. **User Identity & Core Profile:** Attributes such as `name`, `mobile_number`, `email`, `active`, and login statistics (`last_login_at`, `login_count`) reside directly on the `User` model.
2. **Brand & Shop Access:**
   - **RetailBrand:** One-to-many relationship (`User.retail_brand_id = db.ForeignKey('retail_brand.id')`).
   - **RetailShop:** Many-to-many relationship linked via the `user_retail_shop` junction table (`UserRetailShop`).
3. **Roles & Permissions:**
   - **Roles:** Many-to-many relationship linked via `user_role` (`UserRole`).
   - **Permissions:** Dynamic many-to-many relationship linked via `user_permission` (`UserPermission`).
4. **Dedicated UserProfile Architecture:** If extended into a separate table, a profile is modeled via a 1-to-1 relationship:
   ```python
   class UserProfile(BaseMixin, db.Model):
       user_id = db.Column(UUID, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)
       avatar_url = db.Column(db.String(255))
       bio = db.Column(db.Text)
       user = db.relationship('User', backref=db.backref('profile', uselist=False))
   ```

---

### 6.4 Migration Lifecycle (Migrate, Upgrade & Downgrade)

Database schema versions are managed via **Flask-Migrate** (Alembic):

```powershell
# 1. Check current database revision head
flask db current

# 2. Add test column to model (e.g. in src/task/models.py: test_col = db.Column(db.String(50)))
# Generate migration script:
flask db migrate -m "add test_col to task"

# 3. Apply migration to PostgreSQL:
flask db upgrade

# 4. Verify column in database:
# SELECT column_name FROM information_schema.columns WHERE table_name = 'task';

# 5. Rollback migration:
flask db downgrade

# 6. Verify column is removed from database and remove test column from model
```
