import os
import sys
import inspect

from pyramid.decorator import reify

from pyramid.events import NewRequest, BeforeRender, NewResponse
from pyramid.path import package_path
from pyramid.util import action_method

import polib
import babel
from pyramid.i18n import TranslationStringFactory


class I18NHelper(object):
    def __init__(self, package):
        self.package = package
        self.pot_msgids = {}
        # package = sys.modules[package_name]
        # directory = os.path.join(package_path(package), filename)

    @reify
    def tsf(self):
        return TranslationStringFactory(self.package_name)

    @reify
    def package_dir(self):
        return os.path.abspath(os.path.dirname(self.package.__file__))

    @reify
    def package_name(self):
        return os.path.basename(os.path.dirname(self.package.__file__))


def includeme(config):
    # config.add_directive('i18n_helper_add_translation_dirs', i18n_helper_add_translation_dirs)
    # package = _caller_package(('pyramid', 'pyramid.', 'pyramid_jinja2'))
    helper = I18NHelper(config.root_package)
    config.registry['i18n_helper'] = helper

    config.add_route('po', '/po/{lang}')
    config.add_route('pot', '/pot')

    config.scan('pyramid_i18n_helper')

