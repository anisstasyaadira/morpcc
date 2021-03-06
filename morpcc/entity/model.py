import typing
from dataclasses import field, make_dataclass

import morpfw
import rulez
from morpfw.crud.storage.pgsqlstorage import PgSQLStorage
from sqlalchemy import MetaData

from ..deform.refdatawidget import ReferenceDataWidget
from ..deform.referencewidget import ReferenceWidget
from ..validator.reference import ReferenceValidator
from .modelui import EntityCollectionUI, EntityModelUI
from .schema import EntitySchema


class EntityModel(morpfw.Model):
    schema = EntitySchema

    def ui(self):
        return EntityModelUI(self.request, self, self.collection.ui())

    def icon(self):
        return self["icon"] or "database"

    def dataclass(self, validators=None, widgets=None):
        validators = validators or {}
        widgets = widgets or {}
        attrs = []
        primary_key = []
        brels = [
            b["reference_relationship_uuid"] for b in self.backrelationships().values()
        ]

        for k, attr in self.attributes().items():
            metadata = attr.field_metadata()
            if attr.uuid in brels:
                metadata["index"] = True

            name = attr["name"]
            if validators.get(name, []):
                metadata.setdefault("validators", [])
                metadata["validators"] += validators[name]
            if widgets.get(k, None):
                metadata["deform.widget"] = widgets[name]
            attrs.append(
                (attr["name"], attr.datatype(), field(default=None, metadata=metadata))
            )
            if attr["primary_key"]:
                primary_key.append(attr["name"])

        for r, rel in self.relationships().items():
            refsearch = rel.reference_search_attribute()
            ref = rel.reference_attribute()
            dm = ref.entity()

            if refsearch:
                # refsearch field and ref field must come from the same entity
                assert dm["uuid"] == refsearch.entity()["uuid"]
            metadata = {
                "required": rel["required"],
                "title": rel["title"],
                "description": rel["description"],
                "validators": [],
                "index": True,
            }

            name = rel["name"]
            if validators.get(name, []):
                metadata.setdefault("validators", [])
                metadata["validators"] += validators[name]
            if widgets.get(name, None):
                metadata["deform.widget"] = widgets[name]

            attrs.append(
                (rel["name"], rel.datatype(), field(default=None, metadata=metadata))
            )

            if rel["primary_key"]:
                primary_key.append(rel["name"])

        name = self["name"] or "Model"

        bases = []
        for behavior in self.behaviors():
            bases.append(behavior.schema)

        bases.append(morpfw.Schema)

        dc = make_dataclass(name, fields=attrs, bases=tuple(bases))
        if primary_key:
            dc.__unique_constraint__ = tuple(primary_key)

        if not self["allow_invalid"]:
            dc.__validators__ = [
                ev.schema_validator() for ev in self.entity_validators()
            ]
        return dc

    @morpfw.requestmemoize()
    def attributes(self):
        attrcol = self.request.get_collection("morpcc.attribute")
        attrs = attrcol.search(rulez.field["entity_uuid"] == self.uuid)
        result = {}

        for attr in attrs:
            result[attr["name"]] = attr

        return result

    @morpfw.requestmemoize()
    def effective_attributes(self):

        result = {}

        attrs = self.attributes()

        for behavior in self.behaviors():
            for n, attr in behavior.schema.__dataclass_fields__.items():
                if n in attrs.keys():
                    continue

                title = n
                if attr.metadata.get("title", None):
                    title = attr.metadata["title"]
                result[n] = {"title": title, "name": n}

        for n, attr in attrs.items():
            result[n] = {"title": attr["title"], "name": n}

        return result

    @morpfw.requestmemoize()
    def relationships(self):
        relcol = self.request.get_collection("morpcc.relationship")
        rels = relcol.search(rulez.field["entity_uuid"] == self.uuid)

        result = {}

        for rel in rels:
            result[rel["name"]] = rel

        return result

    @morpfw.requestmemoize()
    def backrelationships(self):
        brelcol = self.request.get_collection("morpcc.backrelationship")
        brels = brelcol.search(rulez.field["entity_uuid"] == self.uuid)
        result = {}
        for brel in brels:
            result[brel["name"]] = brel

        return result

    @morpfw.requestmemoize()
    def behaviors(self):
        bhvcol = self.request.get_collection("morpcc.behaviorassignment")
        assignments = bhvcol.search(rulez.field["entity_uuid"] == self.uuid)
        behaviors = []
        for assignment in assignments:
            behavior = self.request.app.config.behavior_registry.get_behavior(
                assignment["behavior"], self.request
            )
            behaviors.append(behavior)

        return behaviors

    @morpfw.requestmemoize()
    def entity_schema(self):
        col = self.request.get_collection("morpcc.schema")
        schema = col.get(self["schema_uuid"])
        return schema

    @morpfw.requestmemoize()
    def entity_validators(self):
        col = self.request.get_collection("morpcc.entityvalidatorassignment")
        assignments = col.search(rulez.field["entity_uuid"] == self.uuid)
        validators = [v.validator() for v in assignments]
        return validators


class EntityCollection(morpfw.Collection):
    schema = EntitySchema

    def ui(self):
        return EntityCollectionUI(self.request, self)
