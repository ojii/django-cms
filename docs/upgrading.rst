#########
Upgrading
#########

Notes on how to upgrade to version |release|

***************
From 2.1.0 RC 1
***************

* No special action is required to upgrade from RC1 to RC2

***************
From 2.1.0 Beta
***************

* Make sure ``'menus'`` is in ``INSTALLED_APPS``. This was already required in
  2.1.0 Beta, however the Beta also worked without it.
* Make sure you ``migrate`` and/or ``snycdb`` your database.
* New dependency: django-classy-tags. The dependency should be resolved
  automatically during installation.

.. note:: In case you have issues with the googlemap migrations. Unfortunately
          due to an issue in older CMS releases, the migrations for the
          googlemap plugin were missnamed.
          The affected migrations are 0003, 0004 and 0005. If they exist in your
          south_migrationhistory table, rename them so the dashes (``-``) turn
          into underscores (``_``).

********
From 2.0
********

* A number of templatetags are now in the ``menu_tags`` template library:
** ``show_menu``
** ``show_menu_below_id``
** ``show_sub_menu``
** ``show_breadcrumb``
** ``language_chooser``
** ``page_language_url``