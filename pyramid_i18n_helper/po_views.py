from pyramid.view import view_config, view_defaults
import colander
import deform
from deform import widget
from pyramid.request import Request
import polib
import os
import babel


@view_defaults(route_name='po', renderer='pyramid_i18n_helper:templates/po.jinja2', permission='i18n_helper')
class PoView():
    def __init__(self, context, request: Request):
        self.request = request
        self.context = context
        _ = request.translate
        self.helper = request.registry['i18n_helper']
        self.lang = request.matchdict['lang']
        self.po = polib.pofile(os.path.join(self.helper.package_dir, 'locale', self.lang, 'LC_MESSAGES',
                                            '{0}.po'.format(self.helper.package_name)))

        self.locale = babel.Locale(*babel.parse_locale(self.lang))

    def form_creator(self):
        po_entries = {entry.msgid: entry.msgstr for entry in self.po}

        class PoEntry(colander.Schema):
            def after_bind(self, schema, kwargs):
                for entry in po_entries:
                    self[entry] = colander.SchemaNode(
                        colander.String(),
                        title=entry,
                        missing='',
                        default=po_entries.get(entry),
                        # description=po_entries.get(entry)
                    )

        class MainSchema(colander.Schema):
            msgid = PoEntry()

        def validator(node, appstruct):
            return True

        schema = MainSchema(validator=validator)
        schema = schema.bind(request=self.request)
        self.form = deform.Form(schema, use_ajax=False, action=self.request.route_url('po', lang=self.lang))
        self.form.buttons.append(deform.Button(name='submit', title='submit'))
        self.form.buttons.append(deform.Button(name='reload', title='reload'))
        return self.form

    @view_config(request_method="GET")
    def get_view(self):

        request = self.request
        context = self.context
        _ = request.translate

        self.form_creator()

        return {"form": self.form, 'locale': self.locale}

    @view_config(request_method="POST")
    def post_view(self):

        request = self.request
        context = self.context
        _ = request.translate
        lang = self.lang

        controls = request.POST.items()

        try:
            appstruct = self.form.validate(controls)


        except:
            appstruct = None
            self.request.message_queue.add(message_type='danger', body='not_valid_data')

        if appstruct:
            # TODO:
            for entry in self.po:
                entry.msgstr = appstruct['msgid'].get(entry.msgid, '')

            self.po.save(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES',
                                      '{0}.po'.format(self.helper.package_name)))
            self.po.save_as_mofile(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES',
                                                '{0}.mo'.format(self.helper.package_name)))

            self.request.message_queue.add(message_type='success', body='success')

        return self.get_view()

    @view_config(request_param='reload')
    def reload_view(self):

        request = self.request
        context = self.context

        _ = request.translate

        lang = request.matchdict['lang']

        pot = polib.pofile(os.path.join(self.helper.package_dir, 'locale', '{0}.pot'.format(self.helper.package_name)))
        self.po = polib.pofile(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES',
                                            '{0}.po'.format(self.helper.package_name)))
        po_entries = {entry.msgid: entry.msgstr for entry in self.po}

        for entry in pot:
            if not entry.msgid in po_entries:
                self.po.append(entry)

        self.po.save(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES',
                                  '{0}.po'.format(self.helper.package_name)))
        self.po.save_as_mofile(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES',
                                            '{0}.mo'.format(self.helper.package_name)))
        return self.get_view()
