import random
from flask_security import Security, SQLAlchemyUserDatastore, ConfirmRegisterForm
from wtforms import StringField
from src.user import models

user_data_store = SQLAlchemyUserDatastore(models.db, models.User, models.Role)

class ExtendedRegisterForm(ConfirmRegisterForm):
    name = StringField('Name')
    mobile_number = StringField('Mobile Number')

    def validate(self, *args, **kwargs):
        from src.user.models import User

        # Auto-fill name and mobile_number if not provided (e.g. from browser form)
        if not self.name.data and self.email.data:
            self.name.data = self.email.data.split('@')[0]
        if not self.mobile_number.data:
            while True:
                candidate = f"9{random.randint(100000000, 999999999)}"
                if not User.query.filter_by(mobile_number=candidate).first():
                    self.mobile_number.data = candidate
                    break

        if not super().validate(*args, **kwargs):
            return False

        if self.mobile_number.data:
            existing = User.query.filter_by(mobile_number=self.mobile_number.data).first()
            if existing:
                self.mobile_number.errors.append("This mobile number is already in use. Please enter a different number.")
                return False

        return True

class AppSecurity(Security):
    def init_app(self, app, datastore=None, **kwargs):
        kwargs.setdefault('confirm_register_form', ExtendedRegisterForm)
        kwargs.setdefault('register_form', ExtendedRegisterForm)
        super().init_app(app, datastore=datastore or user_data_store, **kwargs)

security = AppSecurity(datastore=user_data_store, confirm_register_form=ExtendedRegisterForm, register_form=ExtendedRegisterForm)
