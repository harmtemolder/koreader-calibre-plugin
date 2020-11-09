#!/usr/bin/env python3

__license__   = 'GNU GPLv3'
__copyright__ = '2020, harmtemolder <mail at harmtemolder.com>'
__docformat__ = 'restructuredtext en'

from functools import partial
import sys

from calibre.devices.usbms.driver import debug_print as root_debug_print
from calibre.devices.smart_device_app.driver import SMART_DEVICE_APP
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

    def get_smart_device(self):
        """Tries to get the connected smart device, if any.

        :return: the connected SMART_DEVICE_APP object
        """
        debug_print = partial(module_debug_print,
                              'KoreaderAction:get_smart_device:')

        try:
            is_device_present = self.gui.device_manager.is_device_present
        except:
            is_device_present = False


        if not is_device_present:
            debug_print('is_device_present = ', is_device_present)
            return False

        try:
            connected_device = self.gui.device_manager.connected_device
            is_smart_device = isinstance(connected_device, SMART_DEVICE_APP)
        except:
            is_smart_device = False

        if not is_smart_device:
            debug_print('is_smart_device = ', is_smart_device)
            return False

        # debug_print('connected_device = ', connected_device)
        connected_device._show_message('test')
        return connected_device
