from pyramid.view import view_config, view_defaults
import colander
import deform
from deform import widget
from pyramid.request import Request
import polib
import os



@view_defaults(route_name='po', renderer='templates/po.jinja2', permission='admin')
class PoView():
    def __init__(self, context, request:Request):

        self.request = request
        self.context = context
        _ = request.translate

        self.helper = request.registry['i18n_helper']


        self.lang = request.matchdict['lang']
        lang = self.lang

        self.po = polib.pofile(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES', '{0}.po'.format(self.helper.package_name)))
        po = self.po
        self.po_entries = {entry.msgid: entry.msgstr for entry in po}
        po_entries = self.po_entries


        class PoEntry(colander.Schema):

            def after_bind(self, schema, kwargs):
                for entry in po_entries:
                    self[entry] = colander.SchemaNode(
                        colander.String(),
                        title=entry,
                        missing = '',
                        default = po_entries.get(entry),
                        # description=po_entries.get(entry)
                    )


        class MainSchema(colander.Schema):
            msgid = PoEntry()

        def validator(node, appstruct):
            print('appstruct is: ', appstruct)
            return True

        schema = MainSchema(validator=validator)
        schema = schema.bind(request=request)
        self.form = deform.Form(schema, use_ajax=False, action=request.route_url('po', lang=lang))
        self.form.buttons.append(deform.Button(name='submit', title='submit'))
        self.form.buttons.append(deform.Button(name='reload', title='reload'))


    @view_config(request_method="GET")
    def get_view(self):

        request = self.request
        context = self.context
        _ = request.translate

        return {"form": self.form}

    @view_config(request_method="POST")
    def post_view(self):

        request = self.request
        context = self.context
        _ = request.translate
        lang = self.lang
        po = self.po


        controls = request.POST.items()

        try:
            appstruct = self.form.validate(controls)


        except:
            appstruct = None
            print('no validate')

        if appstruct:
            # TODO:
            for entry in self.po:
                entry.msgstr = appstruct['msgid'].get(entry.msgid, '')

            po.save(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES', '{0}.po'.format(self.helper.package_name)))
            po.save_as_mofile(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES', '{0}.mo'.format(self.helper.package_name)))

        return self.get_view()



    @view_config(request_param='reload')
    def reload_view(self):

        request = self.request
        context = self.context

        _ = request.translate

        lang = request.matchdict['lang']

        pot = polib.pofile(os.path.join(self.helper.package_dir, 'locale', '{0}.pot'.format(self.helper.package_name)))
        po = polib.pofile(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES', '{0}.po'.format(self.helper.package_name)))
        po_entries = {entry.msgid: entry.msgstr for entry in po}

        for entry in pot:
            if not entry.msgid in po_entries:
                po.append(entry)

        po.save(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES', '{0}.po'.format(self.helper.package_name)))
        po.save_as_mofile(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES', '{0}.mo'.format(self.helper.package_name)))
        return self.get_view()

