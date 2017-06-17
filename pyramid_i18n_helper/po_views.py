from pyramid.view import view_config, view_defaults
import colander
import deform
from deform import widget
from pyramid.request import Request
import polib
import os
import babel


@view_defaults(route_name='i18n_helper.po', renderer='pyramid_i18n_helper:templates/po.jinja2', permission='i18n_helper')
class PoView():
    def __init__(self, context, request: Request):
        self.request = request
        self.context = context
        _ = request.translate
        self.helper = request.registry['i18n_helper']
        self.lang = request.matchdict['lang']
        self.domain = request.matchdict['domain']

        self.locale = babel.Locale(*babel.parse_locale(self.lang))

        self.pot_file_path = os.path.join(self.helper.package_dir, 'locale', '{0}.pot'.format(self.domain))
        self.po_file_path = os.path.join(self.helper.package_dir, 'locale', self.lang, 'LC_MESSAGES',
                                         '{0}.po'.format(self.domain))
        self.mo_file_path = os.path.join(self.helper.package_dir, 'locale', self.lang, 'LC_MESSAGES',
                                         '{0}.mo'.format(self.domain))

        if os.path.exists(self.po_file_path):
            self.po = polib.pofile(self.po_file_path)
        else:
            self.po = polib.POFile()

    def create_form(self):
        _ = self.request.translate
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
        self.form = deform.Form(schema,
                                use_ajax=False,
                                action=self.request.route_url('i18n_helper.po', lang=self.lang,domain=self.domain))
        self.form.buttons.append(deform.Button(name='submit', title=_('i18n_translate_submit', domain='i18n_helper')))
        self.form.buttons.append(deform.Button(name='reload', title=_('i18n_translate_reload', domain='i18n_helper')))
        return self.form

    @view_config(request_method="GET")
    def get_view(self):

        request = self.request
        context = self.context
        _ = request.translate

        self.create_form()

        return {"form": self.form, 'locale': self.locale}

    @view_config(request_method="POST")
    def post_view(self):

        request = self.request
        context = self.context
        _ = request.translate
        lang = self.lang
        self.create_form()

        controls = request.POST.items()

        try:
            appstruct = self.form.validate(controls)


        except:
            appstruct = None
            self.request.flash_message.add(message_type='danger', body='i18n_translate_data_not_valid', domain='i18n_helper')

        if appstruct:
            # TODO:
            for entry in self.po:
                entry.msgstr = appstruct['msgid'].get(entry.msgid, '')

            self.po.save(self.po_file_path)
            self.po.save_as_mofile(self.mo_file_path)

            self.request.flash_message.add(message_type='success', body='i18n_translate_success', domain='i18n_helper')

        return self.get_view()

    @view_config(request_param='reload')
    def reload_view(self):

        request = self.request
        context = self.context

        _ = request.translate

        lang = request.matchdict['lang']

        pot = polib.pofile(self.pot_file_path)

        if os.path.exists(self.po_file_path):
            self.po = polib.pofile(self.po_file_path)
            po_entries = {entry.msgid: entry.msgstr for entry in self.po}

        else:
            self.po = polib.POFile()
            po_entries = {}


        for entry in pot:
            if not entry.msgid in po_entries:
                self.po.append(entry)

        self.po.save(self.po_file_path)
        self.po.save_as_mofile(self.mo_file_path)
        self.request.flash_message.add(message_type='success', body='i18n_reload_success', domain='i18n_helper')
        return self.get_view()
