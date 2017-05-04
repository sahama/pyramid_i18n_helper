import os
import polib
import babel
from pyramid.threadlocal import get_current_request
from pyramid.i18n import get_localizer
from pyramid.events import NewRequest, BeforeRender, NewResponse
from pyramid.events import subscriber

@subscriber(NewRequest)
def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)
    helper = request.registry['i18n_helper']

    def auto_translate(string, mapping=None, domain=None):
        tmp = domain if domain else helper.package_name

        if not tmp in helper.pot_msgids:
            helper.pot_msgids[tmp] = set()

        helper.pot_msgids[tmp].add(string)

        return localizer.translate(helper.tsf(string), mapping=mapping, domain=domain)

    request.localizer = localizer
    request.translate = auto_translate
    request.locale = babel.Locale(*babel.parse_locale(request.localizer.locale_name))

@subscriber(BeforeRender)
def add_renderer_globals(event):
    request = event.get('request')
    if request is None:
        request = get_current_request()

    event['_'] = request.translate
    event['localizer'] = request.localizer
    event['locale'] = request.locale

@subscriber(NewResponse)
def before_response(event):
    request = get_current_request()
    helper = request.registry['i18n_helper']

    for domain in helper.pot_msgids:
        s = helper.pot_msgids[domain]
        if s:
            new_pot = polib.pofile(
                os.path.join(helper.package_dir, 'locale', '{0}.pot'.format(domain)),
                check_for_duplicates=True)

            for msgid in [s.pop() for i in range(len(s))]:
                entry = polib.POEntry(msgid=msgid)
                try:
                    new_pot.append(entry)
                except ValueError as e:
                    pass

            new_pot.save()