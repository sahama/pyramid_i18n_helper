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
import logging
log = logging.getLogger(__name__)

@view_defaults(route_name='pot', renderer='pyramid_i18n_helper:templates/pot.jinja2', permission='i18n_helper')
class PotView():
    def __init__(self, context, request: Request):
        self.request = request
        self.context = context
        _ = request.translate

        self.helper = request.registry['i18n_helper']
        self.pot_dir = os.path.join(self.helper.package_dir, 'locale')
        self.pot_list = [polib.pofile(os.path.join(self.pot_dir, pot)) for pot in os.listdir(self.pot_dir) if pot.endswith('.pot')]
        # print(dir(self.pot_list[0].path))
        # self.pot = polib.pofile(
        #     os.path.join(self.helper.package_dir, 'locale', '{0}.pot'.format(self.helper.package_name)))


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
                                           title=_("i18n_new_lang"))

        class SelectLang(colander.Schema):
            select_lang = colander.SchemaNode(colander.String(),
                                           widget=deform.widget.SelectWidget(values=created_langs_choices),
                                           title=_("i18n_select_lang"))

        def validator(node, appstruct):
            return True

        schema = NewLang(validator=validator)
        schema = schema.bind(request=self.request)
        self.new_lang_form = deform.Form(schema, use_ajax=False, action=self.request.route_url('pot'))
        self.new_lang_form.buttons.append(deform.Button(name='submit', title=_('i18n_new_lang_submit')))

        schema = SelectLang(validator=validator)
        schema = schema.bind(request=self.request)
        self.select_lang_form = deform.Form(schema, use_ajax=False, action=self.request.route_url('pot'))
        self.select_lang_form.buttons.append(deform.Button(name='submit', title=_('i18n_select_lang_submit')))

        # MSG FORM
    def msg_form_creator(self):
        request = self.request
        _ = request.translate

        class MsgID(colander.Schema):
            msgid = colander.SchemaNode(colander.String())

        class MessageID(colander.SequenceSchema):
            msgid = colander.SchemaNode(colander.String())

        class MsgIDW(colander.Schema):
            domain = colander.SchemaNode(colander.String())
            msgid = MessageID()

        class MessageSchema(colander.SequenceSchema):

            msgid = MsgIDW(title="msgid")

        class DomainSchema(colander.Schema):
            domain = MessageSchema(title="domain")

        def validator(node, appstruct):
            # TODO: some validation
            return True

        schema = DomainSchema(validator=validator)
        schema = schema.bind(request=self.request)
        self.msg_form = deform.Form(schema, use_ajax=False, action=self.request.route_url('pot'))
        self.msg_form.buttons.append(deform.Button(name='submit', title=_('i18n_pot_submit')))
        return self.msg_form

    @view_config(request_method="GET")
    def get_view(self):
        request = self.request
        context = self.context
        self.msg_form = self.msg_form_creator()
        _ = request.translate

        entries = []
        for domain in self.pot_list:
            domain_entries = []
            for entry in domain:
                domain_entries.append(entry.msgid)
            entries.append({'msgid':domain_entries, 'domain': os.path.split(domain.fpath)[1]})

        print(entries)
        # appstruct is: {'domain': [{'msgid': ['m1', 'm2'], 'domain': 'd1'}, {'msgid': ['m1', 'm2'], 'domain': 'd2'}]}

        msg_form_data = {'domain': entries}
        # msg_form_data = {}

        print(msg_form_data)


        return_dict = {'msg_form': self.msg_form,
                'msg_form_data': msg_form_data,
                'new_lang_form': self.new_lang_form,
                'select_lang_form': self.select_lang_form,
                }

        print(return_dict)
        return return_dict

    @view_config(request_method='POST', request_param='msgid')
    def msg_view(self):

        request = self.request
        context = self.context

        _ = request.translate

        controls = request.POST.items()
        self.msg_form = self.msg_form_creator()
        appstruct = self.msg_form.validate(controls)
        print('appstruct is:', appstruct)

        try:
            appstruct = self.msg_form.validate(controls)
            print('appstruct is:', appstruct)

            self.pot = polib.POFile()

            for msgid in set(appstruct['msgid']):
                entry = polib.POEntry(msgid=msgid)
                self.pot.append(entry)

            self.pot.save(os.path.join(self.helper.package_dir, 'locale', '{0}.pot'.format(self.helper.package_name)))
            self.request.flash_message.add(message_type='success', body='i18n_pot_msg_data_process_success')

        except:
            self.request.flash_message.add(message_type='danger', body='i18n_pot_msg_data_not_valid')

        self.pot = polib.pofile(
            os.path.join(self.helper.package_dir, 'locale', '{0}.pot'.format(self.helper.package_name)))

        return self.get_view()


    @view_config(request_method='POST', request_param='new_lang')
    def new_lang_view(self):

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

                self.request.flash_message.add(message_type='success', body='i18n_new_lang_creation_success')

                return HTTPFound(location=self.request.route_url('po', lang=lang))

            else:
                self.request.flash_message.add(message_type='danger', body='i18n_new_lang_lang_exist')

        except:
            self.request.flash_message.add(message_type='danger', body='i18n_new_lang_creation_error')

        return self.get_view()


    @view_config(request_method='POST', request_param='select_lang')
    def select_lang_view(self):


        lang = self.request.POST.get('select_lang', '').strip()

        self.request.locale = babel.Locale(*babel.parse_locale(lang))


        return HTTPFound(location=self.request.route_url('po', lang=lang))