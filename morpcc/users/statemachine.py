from ..app import App
from morpfw.authn.pas.user.model import UserModel
from dataclasses import dataclass
import morpfw


class UserStateMachine(morpfw.StateMachine):

    states = ['new', 'active', 'inactive']
    transitions = [
        {'trigger': 'initialize', 'source': 'new',
            'dest': 'active', 'conditions': ['is_validated']},
        {'trigger': 'activate', 'source': 'inactive', 'dest': 'active'},
        {'trigger': 'deactivate', 'source': 'active', 'dest': 'inactive'},
    ]

    def is_validated(self):
        xattr = self._context.xattrprovider()
        email_validated = xattr.get('morpfw.email.validated', False)
        return email_validated


@App.statemachine(model=UserModel)
def userstatemachine(context):
    return UserStateMachine(context)
