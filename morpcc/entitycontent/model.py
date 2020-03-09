import morpfw
from morpfw.crud.storage.pgsqlstorage import PgSQLStorage

from ..relationship.validator import EntityContentReferenceValidator
from ..relationship.widget import EntityContentReferenceWidget
from .modelui import EntityContentCollectionUI, EntityContentModelUI


class EntityContentCollection(morpfw.Collection):
    def __init__(self, application, parent, request, storage, data=None):
        self.__application__ = application
        self.__parent__ = parent
        super().__init__(request, storage, data=data)

    def ui(self):
        return EntityContentCollectionUI(self.request, self)


class EntityContentModel(morpfw.Model):
    @property
    def schema(self):
        return self.collection.schema

    def ui(self):
        return EntityContentModelUI(self.request, self, self.collection.ui())

    def attributes(self):
        entity = self.collection.__parent__
        return entity.attributes()

    def relationships(self):
        entity = self.collection.__parent__
        return entity.relationships()

    def backrelationships(self):
        entity = self.collection.__parent__
        return entity.backrelationships()

    def entity(self):
        return self.collection.__parent__


def content_collection_factory(entity, application):
    behaviors = entity.behaviors()

    model_markers = []
    modelui_markers = []
    collection_markers = []
    collectionui_markers = []

    for behavior in behaviors:
        model_markers.append(behavior.model_marker)
        modelui_markers.append(behavior.modelui_marker)
        collection_markers.append(behavior.collection_marker)
        collectionui_markers.append(behavior.collectionui_marker)

    modelui_markers.append(EntityContentModelUI)

    ModelUI = type("ModelUI", tuple(modelui_markers), {})

    # set relationship widgets and validators
    field_widgets = {}
    field_validators = {}
    for relname, rel in entity.relationships().items():
        refsearch = rel.reference_search_attribute()
        ref = rel.reference_attribute()
        ref_field = ref["name"]
        if refsearch:
            refsearch_field = refsearch["name"]
        else:
            refsearch_field = ref["name"]

        field_validators.setdefault(relname, [])
        field_validators[relname].append(
            EntityContentReferenceValidator(
                application_uuid=application.uuid,
                entity_uuid=ref["entity_uuid"],
                attribute=ref_field,
            )
        )

        field_widgets[relname] = EntityContentReferenceWidget(
            application_uuid=application.uuid,
            entity_uuid=ref["entity_uuid"],
            term_field=refsearch_field,
            value_field=ref_field,
        )

    dc_schema = entity.dataclass(validators=field_validators, widgets=field_widgets)

    class ContentCollectionUI(EntityContentCollectionUI):
        schema = dc_schema
        modelui_class = ModelUI

    collectionui_markers.append(ContentCollectionUI)

    CollectionUI = type("CollectionUI", tuple(collectionui_markers), {})

    class ContentModel(EntityContentModel):

        schema = dc_schema
        __path_model__ = EntityContentModel

        def ui(self):
            return ModelUI(self.request, self, self.collection.ui())

    model_markers.append(ContentModel)

    Model = type("Model", tuple(model_markers), {})

    class ContentCollection(EntityContentCollection):

        schema = dc_schema

        __path_model__ = EntityContentCollection

        def ui(self):
            return CollectionUI(self.request, self)

    collection_markers.append(ContentCollection)

    Collection = type("Collection", tuple(collection_markers), {})

    class Storage(PgSQLStorage):
        model = Model

        @property
        def session(self):
            return self.request.get_db_session("warehouse")

    return Collection(
        application,
        entity,
        entity.request,
        storage=Storage(entity.request, metadata=application.content_metadata()),
    )