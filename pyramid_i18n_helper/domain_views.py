from pyramid.view import view_config, view_defaults
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

    @view_config(request_method="GET")
    def get_view(self):
        return {}
