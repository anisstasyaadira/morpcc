from .app import App
from morpfw.authn.pas.user.path import get_user_collection


@App.portletprovider(name='morpcc.left-portlets')
def left_portlets(context, request):
    return ['morpcc.profile', 'morpcc.main_navigation']


@App.portletprovider(name='morpcc.top-navigation')
def topnav_portlets(context, request):
    return ['morpcc.topnav']


@App.portlet(name='morpcc.main_navigation', template='master/portlet/navigation.pt')
def navigation_portlet(context, request):
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
    general_children = [
        {'title': 'Home', 'icon': 'home', 'href': request.relative_url('/')},
    ]

    if types_nav:
        general_children.append({'title': 'Collections', 'icon': 'database',
                                 'children': types_nav})
    return {
        'navtree': [{
            'section': 'General',
            'children': general_children
        }, {
            'section': 'Administrative',
            'children': [
                {'title': 'Settings',
                 'icon': 'cog',
                 'children': [{
                     'title': 'User',
                     'href': request.relative_url('/manage-users/+listing'),
                 }, {
                     'title': 'Group',
                     'href': request.relative_url('/manage-groups/+listing'),
                 }, {
                     'title': 'API Keys',
                     'href': request.relative_url('/manage-apikeys/+listing')
                 }, {
                     'title': 'Personal',
                     'href': request.relative_url('/personal-settings')
                 }]}
            ]
        }]
    }


@App.portlet(name='morpcc.profile', template='master/portlet/profile.pt')
def profile_portlet(context, request):
    userid = request.identity.userid
    newreq = request.get_authn_request()
    usercol = get_user_collection(newreq)
    user = usercol.get_by_userid(userid)
    xattr = user.xattrprovider()
    return {
        'displayname': xattr['displayname'],
        'profilephoto_url': newreq.link(user, '+blobs?field=profile-photo')
    }


@App.portlet(name='morpcc.topnav', template='master/portlet/topnav.pt')
def topnav_portlet(context, request):
    userid = request.identity.userid
    newreq = request.get_authn_request()
    usercol = get_user_collection(newreq)
    user = usercol.get_by_userid(userid)
    xattr = user.xattrprovider()
    return {
        'displayname': xattr['displayname'],
        'profilephoto_url': newreq.link(user, '+blobs?field=profile-photo')
    }
