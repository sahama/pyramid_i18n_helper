Pyramid I18N Helper
===========

This is a helper for internationalization and localization in `Pyramid <https://trypyramid.com/>`_
this package add two view to your pyramid based application:

 - pot view in route /pot
 - po view in route /po/{lang}

in pot view you can edit pot file
in po view po and mo file for lang will be create
remember this package depend on pyramid_layout default layout
also keep in mind at now this package use templates based on jinja2

Installation
------------

.. code-block:: bash

    pip install pyramid_i18_helper

add then add this package to your application

.. code-block:: ini

    pyramid.includes =
        pyramid_jinja2
        pyramid_i18_helper


.. code-block:: python

    config.include('pyramid_jinja2')
    config.include('pyramid_i18_helper')


Support
-------

You can use `project issue page <https://github.com/sahama/pyramid_i18n_helper/issues/>`_ to submit your issue