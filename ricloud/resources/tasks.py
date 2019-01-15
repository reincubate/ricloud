from __future__ import absolute_import, unicode_literals

from . import abase


class Task(abase.CreatableResource, abase.ListableResource):
    RESOURCE = "task"
    RESOURCE_PATH = "tasks"
