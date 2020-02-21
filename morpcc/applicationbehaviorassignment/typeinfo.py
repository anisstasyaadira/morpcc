from ..app import App
from .model import (
    ApplicationBehaviorAssignmentCollection,
    ApplicationBehaviorAssignmentModel,
)

#
from .modelui import (
    ApplicationBehaviorAssignmentCollectionUI,
    ApplicationBehaviorAssignmentModelUI,
)
from .path import get_collection, get_collection_ui, get_model, get_model_ui
from .schema import ApplicationBehaviorAssignmentSchema

#


@App.typeinfo(
    name="morpcc.applicationbehaviorassignment",
    schema=ApplicationBehaviorAssignmentSchema,
)
def get_typeinfo(request):
    return {
        "title": "ApplicationBehaviorAssignment",
        "description": "ApplicationBehaviorAssignment type",
        "schema": ApplicationBehaviorAssignmentSchema,
        "collection": ApplicationBehaviorAssignmentCollection,
        "collection_factory": get_collection,
        "model": ApplicationBehaviorAssignmentModel,
        "model_factory": get_model,
        "collection_ui": ApplicationBehaviorAssignmentCollectionUI,
        "collection_ui_factory": get_collection_ui,
        "model_ui": ApplicationBehaviorAssignmentModelUI,
        "model_ui_factory": get_model_ui,
        "internal": True,
    }
