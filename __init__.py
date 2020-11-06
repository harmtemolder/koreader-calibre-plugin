#!/usr/bin/env python

__license__   = 'GPL v3'
__copyright__ = '2020, Harm te Molder <mail@harmtemolder.com>'
__docformat__ = 'restructuredtext en'

from calibre.customize import InterfaceActionBase


class KoreaderSync(InterfaceActionBase):
    name                    = 'KOReader Sync'
    description             = 'Get read progress from a locally connected KOReader device'
    supported_platforms     = ['windows', 'osx', 'linux']
    author                  = 'Harm te Molder'
    version                 = (0, 0, 1)
    minimum_calibre_version = (5, 0, 1)  # Because Python 3
    actual_plugin           = 'calibre_plugins.koreader.ui:InterfacePlugin'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.koreader.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()

        # Apply the changes
        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()
