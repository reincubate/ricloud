from __future__ import absolute_import, unicode_literals

from . import abase


class Subscription(
    abase.CreatableResource, abase.ListableResource, abase.DeletableResource
):
    RESOURCE = "subscription"
    RESOURCE_PATH = "subscriptions"
