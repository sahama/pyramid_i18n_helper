Pyramid I18N Helper
===================

This is a helper for internationalization and localization in `Pyramid <https://trypyramid.com/>`_
this package add two view to your pyramid based application:

 - pot view in route /pot
 - po view in route /po/{lang}

in pot view you can edit pot file
in po view po and mo file for lang will be create
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
