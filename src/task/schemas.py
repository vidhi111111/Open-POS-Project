from marshmallow import validate
from src import ma, BaseSchema
from .models import Task


class TaskSchema(BaseSchema):
    class Meta:
        model = Task
        exclude = ('updated_on',)

    id = ma.String(dump_only=True)
    title = ma.String(required=True, validate=validate.Length(min=1, max=254))
    description = ma.String(allow_none=True)
    status = ma.String(
        default='pending',
        validate=validate.OneOf(
            ['pending', 'in_progress', 'done'],
            error="status must be one of: pending, in_progress, done"
        )
    )
    due_date = ma.DateTime(allow_none=True)
    user_id = ma.String(required=True)
    created_on = ma.DateTime(dump_only=True)