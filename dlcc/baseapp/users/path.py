from .model import UserModelUI, UserCollectionUI
from ..app import App
from morpfw.auth.user.path import get_user, get_user_collection


@App.path(model=UserCollectionUI, path='/manage-users')
def get_user_collection_ui(request):
    authapp = request.app.get_authnz_provider()
    newreq = request.copy(app=authapp)
    col = get_user_collection(newreq)
    return UserCollectionUI(newreq, col)
