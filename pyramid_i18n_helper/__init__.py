import os
import inspect

from pyramid.decorator import reify
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.events import NewRequest
from pyramid.path import package_path
from pyramid.util import action_method
import sys

class _PackageFinder(object):
    inspect = staticmethod(inspect)

    def caller_package(self, excludes=()):
        """A list of excluded patterns, optionally containing a `.` suffix.
        For example, ``'pyramid.'`` would exclude exclude ``'pyramid.config'``
        but n_PackageFinderot ``'pyramid'``.
        """
        f = None
        for t in self.inspect.stack():
            f = t[0]
            name = f.f_globals.get('__name__')
            if name:
                excluded = False
                for pattern in excludes:
                    if pattern[-1] == '.' and name.startswith(pattern):
                        excluded = True
                        break
                    elif name == pattern:
                        excluded = True
                        break
                if not excluded:
                    break

        if f is None:
            return None

        pname = f.f_globals.get('__name__') or '__main__'
        m = sys.modules[pname]
        f = getattr(m, '__file__', '')
        if (('__init__.py' in f) or ('__init__$py' in f)):  # empty at >>>
            return m

        pname = m.__name__.rsplit('.', 1)[0]

        return sys.modules[pname]


_caller_package = _PackageFinder().caller_package

class I18NHelper(object):
    def __init__(self, package):
        self.package = package
        # package = sys.modules[package_name]
        # directory = os.path.join(package_path(package), filename)

    @reify
    def package_dir(self):
        return os.path.abspath(os.path.dirname(self.package.__file__))

    @reify
    def package_name(self):
        return os.path.basename(os.path.dirname(self.package.__file__))

    # @reify
    # def tsf(self):
    #     return TranslationStringFactory(self.package_name)

# def i18n_helper_add_translation_dirs(config, *specs):
#     config.add_translation_dirs(*specs)

def includeme(config):
    # config.add_directive('i18n_helper_add_translation_dirs', i18n_helper_add_translation_dirs)
    # package = _caller_package(('pyramid', 'pyramid.', 'pyramid_jinja2'))
    helper = I18NHelper(config.root_package)
    config.registry['i18n_helper'] = helper

    config.add_route('po', '/po/{lang}')
    config.add_route('pot', '/pot')

    tsf = TranslationStringFactory(helper.package_name)
    def add_localizer(event):
        request = event.request
        localizer = get_localizer(request)

        def auto_translate(string, mapping=None, domain=None):
            # print(string, mapping, domain)
            return localizer.translate(tsf(string), mapping=mapping, domain=domain)

        request.localizer = localizer
        request.translate = auto_translate

    config.add_subscriber(add_localizer, NewRequest)
    config.scan('pyramid_i18n_helper')


