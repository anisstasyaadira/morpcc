import morpfw
from RestrictedPython import compile_restricted

from ..restrictedpython import get_restricted_function
from .modelui import EntityValidatorCollectionUI, EntityValidatorModelUI
from .schema import EntityValidatorSchema


class EntityValidatorWrapper(object):

    __required_binds__ = ["context"]

    def __init__(self, validator, message):
        self.validator = validator
        self.message = message

    def __call__(self, request, schema, data, mode=None, context=None):
        obj = context.validation_dict()
        if not self.validator(obj):
            return {"message": self.message}


class EntityValidatorModel(morpfw.Model):
    schema = EntityValidatorSchema

    def ui(self):
        return EntityValidatorModelUI(self.request, self, self.collection.ui())

    @morpfw.memoize()
    def bytecode(self):
        bytecode = compile_restricted(
            self["code"],
            filename="<EntityValidator {}>".format(self["name"]),
            mode="exec",
        )
        return bytecode

    @morpfw.memoize()
    def function(self):
        function = get_restricted_function(
            self.request.app, self.bytecode(), "validate"
        )
        return function

    def schema_validator(self):
        return EntityValidatorWrapper(self.function(), self["error_message"])


class EntityValidatorCollection(morpfw.Collection):
    schema = EntityValidatorSchema

    def ui(self):
        return EntityValidatorCollectionUI(self.request, self)
