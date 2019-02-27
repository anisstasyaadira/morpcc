import morpfw
import rulez
from .schema import NotificationSchema


class NotificationModel(morpfw.Model):
    schema = NotificationSchema


class NotificationCollection(morpfw.Collection):
    schema = NotificationSchema

    def search(self, query=None, *args, **kwargs):
        if kwargs.get('secure', True):
            if query:
                rulez.and_(
                    rulez.field['userid'] == self.request.identity.userid,
                    query)
            else:
                query = rulez.field['userid'] == self.request.identity.userid
        return super().search(query, *args, **kwargs)
