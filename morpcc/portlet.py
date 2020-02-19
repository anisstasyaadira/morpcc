from .app import App
from .users.path import get_current_user_model_ui
from .notification.path import get_collection_ui as get_notification_collection_ui
from .application.path import get_collection as get_app_collection
from morpfw.authn.pas.user.path import get_user_collection
from webob.exc import HTTPUnauthorized
import rulez


@App.portletprovider(name='morpcc.left-portlets')
def left_portlets(context, request):
    return ['morpcc.profile', 'morpcc.main_navigation']


@App.portletprovider(name='morpcc.top-navigation')
def topnav_portlets(context, request):
    return ['morpcc.topnav']


@App.portlet(name='morpcc.main_navigation', template='master/portlet/navigation.pt')
def navigation_portlet(context, request):

    general_children = [
        {'title': 'Home', 'icon': 'home', 'href': request.relative_url('/')},
    ]


    appcol = get_app_collection(request)
    apps_nav = []
    for app in appcol.search():
        appui = app.ui()
        apps_nav.append(
            {
                "title": app["title"],
                "href": request.link(appui, "+{}".format(appui.default_view)),
            }
        )

    if apps_nav:
        general_children.append(
            {"title": "Applications", "icon": "cubes", "children": apps_nav}
        )


    types = request.app.config.type_registry.get_typeinfos(request)
    types_nav = []
    for typeinfo in types.values():
        if typeinfo.get('internal', False):
            continue
        collectionui = typeinfo['collection_ui_factory'](request)
        types_nav.append({
            'title': typeinfo['title'],
            'href': request.link(collectionui, '+%s' % collectionui.default_view)
        })
    types_nav.sort(key=lambda x: x['title'])

    if types_nav:
        general_children.append({'title': 'Collections', 'icon': 'database',
                                 'children': types_nav})



    return {
        'navtree': [{
            'section': 'General',
            'children': general_children
        }]
    }


@App.portlet(name='morpcc.profile', template='master/portlet/profile.pt')
def profile_portlet(context, request):
    user = get_current_user_model_ui(request)
    if user is None:
        raise HTTPUnauthorized
    username = user.model['username']
    xattr = user.model.xattrprovider()
    if user.model.get_blob('profile-photo'):
        photo_url = request.link(user, '+download?field=profile-photo')
    else:
        photo_url = request.relative_url(
            '/__static__/morpcc/img/person-icon.jpg')
    return {
        'displayname': xattr.get('displayname', username),
        'profilephoto_url': photo_url
    }


@App.portlet(name='morpcc.topnav', template='master/portlet/topnav.pt')
def topnav_portlet(context, request):
    user = get_current_user_model_ui(request)
    username = user.model['username']
    xattr = user.model.xattrprovider()
    if user.model.get_blob('profile-photo'):
        photo_url = request.link(user, '+download?field=profile-photo')
    else:
        photo_url = request.relative_url(
            '/__static__/morpcc/img/person-icon.jpg')

    notif_col = get_notification_collection_ui(request)
    notifs = notif_col.search(
        query=rulez.field['userid'] == request.identity.userid, limit=10,
        order_by=('created', 'desc'))
    unread_notifs = notif_col.collection.aggregate(
        query=rulez.and_(rulez.field['read'] == None,
                         rulez.field['userid'] == request.identity.userid),
        group={'count': {'function': 'count', 'field': 'uuid'}})
    return {
        'displayname': xattr.get('displayname', username),
        'profilephoto_url': photo_url,
        'notifications': notifs,
        'notification_count': unread_notifs[0]['count'],
    }
