# -*- coding: utf-8 -*-


TEMPLATE_INHERITANCE_MAGIC = 'INHERIT'
REFRESH_PAGE = 'REFRESH_PAGE'
URL_CHANGE = 'URL_CHANGE'
# This is a trick so "foo is RIGHT" will only ever work for this,
# Same goes for LEFT.
RIGHT = object()
LEFT = object()

# Plugin actions
PLUGIN_MOVE_ACTION = 'move'
PLUGIN_COPY_ACTION = 'copy'

PUBLISHER_STATE_DEFAULT = 0
PUBLISHER_STATE_DIRTY = 1
# Page was marked published, but some of page parents are not.
PUBLISHER_STATE_PENDING = 4
