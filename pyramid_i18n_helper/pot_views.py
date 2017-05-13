from pyramid.view import view_config, view_defaults
import colander
import deform
from deform import widget
from pyramid.request import Request
import polib
import os
from pyramid.httpexceptions import HTTPFound
import babel


@view_defaults(route_name='pot', renderer='pyramid_i18n_helper:templates/pot.jinja2', permission='admin')
class PotView():
    def __init__(self, context, request: Request):
        self.request = request
        self.context = context
        _ = request.translate

        self.helper = request.registry['i18n_helper']

        # MSG FORM
        class MessageID(colander.SequenceSchema):
            msgid = colander.SchemaNode(colander.String())

        class MainSchema(colander.Schema):
            msgid = MessageID(title="msgid", widget=widget.SequenceWidget(orderable=True))

        def validator(node, appstruct):
            # TODO:
            return True

        schema = MainSchema(validator=validator)
        schema = schema.bind(request=request)
        self.msg_form = deform.Form(schema, use_ajax=False, action=request.route_url('pot'))
        self.msg_form.buttons.append(deform.Button(name='submit', title=_('i18n_pot_submit')))

        self.pot = polib.pofile(
            os.path.join(self.helper.package_dir, 'locale', '{0}.pot'.format(self.helper.package_name)))


        # LANG FORM
        langs_dir = os.path.join(self.helper.package_dir, 'locale')
        langs_choices = [lang for lang in os.listdir(langs_dir) if os.path.isdir(os.path.join(langs_dir, lang))]



        class NewLang(colander.Schema):
            new_lang = colander.SchemaNode(colander.String(),
                                           widget=deform.widget.AutocompleteInputWidget(values=langs_choices,
                                                                                        min_length=0),
                                           title="New Lang")

        def validator(node, appstruct):
            return True

        schema = NewLang(validator=validator)
        schema = schema.bind(request=self.request)
        self.lang_form = deform.Form(schema, use_ajax=False, action=self.request.route_url('pot'))
        self.lang_form.buttons.append(deform.Button(name='submit', title='submit'))

    @view_config(request_method="GET")
    def get_view(self):
        request = self.request
        context = self.context

        _ = request.translate

        entries = []
        for entry in self.pot:
            entries.append(entry.msgid)

        msg_form_data = {'msgid': entries}


        return {'msg_form': self.msg_form,
                'msg_form_data': msg_form_data,
                'lang_form': self.lang_form,
                }

    @view_config(request_method='POST', request_param='msgid')
    def msg_view(self):

        request = self.request
        context = self.context

        _ = request.translate

        controls = request.POST.items()

        try:
            appstruct = self.msg_form.validate(controls)

        except:
            appstruct = None

        if appstruct:
            self.pot = polib.POFile()

            for msgid in set(appstruct['msgid']):
                entry = polib.POEntry(msgid=msgid)
                self.pot.append(entry)

            self.pot.save(os.path.join(self.helper.package_dir, 'locale', '{0}.pot'.format(self.helper.package_name)))

        self.pot = polib.pofile(
            os.path.join(self.helper.package_dir, 'locale', '{0}.pot'.format(self.helper.package_name)))

        return self.get_view()

    @view_config(request_method='POST', request_param='new_lang')
    def lang_view(self):


        lang = self.request.POST.get('new_lang', '').strip()

        self.request.locale = babel.Locale(*babel.parse_locale(lang))

        if not os.path.isdir(os.path.join(self.helper.package_dir, 'locale', lang)):
            os.mkdir(os.path.join(self.helper.package_dir, 'locale', lang))
            os.mkdir(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES'))
            self.pot.save(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES', '{0}.po'.format(self.helper.package_name)))
            self.pot.save_as_mofile(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES', '{0}.mo'.format(self.helper.package_name)))
        else:
            pass

        return HTTPFound(location=self.request.route_url('po', lang=lang))