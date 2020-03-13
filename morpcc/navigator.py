import typing

import rulez

from .app import App
from .application.path import get_collection as get_app_collection
from .attribute.path import get_collection as get_attr_collection
from .backrelationship.path import get_collection as get_brel_collection
from .dictionaryelement.path import get_collection as get_del_collection
from .dictionaryentity.path import get_collection as get_dent_collection
from .entity.path import get_collection as get_dm_collection
from .entitycontent.path import content_collection_factory
from .referencedata.path import get_collection as get_refdata_collection
from .referencedatakey.path import get_collection as get_refdatakey_collection
from .referencedataproperty.path import get_collection as get_refdataprop_collection
from .relationship.path import get_collection as get_rel_collection


def navmemoize(method):
    def NavigatorMemoizeWrapper(self, *args):
        klass = self.__class__
        if getattr(klass, "__memoize__", None) is None:
            klass.__memoize__ = {}
        cachemgr = klass.__memoize__
        key = hash((klass, method, args))
        cache = cachemgr.get(key, None)
        if cache:
            return cache
        result = method(self, *args)
        cachemgr[key] = result
        return result


class AttributesBrowser(object):
    def __init__(self, entity, request):
        self.entity = entity
        self.col = get_attr_collection(request)

    @navmemoize
    def __getitem__(self, key):
        attrs = self.col.search(
            rulez.and_(
                rulez.field["entity_uuid"] == self.entity.uuid,
                rulez.field["name"] == key,
            )
        )
        if attrs:
            return attrs[0]
        return None

    def keys(self):
        return [
            i["name"]
            for i in self.col.search(rulez.field["entity_uuid"] == self.entity.uuid)
        ]


class RelationshipsBrowser(AttributesBrowser):
    def __init__(self, entity, request):
        self.entity = entity
        self.col = get_rel_collection(request)


class BackRelationshipsBrowser(AttributesBrowser):
    def __init__(self, entity, request):
        self.entity = entity
        self.col = get_brel_collection(request)


class EntityNavigator(object):
    def __init__(self, schema, entity, request):
        self.schema = schema
        self.entity = entity
        self.request = request
        self.attr_col = get_attr_collection(request)
        self.rel_col = get_rel_collection(request)
        self.brel_col = get_brel_collection(request)
        self.attributes = AttributesBrowser(entity, request)
        self.relationships = RelationshipsBrowser(entity, request)
        self.backrelationships = RelationshipsBrowser(entity, request)

    def add_attribute(
        self,
        name,
        type_,
        title,
        description=None,
        required=False,
        primary_key=False,
        dictionaryelement=None,
        allow_invalid=False,
    ):
        data = {
            "name": name,
            "type": type_,
            "title": title,
            "description": description,
            "required": required,
            "primary_key": primary_key,
            "entity_uuid": self.entity.uuid,
            "dictionaryelement_uuid": None,
            "allow_invalid": allow_invalid,
        }
        if dictionaryelement:
            data["dictionaryelement_uuid"] = dictionaryelement.uuid

        return self.attr_col.create(data, deserialize=False)

    def add_relationship(
        self,
        name,
        title,
        reference_attribute,
        reference_search_attribute,
        description=None,
        required=False,
        primary_key=False,
    ):
        data = {
            "name": name,
            "title": title,
            "description": description,
            "reference_attribute_uuid": reference_attribute.uuid,
            "reference_search_attribute_uuid": reference_search_attribute.uuid,
            "required": required,
            "primary_key": primary_key,
            "entity_uuid": self.entity.uuid,
        }

        return self.rel_col.create(data, deserialize=False)

    def add_backrelationship(
        self,
        name,
        title,
        reference_relationship,
        description=None,
        single_relation=False,
    ):

        data = {
            "name": name,
            "title": title,
            "description": description,
            "entity_uuid": self.entity.uuid,
            "reference_relationship_uuid": reference_relationship.uuid,
            "single_relation": single_relation,
        }

        return self.brel_col.create(data, deserialize=False)


class EntityContentNavigator(object):
    def __init__(self, entity, application, request):
        self.request = request
        self.collection = content_collection_factory(entity, application)

    def add(self, data):
        return self.collection.create(data, deserialize=False)

    def search(self, *args, **kwargs):
        return self.collection.search(*args, **kwargs)


class EntityContentCollectionBrowser(object):
    def __init__(self, request, application):
        self.request = request
        self.application = application
        self.collection = request.get_collection("morpcc.entity")

    @navmemoize
    def __getitem__(self, key):
        items = self.collection.search(rulez.field["name"] == key)
        if items:
            return EntityContentNavigator(items[0], self.application, self.request)
        raise KeyError(key)

    def keys(self):
        return [e["name"] for e in self.collection.search()]


class ApplicationNavigator(object):
    def __init__(self, application, request):
        self.application = application
        self.request = request
        self.entities = EntityContentCollectionBrowser(request, application)

    @navmemoize
    def __getitem__(self, key):
        return self.entities[key]

    def keys(self):
        return self.entities.keys()

    def values(self) -> typing.List[EntityNavigator]:
        return self.entities.values()


class RefDataKeyNavigator(object):
    def __init__(self, refdatakey, request):
        self.refdatakey = refdatakey
        self.request = request
        self.prop_col = get_refdataprop_collection(request)

    def add_property(self, name, value):
        data = {
            "name": name,
            "value": value,
            "referencedatakey_uuid": self.refdatakey.uuid,
        }
        prop = self.prop_col.create(data, deserialize=False)
        return prop

    @navmemoize
    def __getitem__(self, key):
        props = self.prop_col.search(
            rulez.and_(
                rulez.field["referencedatakey_uuid"] == self.refdatakey.uuid,
                rulez.field["name"] == key,
            )
        )
        if props:
            return props[0]
        return KeyError(key)

    def keys(self):
        return [
            p["name"]
            for p in self.prop_col.search(
                rulez.field["referencedatakey_uuid"] == self.refdatakey.uuid
            )
        ]


class RefDataNavigator(object):
    def __init__(self, refdata, request):
        self.refdata = refdata
        self.request = request
        self.key_col = get_refdatakey_collection(request)

    def add_key(self, name, description=None) -> typing.Optional[RefDataKeyNavigator]:
        data = {
            "name": name,
            "referencedata_uuid": self.refdata.uuid,
            "description": description,
        }
        key = self.key_col.create(data, deserialize=False)
        if key:
            return RefDataKeyNavigator(key, self.request)
        return None

    @navmemoize
    def __getitem__(self, key) -> RefDataKeyNavigator:
        keys = self.key_col.search(
            rulez.and_(
                rulez.field["referencedata_uuid"] == self.refdata.uuid,
                rulez.field["name"] == key,
            )
        )
        if keys:
            return RefDataKeyNavigator(keys[0], self.request)
        raise KeyError(key)

    def keys(self):
        return [
            k["name"]
            for k in self.key_col.search(
                rulez.field["referencedata_uuid"] == self.refdata.uuid
            )
        ]


class DictionaryEntityNavigator(object):
    def __init__(self, dictentity, request):
        self.dictentity = dictentity
        self.request = request
        self.element_col = get_del_collection(request)

    def add_element(
        self,
        name,
        title,
        type_,
        referencedata_name=None,
        referencedata_property="label",
    ):
        data = {
            "name": name,
            "title": title,
            "type": type_,
            "dictionaryentity_uuid": self.dictentity.uuid,
            "referencedata_name": referencedata_name,
            "referencedata_property": referencedata_property,
        }
        el = self.element_col.create(data, deserialize=False)
        return el

    @navmemoize
    def __getitem__(self, key):
        elements = self.element_col.search(
            rulez.and_(
                rulez.field["dictionaryentity_uuid"] == self.dictentity.uuid,
                rulez.field["name"] == key,
            )
        )
        if elements:
            return elements[0]
        raise KeyError(key)

    def keys(self):
        return [
            e["name"]
            for e in self.element_col.search(
                rulez.field["dictionaryentity_uuid"] == self.dictentity.uuid
            )
        ]


class DataDictionaryBrowser(object):
    def __init__(self, request):
        self.request = request
        self.dictentity_col = get_dent_collection(request)

    @navmemoize
    def __getitem__(self, key):
        dents = self.dictentity_col.search(rulez.field["name"] == key)
        if dents:
            return DictionaryEntityNavigator(dents[0], self.request)
        raise KeyError(key)

    def keys(self):
        return [e["name"] for e in self.dictentity_col.search()]


class EntityBrowser(object):
    def __init__(self, schema, request):
        self.schema = schema
        self.request = request
        self.collection = request.get_collection("morpcc.entity")

    @navmemoize
    def __getitem__(self, key):
        items = self.collection.search(
            rulez.and_(
                rulez.field["schema_uuid"] == self.schema.uuid,
                rulez.field["name"] == key,
            )
        )
        if items:
            return EntityNavigator(self.schema, items[0], self.request)
        raise KeyError(key)

    def keys(self):
        return [
            e["name"]
            for e in self.collection.search(
                rulez.field["schema_uuid"] == self.schema.uuid
            )
        ]


class SchemaNavigator(object):
    def __init__(self, schema, request):
        self.schema = schema
        self.request = request
        self.entity_col = request.get_collection("morpcc.entity")
        self.entities = EntityBrowser(schema, request)

    def add_entity(
        self, name, title, icon="database"
    ) -> typing.Optional[EntityNavigator]:
        data = {
            "name": name,
            "title": title,
            "icon": icon,
            "schema_uuid": self.schema.uuid,
        }
        entity = self.entity_col.create(data, deserialize=False)
        if entity:
            return EntityNavigator(self.schema, entity, self.request)
        return None

    def keys(self):
        return self.entities.keys()

    @navmemoize
    def __getitem__(self, key):
        return self.entities[key]


class SchemaBrowser(object):
    def __init__(self, request):
        self.request = request
        self.collection = request.get_collection("morpcc.schema")

    @navmemoize
    def __getitem__(self, key):
        items = self.collection.search(rulez.field["name"] == key)
        if items:
            return SchemaNavigator(items[0], self.request)
        raise KeyError(key)

    def keys(self):
        return [e["name"] for e in self.collection.search()]


class ApplicationBrowser(object):
    def __init__(self, request):
        self.request = request
        self.collection = request.get_collection("morpcc.application")

    @navmemoize
    def __getitem__(self, key):
        items = self.collection.search(rulez.field["name"] == key)
        if items:
            return ApplicationNavigator(items[0], self.request)
        raise KeyError(key)

    def keys(self):
        return [e["name"] for e in self.collection.search()]


class Navigator(object):
    def __init__(self, request):
        self.request = request
        self.app_col = get_app_collection(request)
        self.refdata_col = get_refdata_collection(request)
        self.dictentity_col = get_dent_collection(request)
        self.schema_col = request.get_collection("morpcc.schema")
        self.datadictionary = DataDictionaryBrowser(request)
        self.schemas = SchemaBrowser(request)
        self.applications = ApplicationBrowser(request)

    def add_schema(self, name, title, icon="cube") -> typing.Optional[SchemaNavigator]:
        data = {"name": name, "title": title}
        schema = self.schema_col.create(data, deserialize=False)
        if schema:
            return SchemaNavigator(schema, self.request)

    def add_application(
        self, name, title, schema, icon="cube"
    ) -> typing.Optional[ApplicationNavigator]:
        data = {
            "name": name,
            "title": title,
            "icon": icon,
            "schema_uuid": schema.uuid,
        }
        app = self.app_col.create(data, deserialize=False)
        if app:
            return ApplicationNavigator(app, self.request)
        return None

    def add_referencedata(self, name, title) -> typing.Optional[RefDataNavigator]:
        data = {"name": name, "title": title}
        refdata = self.refdata_col.create(data, deserialize=False)
        if refdata:
            return RefDataNavigator(refdata, self.request)
        return None

    def add_dictionaryentity(
        self, name, title
    ) -> typing.Optional[DictionaryEntityNavigator]:
        data = {"name": name, "title": title}
        dent = self.dictentity_col.create(data, deserialize=False)
        if dent:
            return DictionaryEntityNavigator(dent, self.request)
        return None
