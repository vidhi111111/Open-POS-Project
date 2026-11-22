from sqlalchemy.dialects.postgresql import UUID
from src.utils import db, BaseMixin, ReprMixin

class Task(BaseMixin, db.Model, ReprMixin):
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(UUID(as_uuid=False), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)

    user = db.relationship('User', backref=db.backref('tasks', lazy='dynamic'))