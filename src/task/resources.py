from src.utils import operators as ops
from src.utils.resource import CommonResource
from .models import Task
from .schemas import TaskSchema

class TaskResource(CommonResource):
    model = Task
    schema = TaskSchema

    filters = {
        'status': [ops.Equal, ops.In],
        'title': [ops.Equal, ops.Contains],
        'user_id': [ops.Equal, ops.In],
        'id': [ops.Equal]
    }

    order_by = ['created_on', 'due_date', 'title', 'id', 'status']