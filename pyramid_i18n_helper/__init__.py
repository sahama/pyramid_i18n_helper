import os
from pyramid.decorator import reify

class I18NHelper(object):
    def __init__(self, package):
        self.package = package

    @reify
    def package_dir(self):
        return os.path.abspath(os.path.dirname(self.package.__file__))

    @reify
    def package_name(self):
        return os.path.basename(os.path.dirname(self.package.__file__))


def includeme(config):
    config.registry['i18n_helper'] = I18NHelper(config.root_package)

    config.add_route('po', '/po/{lang}')
    config.add_route('pot', '/pot')
    config.scan('pyramid_i18n_helper')

