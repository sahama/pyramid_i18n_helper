from pyramid.view import view_config, view_defaults
import colander
import deform
from deform import widget
from pyramid.request import Request
import polib
import os


@view_defaults(route_name='pot', renderer='templates/pot.jinja2', permission='admin')
class PotView():
    def __init__(self, context, request:Request):
        self.request = request
        self.context = context
        _ = request.translate

        self.helper = request.registry['i18n_helper']

        class MessageID(colander.SequenceSchema):
            msgid = colander.SchemaNode(colander.String())


        class MainSchema(colander.Schema):
            msgid = MessageID(title="msgid", widget=widget.SequenceWidget(orderable=True))


        def validator(node, appstruct):
            # TODO:
            return True


        schema = MainSchema(validator=validator)
        schema = schema.bind(request=request)
        self.form = deform.Form(schema, use_ajax=False, action=request.route_url('pot'))
        self.form.buttons.append(deform.Button(name='submit', title=_('i18n_pot_submit')))

        self.pot = polib.pofile(os.path.join(self.helper.package_dir, 'locale', '{0}.pot'.format(self.helper.package_name)))


    @view_config(request_method="GET")
    def get_view(self):
        request = self.request
        context = self.context

        _ = request.translate

        entries = []
        for entry in self.pot:
            entries.append(entry.msgid)

        form_data = {'msgid': entries}

        return {'form': self.form, 'form_data': form_data}


    @view_config(request_method='POST')
    def post_view(self):

        request = self.request
        context = self.context

        _ = request.translate

        controls = request.POST.items()

        try:
            appstruct = self.form.validate(controls)
            print(appstruct)

        except:
            appstruct = None

        if appstruct:
            self.pot = polib.POFile()

            for msgid in set(appstruct['msgid']):
                entry = polib.POEntry(msgid=msgid)
                self.pot.append(entry)

            self.pot.save(os.path.join(self.helper.package_dir, 'locale','{0}.pot'.format(self.helper.package_name)))

        self.pot = polib.pofile(os.path.join(self.helper.package_dir, 'locale', '{0}.pot'.format(self.helper.package_name)))

        return self.get_view()
