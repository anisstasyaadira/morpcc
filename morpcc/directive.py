import dectate
import reg
import morepath
from morepath.directive import SettingAction
from .portletregistry import PortletRegistry, PortletProviderRegistry

PORTLET_FACTORY_IDS: dict = {}


class PortletFactoryAction(dectate.Action):

    config = {"portlet_registry": PortletRegistry}

    depends = [SettingAction]

    def __init__(self, name, template=None, permission=None):
        self.template = template
        self.name = name
        self.permission = permission

    def identifier(self, portlet_registry: PortletRegistry):
        return self.name

    def perform(self, obj, portlet_registry: PortletRegistry):
        portlet_registry.register(
            obj, name=self.name, template=self.template, permission=self.permission
        )


class PortletProviderFactoryAction(dectate.Action):

    config = {"portletprovider_registry": PortletProviderRegistry}

    depends = [SettingAction]

    def __init__(self, name, permission=None):
        self.name = name
        self.permission = permission

    def identifier(self, portletprovider_registry: PortletProviderRegistry):
        return self.name

    def perform(self, obj, portletprovider_registry: PortletProviderRegistry):
        portletprovider_registry.register(
            obj, name=self.name, permission=self.permission
        )


class StructureColumnAction(dectate.Action):

    app_class_arg = True

    def __init__(self, model, name):
        self.model = model
        self.name = name

    def identifier(self, app_class):
        return str((app_class, self.model, self.name))

    def perform(self, obj, app_class):
        app_class.get_structure_column.register(
            reg.methodify(obj),
            model=self.model,
            request=morepath.Request,
            name=self.name,
        )


class SchemaExtenderAction(dectate.Action):

    app_class_arg = True

    def __init__(self, schema):
        self.schema = schema

    def identifier(self, app_class):
        return str((app_class, self.schema))

    def perform(self, obj, app_class):
        app_class.get_schemaextender.register(reg.methodify(obj), schema=self.schema)


class MessagingProviderAction(dectate.Action):

    app_class_arg = True

    def __init__(self, name):
        self.name = name

    def identifier(self, app_class):
        return str((app_class, self.name))

    def perform(self, obj, app_class):
        app_class.get_messagingprovider.register(
            reg.methodify(obj), request=morepath.Request, name=self.name
        )


class VocabularyAction(dectate.Action):

    app_class_arg = True

    def __init__(self, name):
        self.name = name

    def identifier(self, app_class):
        return str((app_class, self.name))

    def perform(self, obj, app_class):
        app_class.get_vocabulary.register(
            reg.methodify(obj), request=morepath.Request, name=self.name
        )


class IndexerAction(dectate.Action):

    app_class_arg = True

    def __init__(self, model, name):
        self.model = model
        self.name = name

    def identifier(self, app_class):
        return str((app_class, self.model, self.name))

    def perform(self, obj, app_class):
        app_class.get_indexer.register(
            reg.methodify(obj),
            model=self.model,
            name=self.name,
        )


