import html

import morpfw


class ModelUI(object):

    view_include_fields: list = []
    view_exclude_fields: list = [
        "id",
        "uuid",
        "creator",
        "created",
        "modified",
        "state",
        "deleted",
        "xattrs",
        "blobs",
    ]
    edit_include_fields: list = []
    edit_exclude_fields: list = [
        "id",
        "uuid",
        "creator",
        "created",
        "modified",
        "state",
        "deleted",
        "xattrs",
        "blobs",
    ]

    default_view = "view"

    @property
    def identifier(self):
        return self.model.identifier

    def __init__(self, request, model, collection_ui):
        self.request = request
        self.model = model
        self.collection_ui = collection_ui

    def transitions(self):
        sm = self.model.statemachine()
        if sm:
            return list(
                [
                    i
                    for i in sm._machine.get_triggers(sm.state)
                    if not i.startswith("to_")
                ]
            )
        return []



class CollectionUI(object):

    modelui_class = ModelUI

    create_include_fields: list = []
    create_exclude_fields: list = [
        "id",
        "uuid",
        "creator",
        "created",
        "modified",
        "state",
        "deleted",
        "xattrs",
        "blobs",
    ]

    default_view = "listing"

    @property
    def page_title(self):
        return str(self.collection.__class__.__name__)

    @property
    def listing_title(self):
        return "Contents"

    @property
    def columns(self):
        columns = []
        for n, field in self.collection.schema.__dataclass_fields__.items():
            if n in morpfw.Schema.__dataclass_fields__.keys():
                continue
            title = field.metadata.get("title", n)
            columns.append({"title": title, "name": n})

        columns.append({"title": "Actions", "name": "structure:buttons"})
        return columns

    def __init__(self, request, collection):
        self.request = request
        self.collection = collection

    def get_structure_column(self, obj, request, column_type):
        column_type = column_type.replace("structure:", "")
        coldata = request.app.get_structure_column(
            model=obj, request=request, name=column_type
        )
        return coldata

    def search(self, query=None, offset=0, limit=None, order_by=None, secure=False):
        objs = self.collection.search(query, offset, limit, order_by, secure)
        return list([self.modelui_class(self.request, o, self) for o in objs])

    def get(self, identifier):
        obj = self.collection.get(identifier)
        if obj:
            return self.modelui_class(self.request, obj, self)
        return None


