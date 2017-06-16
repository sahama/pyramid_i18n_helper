Pyramid I18N Helper
===================

This is a helper for internationalization and localization in `Pyramid <https://trypyramid.com/>`_
this package add two view to your pyramid based application:

 - pot view in route /pot
 - po view in route /po/{lang}

and add `Babel <http://babel.pocoo.org/en/latest/>`_ locale object to request.

in pot view you can edit pot file
in po view po and mo file for lang will be create. also you can update po file from pot file.

keep in mind this package depend on pyramid_layout default layout
also at now this package use templates based on jinja2

Installation
------------

.. code-block:: bash

    pip install pyramid_i18n_helper

add then add this package to your application

.. code-block:: ini

    pyramid.includes =
        pyramid_layout
        pyramid_jinja2
        pyramid_i18n_helper


or

.. code-block:: python

    config.include('pyramid_layout')
    config.include('pyramid_jinja2')
    config.include('pyramid_i18n_helper')


Support
-------

You can use `project issue page <https://github.com/sahama/pyramid_i18n_helper/issues/>`_ to submit your issue

Khown Issues
------------

 - After translating a msgid you have to restart your application
 - At now this package use pyramid_layout default layout. form `pyramid_layout documentation page <http://docs.pylonsproject.org/projects/pyramid_layout/en/latest/layouts.html>`_ `main_template is the template object that provides the main template (aka, o-wrap) for the view`. so if your application dont have main_layout. you may have problem.
 - main_layout template have to designed via jinja2


Changes
=======


v 0.2.13
--------

 - handle duplication error
 - create new domain if not exist

v 0.2.11
--------

 - compatible with pyramid_flash_message 0.2

v 0.2.9
-------

 - add flash message.

v 0.2.8
-------

 - set permission to 'i18n_helper'. so user want to access pages have to have this permission.

v 0.2.7
-------

 - modify create lang and select lang
 - error in creating new lang if lang not valid in babel

v 0.2.6
-------

 - add ability to collect msgids in pot file via `i18n_helper.collect_msgid` setting as `true`
 - some debug

v 0.2.5
-------

 - add babel locale object to request

v 0.2.4
-------

 - some bug fix

v 0.2.3
-------

 - some bug fix

v 0.2
-----

 - add (newlang / go to lang) field
 - some bug fix

v 0.1
-----

 - some modification
 - apply suggestion from #1. thank @mmerickel

v 0.0
-----

 - init project and create skeleton of it