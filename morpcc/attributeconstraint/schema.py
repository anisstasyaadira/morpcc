import typing
from dataclasses import dataclass, field

import morpfw
from deform.widget import TextAreaWidget
from morpcc.deform.referencewidget import ReferenceWidget
from morpcc.deform.vocabularywidget import VocabularyWidget


@dataclass
class AttributeConstraintSchema(morpfw.Schema):

    title: typing.Optional[str] = None
    validator: typing.Optional[str] = field(
        default=None,
        metadata={
            "required": True,
            "deform.widget": VocabularyWidget("morpcc.attributevalidators"),
        },
    )
    parameters: typing.Optional[str] = field(default=None, metadata={"format": "text"})
    attribute_uuid: typing.Optional[str] = field(
        default=None,
        metadata={
            "required": True,
            "editable": False,
            "format": "uuid",
            "deform.widget": ReferenceWidget("morpcc.attribute"),
        },
    )
