import typing
from dataclasses import dataclass, field

import morpfw

from ..deform.referencewidget import ReferenceWidget
from ..validator.reference import ReferenceValidator


@dataclass
class EntityValidatorAssignmentSchema(morpfw.Schema):

    entity_uuid: typing.Optional[str] = field(
        default=None,
        metadata={
            "format": "uuid",
            "required": True,
            "validators": [ReferenceValidator("morpcc.entity", "uuid")],
            "deform.widget": ReferenceWidget("morpcc.entity", "title", "uuid"),
        },
    )
    entityvalidator_name: typing.Optional[str] = field(
        default=None,
        metadata={
            "required": True,
            "validators": [ReferenceValidator("morpcc.entityvalidator", "name")],
            "deform.widget": ReferenceWidget("morpcc.entityvalidator", "title", "name"),
        },
    )
