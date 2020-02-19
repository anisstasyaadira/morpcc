from ..app import App
from .model import ApplicationCollection
from .model import ApplicationModel
from .schema import ApplicationSchema
from .path import get_collection, get_model
# 
from .modelui import ApplicationCollectionUI
from .modelui import ApplicationModelUI
from .path import get_collection_ui, get_model_ui
# 


@App.typeinfo(name='morpcc.application')
def get_typeinfo(request):
    return {
        'title': 'Application',
        'description': 'Application type',
        'schema': ApplicationSchema,
        'collection': ApplicationCollection,
        'collection_factory': get_collection,
        'model': ApplicationModel,
        'model_factory': get_model,
        # 
        'collection_ui': ApplicationCollectionUI,
        'collection_ui_factory': get_collection_ui,
        'model_ui': ApplicationModelUI,
        'model_ui_factory': get_model_ui,
        # 
    }
