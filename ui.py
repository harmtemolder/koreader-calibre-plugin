#!/usr/bin/env python

__license__   = 'GPL v3'
__copyright__ = '2020, Harm te Molder <mail@harmtemolder.com>'
__docformat__ = 'restructuredtext en'

from calibre.gui2.actions import InterfaceAction
from calibre_plugins.koreader.main import SettingsDialog

class InterfacePlugin(InterfaceAction):
    name = 'KOReader Sync'

    def genesis(self):
        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_dialog)

    def show_dialog(self):
        base_plugin_object = self.interface_action_base_plugin
        do_user_config = base_plugin_object.do_user_config
        d = SettingsDialog(self.gui, self.qaction.icon(), do_user_config)
        d.show()

    def apply_settings(self):
        from calibre_plugins.koreader.config import prefs
        prefs
