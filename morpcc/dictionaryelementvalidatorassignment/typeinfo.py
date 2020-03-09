from ..app import App
from .model import (
    DictionaryElementValidatorAssignmentCollection,
    DictionaryElementValidatorAssignmentModel,
)

#
from .modelui import (
    DictionaryElementValidatorAssignmentCollectionUI,
    DictionaryElementValidatorAssignmentModelUI,
)
from .path import get_collection, get_collection_ui, get_model, get_model_ui
from .schema import DictionaryElementValidatorAssignmentSchema

#


@App.typeinfo(
    name="morpcc.dictionaryelementvalidatorassignment",
    schema=DictionaryElementValidatorAssignmentSchema,
)
def get_typeinfo(request):
    return {
        "title": "DictionaryElementValidatorAssignment",
        "description": "DictionaryElementValidatorAssignment type",
        "schema": DictionaryElementValidatorAssignmentSchema,
        "collection": DictionaryElementValidatorAssignmentCollection,
        "collection_factory": get_collection,
        "model": DictionaryElementValidatorAssignmentModel,
        "model_factory": get_model,
        #
        "collection_ui": DictionaryElementValidatorAssignmentCollectionUI,
        "collection_ui_factory": get_collection_ui,
        "model_ui": DictionaryElementValidatorAssignmentModelUI,
        "model_ui_factory": get_model_ui,
        #
        "internal": True,
    }
