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
        # self.default_permission = 'i18n_helper'
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

def set_default_permission(config, default_permission):
    helper = config.registry['i18n_helper']
    helper.default_permission = default_permission


def includeme(config):
    # config.add_directive('i18n_helper_add_translation_dirs', i18n_helper_add_translation_dirs)
    # package = _caller_package(('pyramid', 'pyramid.', 'pyramid_jinja2'))
    helper = I18NHelper(config.root_package)
    config.registry['i18n_helper'] = helper

    # config.add_directive('set_i18n_helper_default_permission', set_default_permission)

    config.add_route('i18n_helper.domain', '/translate')
    config.add_route('i18n_helper.pot', '/translate/{domain}')
    config.add_route('i18n_helper.po', '/translate/{domain}/{lang}')

    config.scan('pyramid_i18n_helper')

