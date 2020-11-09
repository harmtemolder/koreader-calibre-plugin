#!/usr/bin/env python3

__license__   = 'GNU GPLv3'
__copyright__ = '2020, harmtemolder <mail at harmtemolder.com>'
__docformat__ = 'restructuredtext en'

from functools import partial
import sys

from calibre.devices.usbms.driver import debug_print as root_debug_print
from calibre.gui2.actions import InterfaceAction
from calibre_plugins.koreader.config import SettingsDialog

sys.path.append('/Applications/PyCharm.app/Contents/debug-eggs/pydevd-pycharm.egg')
import pydevd_pycharm
pydevd_pycharm.settrace('localhost', stdoutToServer=True, stderrToServer=True,
                        suspend=False)

module_debug_print = partial(root_debug_print, ' koreader:action:', sep='')


class KoreaderAction(InterfaceAction):
    name = 'KOReader Sync'

    def genesis(self):
        debug_print = partial(module_debug_print, 'KoreaderAction:genesis:')
        debug_print('start')
        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_dialog)

    def show_dialog(self):
        debug_print = partial(module_debug_print, 'KoreaderAction:show_dialog:')
        debug_print('start')
        base_plugin_object = self.interface_action_base_plugin
        do_user_config = base_plugin_object.do_user_config
        d = SettingsDialog(self.gui, self.qaction.icon(), do_user_config)
        d.show()

    def apply_settings(self):
        debug_print = partial(module_debug_print, 'KoreaderAction:apply_settings:')
        debug_print('start')
        from calibre_plugins.koreader.config import prefs
        prefs

    def get_device_path(self):
        """Tries to get the path to the connected device.

        Inspired by Kobo Utilities/action.py/get_device_path

        :return: path to the root of the calibre library on device
        """
        debug_print = partial(module_debug_print, 'KoreaderAction:get_device_path:')
        device_path = ''

        try:
            device_connected = self.gui.library_view.model().device_connected
        except:
            device_connected = None

        debug_print('device_connected = ', device_connected)

        if device_connected:
            try:
                device_path = self.gui.device_manager.connected_device._main_prefix
            except:
                debug_print('device connected but no device_path')

        debug_print('device_path = ', device_path)
        return device_path
