import html

import colander
import deform
import morepath
from morpfw.crud import permission as crudperms
from morpfw.crud.errors import AlreadyExistsError, ValidationError
from webob.exc import HTTPFound, HTTPNotFound

from ...app import App
from ...util import dataclass_to_colander
from ..model import CollectionUI, ModelUI


@App.html(
    model=ModelUI,
    name="edit",
    template="master/crud/form.pt",
    permission=crudperms.Edit,
)
def edit(context, request):
    formschema = dataclass_to_colander(
        context.model.schema,
        request=request,
        mode="edit",
        include_fields=context.edit_include_fields,
        exclude_fields=context.edit_exclude_fields,
    )
    data = context.model.data.as_dict()
    fs = formschema()
    fs.bind(context=context, request=request)
    return {
        "page_title": "Edit %s" % html.escape(str(context.model.__class__.__name__)),
        "form_title": "Edit",
        "form": deform.Form(fs, buttons=("Submit",)),
        "form_data": data,
    }


@App.html(
    model=ModelUI,
    name="modal-edit",
    template="master/crud/modal-form.pt",
    permission=crudperms.Edit,
)
def modal_edit(context, request):
    return edit(context, request)


@App.html(
    model=ModelUI,
    name="edit",
    template="master/crud/form.pt",
    permission=crudperms.Edit,
    request_method="POST",
)
def process_edit(context, request):
    formschema = dataclass_to_colander(
        context.model.schema,
        request=request,
        mode="edit-process",
        include_fields=context.edit_include_fields,
        exclude_fields=context.edit_exclude_fields,
        include_schema_validators=False,
    )
    fs = formschema()
    fs.bind(context=context, request=request)
    data = context.model.data.as_dict()
    controls = list(request.POST.items())
    form = deform.Form(fs, buttons=("Submit",))

    failed = False
    try:
        data = form.validate(controls)
    except deform.ValidationFailure as e:
        form = e
        failed = True
    if not failed:
        try:
            context.model.update(data, deserialize=False)
        except ValidationError as e:
            failed = True
            for fe in e.field_errors:
                node = form
                if fe.path in form:
                    node = form[fe.path]
                node_error = colander.Invalid(node.widget, fe.message)
                node.widget.handle_error(node, node_error)
        if not failed:
            return morepath.redirect(request.link(context))

    @request.after
    def set_header(response):
        response.headers.add("X-MORP-FORM-FAILED", "True")

    return {
        "page_title": "Edit %s" % html.escape(str(context.model.__class__.__name__)),
        "form_title": "Edit",
        "form": form,
        "form_data": data,
    }


@App.html(
    model=ModelUI,
    name="modal-edit",
    template="master/crud/modal-form.pt",
    permission=crudperms.Edit,
    request_method="POST",
)
def modal_process_edit(context, request):
    result = process_edit(context, request)
    if isinstance(result, HTTPFound):
        return morepath.redirect(request.link(context, "+modal-close"))
    return result


@App.html(
    model=ModelUI,
    name="xattredit",
    template="master/crud/form.pt",
    permission=crudperms.Edit,
)
def xattredit(context, request):

    xattrprovider = context.model.xattrprovider()
    if xattrprovider:
        xattrformschema = dataclass_to_colander(xattrprovider.schema, request=request)
    else:
        raise HTTPNotFound()

    data = xattrprovider.as_dict()
    return {
        "page_title": "Edit %s Extended Attributes"
        % html.escape(str(context.model.__class__.__name__)),
        "form_title": "Edit Extended Attributes",
        "form": deform.Form(xattrformschema(), buttons=("Submit",)),
        "form_data": data,
    }


@App.html(
    model=ModelUI,
    name="modal-xattredit",
    template="master/crud/modal-form.pt",
    permission=crudperms.Edit,
)
def modal_xattredit(context, request):
    return xattredit(context, request)


@App.html(
    model=ModelUI,
    name="xattredit",
    template="master/crud/form.pt",
    permission=crudperms.Edit,
    request_method="POST",
)
def process_xattredit(context, request):

    xattrprovider = context.model.xattrprovider()
    if xattrprovider:
        xattrformschema = dataclass_to_colander(xattrprovider.schema, request=request)
    else:
        raise HTTPNotFound()

    fs = xattrformschema()
    fs.bind(context=context, request=request)
    data = xattrprovider.as_dict()
    controls = list(request.POST.items())
    form = deform.Form(fs, buttons=("Submit",))

    failed = False
    try:
        data = form.validate(controls)
    except deform.ValidationFailure as e:
        form = e
        failed = True
    if not failed:
        # FIXME: model update should allow datetime object
        xattrprovider.update(data)
        return morepath.redirect(request.link(context))

    return {
        "page_title": "Edit %s" % html.escape(str(context.model.__class__.__name__)),
        "form_title": "Edit",
        "form": form,
        "form_data": data,
    }


@App.html(
    model=ModelUI,
    name="modal-xattredit",
    template="master/crud/modal-form.pt",
    permission=crudperms.Edit,
    request_method="POST",
)
def modal_process_xattredit(context, request):
    result = process_xattredit(context, request)
    if isinstance(result, HTTPFound):
        return morepath.redirect(request.link(context, "+modal-close"))
    return result
