import os
import re
from datetime import datetime
import click
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

from src import api, db, ma, create_app, configs, bp, security, admin

config_name = os.environ.get('PYTH_SRVR', 'default')
config = configs.get(config_name, configs['default'])

extensions = [api, db, ma, security, admin]
bps = [bp]

# Create Flask application instance
app = create_app(__name__, config, extensions=extensions, blueprints=bps)

# Migrate automatically registers 'flask db' command
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, ma=ma, config=config)

@app.cli.command("create-db")
def create_db():
    db.session.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    db.session.commit()
    db.create_all()
    print("Database tables created successfully.")


@app.cli.command("create-admin")
@click.option("-e", "--email", required=True, help="Admin email address")
@click.option("-p", "--password", required=True, help="Admin password")
@click.option("-n", "--name", default="Admin", help="Admin name")
@click.option("-m", "--mobile", default="9999999999", help="Mobile number")
@click.option("-b", "--brand", default="Demo Brand", help="Retail brand name")
@click.option("-s", "--shop", default="Main Shop", help="Retail shop name")
def create_admin(email, password, name, mobile, brand, shop):
    """Create (or update) a confirmed 'admin' + 'owner' user with a retail brand, a shop and every permission used in the code."""
    from flask_security.utils import encrypt_password
    from src.utils.security import user_data_store
    from src.user.models import User, RetailBrand, RetailShop, Permission

    # 1. Collect every permission name checked via has_permission('...') in src/
    names = set()
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f.endswith('.py'):
                with open(os.path.join(root, f), encoding='utf-8') as fh:
                    names.update(re.findall(r"has_permission\('([a-z_]+)'\)", fh.read()))

    permissions = []
    for perm_name in sorted(names):
        perm = Permission.query.filter_by(name=perm_name).first() or Permission(name=perm_name)
        permissions.append(perm)

    # 2. Setup Brand and Shop
    retail_brand = RetailBrand.query.filter_by(name=brand).first() or RetailBrand(name=brand)
    retail_shop = RetailShop.query.filter_by(name=shop, retail_brand=retail_brand).first() if retail_brand.id else None
    retail_shop = retail_shop or RetailShop(name=shop, identity=shop, retail_brand=retail_brand)

    # 3. Setup Roles
    roles = [user_data_store.find_or_create_role(name=r) for r in ('admin', 'owner')]

    # 4. Create or update User
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = user_data_store.create_user(email=email, name=name, mobile_number=mobile)

    user.password = encrypt_password(password)
    user.active = True
    user.confirmed_at = user.confirmed_at or datetime.utcnow()
    user.retail_brand = retail_brand

    for role in roles:
        if role not in user.roles:
            user.roles.append(role)

    for perm in permissions:
        if perm not in user.permissions:
            user.permissions.append(perm)

    if retail_shop not in user.retail_shops:
        user.retail_shops.append(retail_shop)

    db.session.commit()
    print(f"User {email} ready (brand: {brand}, shop: {shop} [{retail_shop.id}], {len(permissions)} permissions).")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)