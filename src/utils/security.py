from flask_security import Security, SQLAlchemyUserDatastore
from src.user import models

user_data_store = SQLAlchemyUserDatastore(models.db, models.User, models.Role)

class AppSecurity(Security):
    def init_app(self, app, datastore=None, **kwargs):
        super().init_app(app, datastore=datastore or user_data_store, **kwargs)

security = AppSecurity(datastore=user_data_store)
