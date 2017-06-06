from pyramid.view import view_config, view_defaults
import colander
import deform
from deform import widget
from pyramid.request import Request
import polib
import os
from pyramid.httpexceptions import HTTPFound
import babel
import locale


@view_defaults(route_name='pot', renderer='pyramid_i18n_helper:templates/pot.jinja2', permission='i18n_helper')
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
        created_langs_choices = []
        for lang in os.listdir(langs_dir):
            if os.path.isdir(os.path.join(langs_dir, lang)):
                lang_locale = babel.Locale(*babel.parse_locale(lang))
                created_langs_choices.append(
                    (lang , '{en_name}/{display_name}'.format(
                        en_name=lang_locale.english_name,
                        display_name=lang_locale.display_name )
                    )
                )

        available_langs_choices = sorted(locale.locale_alias)


        class NewLang(colander.Schema):
            new_lang = colander.SchemaNode(colander.String(),
                                           widget=deform.widget.AutocompleteInputWidget(values=available_langs_choices,
                                                                                        min_length=0),
                                           title="New Lang")

        class SelectLang(colander.Schema):
            select_lang = colander.SchemaNode(colander.String(),
                                           widget=deform.widget.SelectWidget(values=created_langs_choices),
                                           title="Select Lang")


        def validator(node, appstruct):
            return True

        schema = NewLang(validator=validator)
        schema = schema.bind(request=self.request)
        self.new_lang_form = deform.Form(schema, use_ajax=False, action=self.request.route_url('pot'))
        self.new_lang_form.buttons.append(deform.Button(name='submit', title='submit'))

        schema = SelectLang(validator=validator)
        schema = schema.bind(request=self.request)
        self.select_lang_form = deform.Form(schema, use_ajax=False, action=self.request.route_url('pot'))
        self.select_lang_form.buttons.append(deform.Button(name='submit', title='submit'))

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
                'new_lang_form': self.new_lang_form,
                'select_lang_form': self.select_lang_form,
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
            self.request.flash_message.add(message_type='danger', body='not_valid_data')

        if appstruct:
            self.pot = polib.POFile()

            for msgid in set(appstruct['msgid']):
                entry = polib.POEntry(msgid=msgid)
                self.pot.append(entry)

            self.pot.save(os.path.join(self.helper.package_dir, 'locale', '{0}.pot'.format(self.helper.package_name)))
            self.request.flash_message.add(message_type='success', body='success')

        self.pot = polib.pofile(
            os.path.join(self.helper.package_dir, 'locale', '{0}.pot'.format(self.helper.package_name)))

        return self.get_view()


    @view_config(request_method='POST', request_param='new_lang')
    def lang_view(self):


        lang = self.request.POST.get('new_lang', '').strip()
        try:
            self.request.locale = babel.Locale(*babel.parse_locale(lang))

            if not os.path.isdir(os.path.join(self.helper.package_dir, 'locale', lang)):
                os.mkdir(os.path.join(self.helper.package_dir, 'locale', lang))
                os.mkdir(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES'))
                self.pot.save(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES',
                                           '{0}.po'.format(self.helper.package_name)))
                self.pot.save_as_mofile(os.path.join(self.helper.package_dir, 'locale', lang, 'LC_MESSAGES',
                                                     '{0}.mo'.format(self.helper.package_name)))
                self.request.flash_message.add(message_type='success', body='success')

                return HTTPFound(location=self.request.route_url('po', lang=lang))

            else:
                self.request.flash_message.add(message_type='danger', body='can_not_create_lang')

        except:
            self.request.flash_message.add(message_type='danger', body='not_valid_lang')


        return self.get_view()


    @view_config(request_method='POST', request_param='select_lang')
    def select_lang_view(self):


        lang = self.request.POST.get('select_lang', '').strip()

        self.request.locale = babel.Locale(*babel.parse_locale(lang))


        return HTTPFound(location=self.request.route_url('po', lang=lang))