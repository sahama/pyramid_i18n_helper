from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
import colander
import deform
from deform import widget
from pyramid.request import Request
import polib
import os
import babel


@view_defaults(route_name='i18n_helper.domain', renderer='pyramid_i18n_helper:templates/domain.jinja2', permission='i18n_helper')
class PoView():
    def __init__(self, context, request: Request):
        self.request = request
        self.context = context
        _ = request.translate

        self.helper = request.registry['i18n_helper']


        # Select Domain FORM
        self.pot_dir = os.path.join(self.helper.package_dir, 'locale')
        domains_choices = [(pot.rsplit('.',maxsplit = 1)[0],pot.rsplit('.',maxsplit = 1)[0]) for pot in os.listdir(self.pot_dir) if pot.endswith('.pot')]

        class SelectDomain(colander.Schema):
            select_domain = colander.SchemaNode(colander.String(),
                                                widget=deform.widget.SelectWidget(values=domains_choices),
                                                title=_("i18n_select_domain", domain='i18n_helper'))

        class NewDomain(colander.Schema):
            new_domain = colander.SchemaNode(colander.String(),
                                             title=_("i18n_new_domain", domain='i18n_helper'))

        def validator(node, appstruct):
            return True

        schema = NewDomain(validator=validator)
        schema = schema.bind(request=self.request)
        self.new_domain_form = deform.Form(schema,
                                           use_ajax=False,
                                           action=self.request.route_url('i18n_helper.domain'))
        self.new_domain_form.buttons.append(deform.Button(name='submit',
                                                          title=_('i18n_new_domain_submit',
                                                                  domain='i18n_helper')))

        schema = SelectDomain(validator=validator)
        schema = schema.bind(request=self.request)
        self.select_domain_form = deform.Form(schema,
                                              use_ajax=False,
                                              action=self.request.route_url('i18n_helper.domain'))
        self.select_domain_form.buttons.append(deform.Button(name='submit',
                                                             title=_('i18n_select_domain_submit',
                                                                     domain='i18n_helper')))

    @view_config(request_method="GET")
    def get_view(self):

        return {
            'select_domain_form': self.select_domain_form,
            'new_domain_form': self.new_domain_form,
                }

    @view_config(request_method="POST", request_param='select_domain')
    def select_domain_view(self):
        domain = self.request.POST.get('select_domain', '').strip()

        return HTTPFound(location=self.request.route_url('i18n_helper.pot', domain=domain))

    @view_config(request_method="POST", request_param='new_domain')
    def new_domain_view(self):
        try:
            domain = self.request.POST.get('new_domain', '').strip()
            assert domain
            pot = polib.POFile()
            pot.save(os.path.join(self.pot_dir, '{0}.pot'.format(domain)))
            self.request.flash_message.add(message_type='success', body='i18n_new_domain_creation_success',
                                           domain='i18n_helper')

            return HTTPFound(location=self.request.route_url('i18n_helper.pot', domain=domain))
        except:
            self.request.flash_message.add(message_type='danger', body='i18n_new_domain_creation_error',
                                           domain='i18n_helper')
            return self.get_view()

