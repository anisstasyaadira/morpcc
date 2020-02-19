import morpfw
import morpfw.sql
import sqlalchemy as sa
import sqlalchemy_jsonfield as sajson

from .model import RelationshipModel


class Relationship(morpfw.sql.Base):

    __tablename__ = "morpcc_relationship"

    name = sa.Column(sa.String(length=1024))
    title = sa.Column(sa.String(length=1024))
    description = sa.Column(sa.Text())
    datamodel_uuid = sa.Column(morpfw.sql.GUID)
    reference_attribute_uuid = sa.Column(morpfw.sql.GUID)
    reference_search_attribute_uuid = sa.Column(morpfw.sql.GUID)
    required = sa.Column(sa.Boolean())


class RelationshipStorage(morpfw.SQLStorage):
    model = RelationshipModel
    orm_model = Relationship
