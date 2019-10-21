import typing
import deform
import morpfw
import morepath
from ..util import dataclass_to_colander


class WizardStep(object):
    title: str = "step"
    description: str = "step description"
    template: str
    index: int
    wizard: 'Wizard'

    def __init__(self, context, request, wizard, index):
        self.context = context
        self.request = request
        self.wizard = wizard
        self.index = index

    def macro(self, load_template):
        return load_template(self.template).macros.step

    def handler_macro(self, load_template):
        return load_template(self.template).macros['step-handler']

    def can_handle(self) -> bool:
        """
        check if the current form submission belong to this step, and
        return True if this step will handle the form processing
        """
        return False

    def finalize(self) -> bool:
        """
        this is run when wizard is finalized, check that all
        needed values are here
        """
        return True

    @property
    def sessiondata(self):
        req = self.request
        req.session.setdefault('wizard_data', {})
        req.session['wizard_data'].setdefault(self.wizard.id, {})
        req.session['wizard_data'][self.wizard.id].setdefault('steps', {})
        data = req.session['wizard_data'][self.wizard.id]['steps'].get(
            self.index, None)
        return data

    @sessiondata.setter
    def sessiondata(self, data):
        req = self.request
        req.session.setdefault('wizard_data', {})
        req.session['wizard_data'].setdefault(self.wizard.id, {})
        req.session['wizard_data'][self.wizard.id].setdefault('steps', {})
        req.session['wizard_data'][self.wizard.id]['steps'][self.index] = data
        req.session.save()

    def clear_sessiondata(self):
        req = self.request
        req.session.setdefault('wizard_data', {})
        if self.sessiondata:
            del req.session['wizard_data'][self.wizard.id]['steps'][self.index]
            req.session.save()

    def handle(self):
        return {}


class FormWizardStep(WizardStep):

    template: str = 'master/wizard/form-step.pt'
    schema: object

    def get_form(self, formid):
        formschema = dataclass_to_colander(self.schema)
        return deform.Form(formschema(), formid=formid)

    def can_handle(self):
        request = self.request
        formid = request.POST.get('__formid__')
        if formid:
            try:
                step = int(formid.split('-')[-1])
            except:
                return False

            if step == self.index:
                return True

        return False

    def process_form(self):
        request = self.request
        formschema = dataclass_to_colander(self.schema)
        controls = request.POST.items()
        form = deform.Form(formschema(), formid=request.POST.get('__formid__'))
        failed = False
        try:
            data = form.validate(controls)
        except deform.ValidationFailure as e:
            form = e
            failed = True
            data = controls

        return {
            'form': form,
            'failed': failed,
            'data': data
        }

    def handle(self):
        result = self.process_form()

        # FIXME remember the value in session
        if result['failed']:
            return {
                'step': self,
                'form': result['form']
            }

        self.sessiondata = result['data']
        return {
            'step': self,
            'form': result['form']
        }


class Wizard(object):
    steps: typing.List[WizardStep] = []
    style: str

    def __init__(self, context, request, identifier, style='horizontal'):
        self.id = identifier
        self.context = context
        self.style = style
        self.request = request
        steps = []
        for idx, step in enumerate(self.steps):
            s = step(context, request, self, idx)
            steps.append(s)
        self.steps = steps

    def macro(self, load_template, macro='wizard'):
        template = 'master/wizard/wizard-macros.pt'
        return load_template(template).macros[macro]

    def finalize(self):
        self.clear()
        return morepath.redirect(self.request.link(self.context))

    def clear(self):
        del self.request.session['wizard_data'][self.id]
        self.request.session.save()

    def handle(self):
        request = self.request
        for step in self.steps:
            if step.can_handle():
                return step.handle()

        finalize_form = '%s-finalize' % self.id
        if request.POST.get('__formid__') == finalize_form:
            for step in self.steps:
                step.finalize()

            return self.finalize()

        raise ValueError('Unable to process wizard form submission')
