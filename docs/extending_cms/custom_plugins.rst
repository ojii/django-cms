##############
Custom Plugins
##############

CMS Plugins are used to give content managers the ability to add content to
pages, in most cases, the builtin and 3rd party plugins are not enough, in
which case you have to write your own custom CMS Plugin.

Don't worry though, since writing a CMS Plugin is rather simple.


********
Overview
********

* A subclass of :class:`cms.plugin_base.CMSPluginBase`, usually placed in
  ``cms_plugins.py`` defines your plugin.
* A template to render the plugin.
* *Optionally* use a subclass of :class:`cms.models.pluginmodel.CMSPlugin` to
  store the configuration for your plugin instances.


*******************
The simplest plugin
*******************

You may use ``python manage.py startapp`` to set up the basic layout for you
plugin app, alternatively, just add a file called ``cms_plugins.py`` to an
existing Django application.

In there, you place your plugins, in our example the following code::

    from cms.plugin_base import CMSPluginBase
    from cms.plugin_pool import plugin_pool
    from cms.models.pluginmodel import CMSPlugin
    from django.utils.translation import ugettext_lazy as _

    class HelloPlugin(CMSPluginBase):
        model = CMSPlugin
        name = _("Hello Plugin")
        render_template = "hello_plugin.html"

        def render(self, context, instance, placeholder):
            return context

    plugin_pool.register_plugin(HelloPlugin)

Now we're almost done, all that's left is adding the template. Add the
following into the root template directory in a file called
``hello_plugin.html``:

.. code-block:: html+django

    <h1>Hello {% if request.user.is_authenticated %}{{ request.user.first_name }} {{ request.user.last_name}}{% else %}Guest{% endif %}</h1>

This plugin will now greet the users on your website either by their name if
they're logged in, or as Guest if they're not.

Now let's take a closer look at what we did there. The ``cms_plugins.py`` files
are where you should define your subclasses of
:class:`cms.plugin_base.CMSPluginBase`, these classes define the different
plugins.

There are three required attributes on those classes:

* ``model``: The model you wish to use to store information about this plugin,
  if you do not require any special information, for example configuration, to
  be stored for your plugins, you may just use
  :class:`cms.models.pluginmodel.CMSPlugin`. We'll look at that model more
  closely in a bit.
* ``name``: The name of your plugin as displayed in the admin. It is generally
  good practice to mark this string as translatable using
  :func:`django.utils.translation.ugettext_lazy`, however this is optional.
* ``render_template``: The template to render this plugin with.

In addition to those three attributes, you must also define a 
:meth:`render` method on your subclasses. That method gets three arguments:

* ``context``: The context with which the page is rendered.
* ``instance``: The instance of your plugin that is rendered.
* ``placeholder``: The name of the placeholder that is rendered. 

This method must return a dictionary or an instance of
:class:`django.template.Context`, which will be used as context to render the
plugin template.



*********************
Storing configuration
*********************

In many cases, you want to store configuration for your plugin instances, for
example if you have a plugin that shows the latest blog posts, you might want
to be able to choose the amount of entries shown. Another example would be a
gallery plugin, where you want to choose the pictures to show for the plugin.

To do so, you create a Django model by subclassing
:class:`cms.models.pluginmodel.CMSPlugin` in the ``models.py`` of an installed
application.

Let's improve our ``HelloPlugin`` from above by making it configurable what the
fallback name for non authenticated users should be.

In our ``models.py`` we add following model::

    from cms.models.pluginmodel import CMSPlugin
    
    from django.db import models

    class Hello(CMSPlugin):
        guest_name = models.CharField(max_length=50, default='Guest')


If you followed the Django tutorial, this shouldn't look too new to you. The 
only difference to normal models is that you subclass
:class:`cms.models.pluginmodel.CMSPlugin` rather than
:class:`django.db.models.base.Model`.

Now we need to change our plugin definition to use this model, so our new
``cms_plugins.py`` looks like this::

    from cms.plugin_base import CMSPluginBase
    from cms.plugin_pool import plugin_pool
    from django.utils.translation import ugettext_lazy as _
    
    from models import Hello

    class HelloPlugin(CMSPluginBase):
        model = Hello
        name = _("Hello Plugin")
        render_template = "hello_plugin.html"

        def render(self, context, instance, placeholder):
            context['instance'] = instance
            return context

    plugin_pool.register_plugin(HelloPlugin)

We changed the ``model`` attribute to point to our newly created ``Hello``
model and pass the model instance to the context.

As a last step, we have to update our template to make use of this
new configuration:

.. code-block:: html+django

    <h1>Hello {% if request.user.is_authenticated %}{{ request.user.first_name }} {{ request.user.last_name}}{% else %}{{ instance.guest_name }}{% endif %}</h1>

The only thing we changed there is that we use the template variable
``{{ instance.guest_name }}`` instead of the hardcoded ``Guest`` string in the
else clause.

.. warning::

    :class:`cms.models.pluginmodel.CMSPlugin` subclasses cannot be further
    subclassed at the moment. In order to make your plugin models reusable,
    please use abstract base models.

.. warning::
    
    You cannot name your model fields the same as any installed plugins
    lower-cased model name, due to the implicit one to one relation Django uses
    for subclassed models. If you use all core plugins, this includes:
    ``file``, ``flash``, ``googlemap``, ``link``, ``picture``, ``snippetptr``,
    ``teaser``, ``twittersearch``, ``twitterrecententries`` and ``video``.
    

*********
OLD PARTS
*********


Plugin Model
============

First create a model that links to the gallery via a
:class:`~django.db.models.ForeignKey` field::

    from cms.models import CMSPlugin

    class GalleryPlugin(CMSPlugin):
        gallery = models.ForeignKey(Gallery)

Be sure that your model inherits the :class:`cms.models.pluginmodel.CMSPlugin`
class. The plugin model can have any number of fields you want. They are the
fields that get displayed if you edit the plugin.

.. warning::

    :class:`CMSPlugin` subclasses cannot be further subclassed, if you want to make
    a reusable plugin model, make an abstract base model which does not extend
    :class:`CMSPlugin` and subclass this abstract model as well as
    :class:`CMSPlugin` in your real plugin model.
    Further note that you cannot name your model fields the same as any plugin's
    lowercased model name you use is called, due to the implicit one to one
    relation Django uses for subclassed models. This includes but is not limited
    to ``text`` if you have the text CMS plugin enabled.

Now models.py looks like the following::

    from django.db import models
    from cms.models import CMSPlugin

    class Gallery(models.Model):
        parent = models.ForeignKey('self', blank=True, null=True)
        name = models.CharField(max_length=30)

        def __unicode__(self):
            return self.name

        def get_absolute_url(self):
            return reverse('gallery_view', args=[self.pk])

        class Meta:
            verbose_name_plural = 'gallery'


    class Picture(models.Model):
        gallery = models.ForeignKey(Gallery)
        image = models.ImageField(upload_to="uploads/images/")
        description = models.CharField(max_length=60)


    class GalleryPlugin(CMSPlugin):
        gallery = models.ForeignKey(Gallery)



Handling Relations
------------------

If your custom plugin has foreign key or many-to-many relations you are
responsible for copying those if necessary whenever the CMS copies the plugin.

To do this you can implement a method called
:meth:`cms.models.pluginmodel.CMSPlugin.copy_relations` on your plugin
model which gets the **old** instance of the plugin as argument.

Lets assume this is your plugin::

    class ArticlePluginModel(CMSPlugin):
        title = models.CharField(max_length=50)
        sections =  models.ManyToManyField(Section)

        def __unicode__(self):
            return self.title

Now when the plugin gets copied, you want to make sure the sections stay::

        def copy_relations(self, oldinstance):
            self.sections = oldinstance.sections.all()

Your full model now::

    class ArticlePluginModel(CMSPlugin):
        title = models.CharField(max_length=50)
        sections =  models.ManyToManyField(Section)

        def __unicode__(self):
            return self.title

        def copy_relations(self, oldinstance):
            self.sections = oldinstance.sections.all()


cms_plugins.py
==============

After that create in the application folder (the same one where ``models.py``
is) a file called ``cms_plugins.py``.

In there write the following::

    from cms.plugin_base import CMSPluginBase
    from cms.plugin_pool import plugin_pool
    from models import GalleryPlugin
    from django.utils.translation import ugettext as _

    class CMSGalleryPlugin(CMSPluginBase):
        model = GalleryPlugin
        name = _("Gallery")
        render_template = "gallery/gallery.html"

        def render(self, context, instance, placeholder):
            context.update({
                'gallery':instance.gallery,
                'object':instance,
                'placeholder':placeholder
            })
            return context

    plugin_pool.register_plugin(CMSGalleryPlugin)


:class:`cms.plugin_base.CMSPluginBase` itself inherits from
:class:`django.contrib.admin.ModelAdmin` so you can use all the things
(inlines for example) you would use in a regular admin class. For more 
information see the `Django admin documentation`_.


For a list of all the options you have on :class:`CMSPluginBase` have a look at
the plugin reference

.. note::

    If at some point you want to remove this plugin after deleting the cms_plugins.py
    there is a cms management command called uninstall plugins
    that removes all instances of the specified plugin(s) by name.
    eg. ``manage.py cmsmanage uninstall plugins CMSGalleryPlugin``.
    To find all names for uninstallable plugins there is a command for this aswell
    ``manage.py cmsmanage list plugins``.
    
Template
========

Now create a ``gallery.html`` template in ``templates/gallery/`` and write the
following in there:

.. code-block:: html+django

    {% for image in gallery.picture_set.all %}
        <img src="{{ image.image.url }}" alt="{{ image.description }}" />
    {% endfor %}

Add a file ``admin.py`` in your plugin root-folder and insert the following::

    from django.contrib import admin
    from cms.admin.placeholderadmin import PlaceholderAdmin
    from models import Gallery,Picture

    class PictureInline(admin.StackedInline):
        model = Picture

    class GalleryAdmin(admin.ModelAdmin):
        inlines = [PictureInline]

    admin.site.register(Gallery, GalleryAdmin)


Now go into the admin create a gallery and afterwards go into a page and add a
gallery plugin and some pictures should appear in your page.

Limiting Plugins per Placeholder
================================

You can limit in which placeholder certain plugins can appear. Add a
:setting:`CMS_PLACEHOLDER_CONF` to your ``settings.py``.

Example::

    CMS_PLACEHOLDER_CONF = {
        'col_sidebar': {
            'plugins': ('FilePlugin', 'FlashPlugin', 'LinkPlugin', 'PicturePlugin', 'TextPlugin', 'SnippetPlugin'),
            'name': gettext("sidebar column")
        },

        'col_left': {
            'plugins': ('FilePlugin', 'FlashPlugin', 'LinkPlugin', 'PicturePlugin', 'TextPlugin', 'SnippetPlugin','GoogleMapPlugin','CMSTextWithTitlePlugin','CMSGalleryPlugin'),
            'name': gettext("left column")
        },

        'col_right': {
            'plugins': ('FilePlugin', 'FlashPlugin', 'LinkPlugin', 'PicturePlugin', 'TextPlugin', 'SnippetPlugin','GoogleMapPlugin',),
            'name': gettext("right column")
        },
    }

"**col_left**" and "**col_right**" are the names of two placeholders. The
plugins list are filled with plugin class names you find in the
``cms_plugins.py``. You can add extra context to each placeholder so
plugin-templates can react to them.

You can change the displayed name in the admin with the **name** parameter. In
combination with gettext you can translate this names according to the language
of the user. Additionally you can limit the number of plugins (either total or
by type) for each placeholder with the **limits** parameter (see
:ref:`configuration` for details).


Advanced
========

:class:`CMSGalleryPlugin` can be even further customized:

Because :class:`CMSPluginBase <cms.plugin_base.CMSPluginBase>` extends
:class:`ModelAdmin <django.contrib.admin.ModelAdmin>` you can use
all the things you are used to with normal admin classes. You can define
inlines, the form, the form template etc.

.. note::

    If you want to overwrite the form be sure to extend from
    ``admin/cms/page/plugin_change_form.html`` to have an unified look across the
    plugins and to have the preview functionality automatically installed.

.. _custom-plugins-handling-media:

Handling media
==============

If your plugin depends on certain media files, javascript or stylesheets, you
can include them from your plugin template using `django-sekizai`_. Your CMS
templates are always enforced to have the ``css`` and ``js`` sekizai namespaces,
therefore those should be used to include the respective files. For more 
information about django-sekizai, please refer to the
`django-sekizai documentation`_.

Sekizai style
-------------

To fully harness the power of django-sekizai, it is helpful to have a consistent
style on how to use it. Here is a set of conventions that should, but don't
necessarily need to,  be followed:

* One bit per ``addtoblock``. Always include one external CSS or JS file per
  ``addtoblock`` or one snippet per ``addtoblock``. This is needed so
  django-sekizai properly detects duplicate files.
* External files should be on one line, with no spaces or newlines between the
  ``addtoblock`` tag and the HTML tags.
* When using embedded javascript or CSS, the HTML tags should be on a newline.

A **good** example:

.. code-block:: html+django

    {% load sekizai_tags %}
    
    {% addtoblock "js" %}<script type="text/javascript" src="{{ MEDIA_URL }}myplugin/js/myjsfile.js"></script>{% endaddtoblock %}
    {% addtoblock "js" %}<script type="text/javascript" src="{{ MEDIA_URL }}myplugin/js/myotherfile.js"></script>{% endaddtoblock %}
    {% addtoblock "css" %}<link rel="stylesheet" type="text/css" href="{{ MEDIA_URL }}myplugin/css/astylesheet.css"></script>{% endaddtoblock %}
    {% addtoblock "js" %}
    <script type="text/javascript">
        $(document).ready(function(){
            doSomething();
        });
    </script>
    {% endaddtoblock %}

A **bad** example:

.. code-block:: html+django

    {% load sekizai_tags %}
    
    {% addtoblock "js" %}<script type="text/javascript" src="{{ MEDIA_URL }}myplugin/js/myjsfile.js"></script>
    <script type="text/javascript" src="{{ MEDIA_URL }}myplugin/js/myotherfile.js"></script>{% endaddtoblock %}
    {% addtoblock "css" %}
        <link rel="stylesheet" type="text/css" href="{{ MEDIA_URL }}myplugin/css/astylesheet.css"></script>
    {% endaddtoblock %}
    {% addtoblock "js" %}<script type="text/javascript">
        $(document).ready(function(){
            doSomething();
        });
    </script>{% endaddtoblock %}


*************************
Plugin Context Processors
*************************

Plugin context processors are callables that modify all plugin's context before
rendering. They are enabled using the :setting:`CMS_PLUGIN_CONTEXT_PROCESSORS`
setting.

A plugin context processor takes 2 arguments:

**instance**:

The instance of the plugin model

**placeholder**:

The instance of the placeholder this plugin appears in.

The return value should be a dictionary containing any variables to be added to
the context.

Example::

    # settings.py:
    CMS_PLUGIN_CONTEXT_PROCESSORS = (
        'yourapp.cms_plugin_context_processors.add_verbose_name',
    )

    # yourapp.cms_plugin_context_processors.py:
    def add_verbose_name(instance, placeholder):
        '''
        This plugin context processor adds the plugin model's verbose_name to context.
        '''
        return {'verbose_name': instance._meta.verbose_name}


*****************
Plugin Processors
*****************

Plugin processors are callables that modify all plugin's output after rendering.
They are enabled using the :setting:`CMS_PLUGIN_PROCESSORS` setting.

A plugin processor takes 4 arguments:

**instance**:

The instance of the plugin model

**placeholder**:

The instance of the placeholder this plugin appears in.

**rendered_content**:

A string containing the rendered content of the plugin.

**original_context**:

The original context for the template used to render the plugin.

Note that plugin processors are also applied to plugins embedded in Text.
Depending on what your processor does, this might break the output. For example,
if your processor wraps the output in a ``div`` tag, you might end up having
``div`` tags inside of ``p`` tags, which is invalid. You can prevent such cases
by returning ``rendered_content`` unchanged if
``instance._render_meta.text_enabled`` is ``True``, which is the case when
rendering an embedded plugin.

Example
=======

Suppose you want to put wrap each plugin in the main placeholder in a colored
box, but it would be too complicated to edit each individual plugin's template:

In your ``settings.py``::

    CMS_PLUGIN_PROCESSORS = (
        'yourapp.cms_plugin_processors.wrap_in_colored_box',
    )

In your ``yourapp.cms_plugin_processors.py``::

    def wrap_in_colored_box(instance, placeholder, rendered_content, original_context):
        '''
        This plugin processor wraps each plugin's output in a colored box if it is in the "main" placeholder.
        '''
        # Plugins not in the main placeholder should remain unchanged
        # Plugins embedded in Text should remain unchanged in order not to break output
        if placeholder.slot != 'main' or (instance._render_meta.text_enabled and instance.parent):
            return rendered_content
        else:
            from django.template import Context, Template
            # For simplicity's sake, construct the template from a string:
            t = Template('<div style="border: 10px {{ border_color }} solid; background: {{ background_color }};">{{ content|safe }}</div>')
            # Prepare that template's context:
            c = Context({
                'content': rendered_content,
                # Some plugin models might allow you to customize the colors,
                # for others, use default colors:
                'background_color': instance.background_color if hasattr(instance, 'background_color') else 'lightyellow',
                'border_color': instance.border_color if hasattr(instance, 'border_color') else 'lightblue',
            })
            # Finally, render the content through that template, and return the output
            return t.render(c)


.. _Django admin documentation: http://docs.djangoproject.com/en/1.2/ref/contrib/admin/
.. _django-sekizai: https://github.com/ojii/django-sekizai
.. _django-sekizai documentation: http://django-sekizai.readthedocs.org