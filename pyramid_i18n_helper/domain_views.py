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


        # Domain FORM
        pot_dir = os.path.join(self.helper.package_dir, 'locale')
        domains_choices = [(pot.rsplit('.',maxsplit = 1)[0],pot.rsplit('.',maxsplit = 1)[0]) for pot in os.listdir(pot_dir) if pot.endswith('.pot')]

        class SelectDomain(colander.Schema):
            select_domain = colander.SchemaNode(colander.String(),
                                              widget=deform.widget.SelectWidget(values=domains_choices),
                                              title=_("domains"))

        def validator(node, appstruct):
            return True



        schema = SelectDomain(validator=validator)
        schema = schema.bind(request=self.request)
        self.select_domain_form = deform.Form(schema,
                                            use_ajax=False,
                                            action=self.request.route_url('i18n_helper.domain'))
        self.select_domain_form.buttons.append(deform.Button(name='submit', title=_('i18n_select_domain_submit')))

    @view_config(request_method="GET")
    def get_view(self):

        return {'form': self.select_domain_form}

    @view_config(request_method="POST")
    def post_view(self):
        domain = self.request.POST.get('select_domain', '').strip()

        return HTTPFound(location=self.request.route_url('i18n_helper.pot', domain=domain))
