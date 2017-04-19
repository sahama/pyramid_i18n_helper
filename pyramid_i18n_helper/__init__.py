from pyramid.i18n import get_localizer, TranslationStringFactory

from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid.events import BeforeRender

from webob.acceptparse import Accept

from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.threadlocal import get_current_request


import os
def includeme(config):
    import pyramid_i18n_helper

    root_package_directory = os.path.abspath(os.path.dirname(config.root_package.__file__))
    root_package_name = os.path.basename(root_package_directory)
    pyramid_i18n_helper.root_package_directory = root_package_directory
    pyramid_i18n_helper.root_package_name = root_package_name

    config.add_route('po', '/po/{lang}')
    config.add_route('pot', '/pot')
    config.scan('pyramid_i18n_helper')

