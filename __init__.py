#!/usr/bin/env python3

__license__   = 'GNU GPLv3'
__copyright__ = '2020, harmtemolder <mail at harmtemolder.com>'
__docformat__ = 'restructuredtext en'

from functools import partial
import os

from calibre.customize import InterfaceActionBase
from calibre.devices.usbms.driver import debug_print as _debug_print
from calibre.utils.config import JSONConfig

debug_print = partial(_debug_print, ' koreader:__init__:', sep='')


class KoreaderSync(InterfaceActionBase):
    name                    = 'KOReader Sync'
    description             = 'Get read progress from a locally connected KOReader device'
    author                  = 'harmtemolder'
    version                 = (0, 1, 0)
    minimum_calibre_version = (5, 0, 1)  # Because Python 3
    config                  = JSONConfig(os.path.join('plugins', 'KOReader Sync.json'))
    actual_plugin           = 'calibre_plugins.koreader.action:KoreaderAction'

    def is_customizable(self):
        debug_print('KoreaderSync:is_customizable:start')
        return True

    def config_widget(self):
        debug_print('KoreaderSync:config_widget:start')
        from calibre_plugins.koreader.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        debug_print('KoreaderSync:save_settings:start')
        config_widget.save_settings()

        # Apply the changes
        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()
