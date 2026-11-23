import random
from flask_security import Security, SQLAlchemyUserDatastore, ConfirmRegisterForm
from wtforms import StringField
from src.user import models

user_data_store = SQLAlchemyUserDatastore(models.db, models.User, models.Role)

class ExtendedRegisterForm(ConfirmRegisterForm):
    name = StringField('Name')
    mobile_number = StringField('Mobile Number')

    def validate(self, *args, **kwargs):
        # Auto-fill name and mobile_number if not provided (e.g. from browser form)
        if not self.name.data and self.email.data:
            self.name.data = self.email.data.split('@')[0]
        if not self.mobile_number.data:
            self.mobile_number.data = f"9{random.randint(100000000, 999999999)}"
        return super().validate(*args, **kwargs)

class AppSecurity(Security):
    def init_app(self, app, datastore=None, **kwargs):
        kwargs.setdefault('confirm_register_form', ExtendedRegisterForm)
        kwargs.setdefault('register_form', ExtendedRegisterForm)
        super().init_app(app, datastore=datastore or user_data_store, **kwargs)

security = AppSecurity(datastore=user_data_store, confirm_register_form=ExtendedRegisterForm, register_form=ExtendedRegisterForm)
