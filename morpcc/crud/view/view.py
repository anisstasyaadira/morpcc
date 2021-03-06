import html

import deform
import morepath
import morpfw
from morpfw.crud import permission as crudperms

from ...app import App
from ...deform.referencewidget import ReferenceWidget
from ...util import dataclass_to_colander
from ..model import CollectionUI, ModelUI


@App.view(model=CollectionUI)
def collection_index(context, request):
    return morepath.redirect(request.link(context, "+%s" % context.default_view))


@App.view(model=ModelUI)
def model_index(context, request):
    return morepath.redirect(request.link(context, "+%s" % context.default_view))


@App.html(
    model=ModelUI,
    name="view",
    template="master/crud/view.pt",
    permission=crudperms.View,
)
def view(context, request):
    formschema = dataclass_to_colander(
        context.model.schema,
        request=request,
        include_fields=context.view_include_fields,
        exclude_fields=context.view_exclude_fields,
    )

    xattrprovider = context.model.xattrprovider()
    if xattrprovider:
        xattrformschema = dataclass_to_colander(xattrprovider.schema, request=request)
    else:
        xattrformschema = None
    data = context.model.data.as_dict()
    sm = context.model.statemachine()

    metadataschema = dataclass_to_colander(
        morpfw.Schema, request=request, exclude_fields=["blobs", "xattrs"]
    )
    # FIXME: widget override should be part of dataclass_to_colander
    for f in metadataschema.__all_schema_nodes__:
        if f.name == "creator":
            f.widget = ReferenceWidget(
                "morpfw.pas.user", term_field="username", value_field="uuid"
            )
    if sm:
        triggers = [
            i for i in sm._machine.get_triggers(sm.state) if not i.startswith("to_")
        ]
    else:
        triggers = None

    fs = formschema()
    fs.bind(context=context, request=request)

    mfs = metadataschema()
    mfs.bind(context=context, request=request)

    xfs = None
    if xattrprovider:
        xfs = xattrformschema()
        xfs.bind(context=context, request=request)

    return {
        "page_title": "View %s" % html.escape(str(context.model.__class__.__name__)),
        "form_title": "View",
        "metadataform": deform.Form(mfs),
        "form": deform.Form(fs),
        "form_data": data,
        "xattrform": deform.Form(xfs) if xattrprovider else None,
        "xattrform_data": xattrprovider.as_dict() if xattrprovider else None,
        "readonly": True,
        "transitions": triggers,
    }


@App.html(
    model=ModelUI, name="preview", permission=crudperms.View,
)
def preview(context, request):
    formschema = dataclass_to_colander(
        context.model.schema,
        request=request,
        include_fields=context.view_include_fields,
        exclude_fields=context.view_exclude_fields,
    )

    fs = formschema()
    fs.bind(context=context, request=request)
    form = deform.Form(fs)
    form_data = context.model.data.as_dict()
    return form.render(
        appstruct=form_data, readonly=True, request=request, context=context
    )


@App.html(
    model=ModelUI,
    name="modal-view",
    template="master/crud/modal-view.pt",
    permission=crudperms.View,
)
def modal_view(context, request):
    return view(context, request)


@App.html(
    model=ModelUI,
    name="modal-close",
    template="master/crud/modal-close.pt",
    permission=crudperms.View,
)
def modal_close(context, request):
    return {}


@App.html(
    model=CollectionUI,
    name="modal-close",
    template="master/crud/modal-close.pt",
    permission=crudperms.View,
)
def collection_modal_close(context, request):
    return {}


@App.view(
    model=ModelUI, name="statemachine", permission=crudperms.Edit, request_method="POST"
)
def statemachine(context, request):
    transition = request.POST.get("transition", None)
    sm = context.model.statemachine()
    if transition:
        attr = getattr(sm, transition, None)
        if attr:
            attr()
            request.notify("success", "State updated", "Object state have been updated")
            return morepath.redirect(request.link(context))
    request.notify(
        "error", "Unknown transition", 'Transition "%s" is unknown' % transition
    )
    return morepath.redirect(request.link(context))
