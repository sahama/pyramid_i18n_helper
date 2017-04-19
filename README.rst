This is a helper for internationalization and localization in pyramid
this package add two view to your pyramid based application:
pot view in route /pot
po view in route /po/{lang}
in pot view you can edit pot file
in po view po and mo file for lang will be create
remember this package depend on pyramid_layout default layout
also keep in mind at now this package use templates based on jinja2

installation
------------

pip install pyramid_i18_helper

add then add this package to your application

pyramid.includes =
    pyramid_i18_helper

or in init
    config.include('pyramid_i18_helper')
