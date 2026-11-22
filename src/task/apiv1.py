from flask import request
from src import BaseView, api
from .resources import TaskResource

@api.register(url='/task')
class TaskView(BaseView):
    @classmethod
    def get_resource(cls):
        return TaskResource
    
    def put(self, slug=None):
        if slug:
            return self.patch(slug)
        return super().put()


# Register the plural /tasks collection routes
task_collection_view = TaskView.as_view('task_collection_api')
api.app.add_url_rule('/tasks', view_func=task_collection_view, methods=['GET', 'POST'], endpoint='task_list_create')
api.app.add_url_rule('/tasks/', view_func=task_collection_view, methods=['GET', 'POST'], endpoint='task_list_create_slash')