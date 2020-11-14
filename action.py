#!/usr/bin/env python3

__license__   = 'GNU GPLv3'
__copyright__ = '2020, harmtemolder <mail at harmtemolder.com>'
__docformat__ = 'restructuredtext en'

from functools import partial
import io
import json
import re
import sys

from calibre.devices.usbms.driver import debug_print as root_debug_print
from calibre.gui2 import error_dialog, info_dialog
from calibre.gui2.actions import InterfaceAction
from calibre_plugins.koreader import KoreaderSync
from calibre_plugins.koreader.config import COLUMNS, CONFIG
from calibre_plugins.koreader.slpp import slpp as lua


sys.path.append('/Applications/PyCharm.app/Contents/debug-eggs/pydevd-pycharm.egg')
import pydevd_pycharm
pydevd_pycharm.settrace('localhost', stdoutToServer=True, stderrToServer=True,
                        suspend=False)

module_debug_print = partial(root_debug_print, ' koreader:action:', sep='')


class KoreaderAction(InterfaceAction):
    name = KoreaderSync.name
    action_spec = (name, None, KoreaderSync.description, None)
    dont_add_to = frozenset([
        'context-menu', 'context-menu-device','toolbar-child', 'menubar',
        'menubar-device', 'context-menu-cover-browser', 'context-menu-split'])
    dont_remove_from = frozenset(['toolbar', 'toolbar-device'])
    action_type = 'current'

    def genesis(self):
        debug_print = partial(module_debug_print, 'KoreaderAction:genesis:')
        debug_print('start')

        base = self.interface_action_base_plugin
        self.version = '{} {}.{}.{}'.format(base.name, *base.version)

        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)

        self.qaction.triggered.connect(self.show_config)

    def show_config(self):
        self.interface_action_base_plugin.do_user_config(self.gui)

    def apply_settings(self):
        debug_print = partial(module_debug_print, 'KoreaderAction:apply_settings:')
        debug_print('start')
        pass

    def get_connected_device(self):
        """Tries to get the connected device, if any

        :return: the connected device object or None
        """
        debug_print = partial(module_debug_print,
                              'KoreaderAction:get_connected_device:')

        try:
            is_device_present = self.gui.device_manager.is_device_present
        except:
            is_device_present = False


        if not is_device_present:
            debug_print('is_device_present = ', is_device_present)
            error_dialog(self.gui, 'No device found', 'No device found',
                         show=True)
            return None

        try:
            connected_device = self.gui.device_manager.connected_device
            connected_device_type = connected_device.__class__.__name__
        except:
            debug_print('could not get connected_device')
            error_dialog(self.gui, 'Could not connect to device',
                         'Could not connect to device', show=True)
            return None

        debug_print('connected_device_type = ', connected_device_type)
        return connected_device

    def get_paths(self, device):
        """Retrieves paths to sidecars of all books in calibre's library
        on the device

        :param device: a device object
        :return: a dict of uuids with corresponding paths to sidecars
        """
        debug_print = partial(module_debug_print,
                              'KoreaderAction:get_paths:')

        paths = {
            book.uuid: device._main_prefix + book.lpath.replace(
                '.epub', '.sdr/metadata.epub.lua')
            for book in device.books()
        }

        debug_print('found {} path(s) to sidecar Lua files'.format(
            len(paths)))

        return paths

    def get_sidecar(self, device, path):
        """Requests the given path from the given device and returns the
        contents of a sidecar Lua as Python dict

        :param device: a device object
        :param path: a path to a sidecar Lua on the device
        :return: dict or None
        """
        debug_print = partial(module_debug_print,
                              'KoreaderAction:get_sidecar:')

        with io.BytesIO() as outfile:
            try:
                device.get_file(path, outfile)
            except:
                debug_print('could not get ', path)
                return None

            contents = outfile.getvalue()
            parsed_contents = self.parse_sidecar_lua(contents.decode())

        return parsed_contents

    def parse_sidecar_lua(self, sidecar_lua):
        """Parses a sidecar Lua file into a Python dict

        :param sidecar_lua: the contents of a sidecar Lua as a str
        :return: a dict of those contents
        """
        debug_print = partial(module_debug_print,
                              'KoreaderAction:parse_sidecar_lua:')

        try:
            decoded_lua = lua.decode(re.sub('^[^{]*', '', sidecar_lua))
        except:
            debug_print('could not decode sidecar_lua')
            decoded_lua = None

        return decoded_lua

    def update_metadata(self, uuid, key, value):
        debug_print = partial(module_debug_print,
                              'KoreaderAction:update_metadata:')

        try:
            db = self.gui.current_db.new_api
            book_id = db.lookup_by_uuid(uuid)
        except:
            book_id = None

        if not book_id:
            debug_print('could not find {} in calibre’s library'.format(uuid))
            return None

        metadata = db.get_metadata(book_id)
        metadata.set(key, value, extra='test value for extra')
        db.set_metadata(book_id, metadata, set_title=False, set_authors=False)

    def sync_to_calibre(self):
        """This plugin’s main purpose. It syncs the contents of
        KOReader’s metadata sidecar files into calibre’s metadata.

        :return:
        """
        debug_print = partial(module_debug_print,
                              'KoreaderAction:sync_to_calibre:')

        device = self.get_connected_device()

        if not device:
            return None

        sidecar_paths = self.get_paths(device)

        for book_uuid, sidecar_path in sidecar_paths.items():
            sidecar_contents = self.get_sidecar(device, sidecar_path)

            for column in COLUMNS:
                name = column['name']
                target = CONFIG[name]

                if target == '':
                    # No column mapped, so do not sync
                    continue

                property = column['sidecar_property']
                if property == '*':
                    value = json.dumps(sidecar_contents, indent=4)
                else:
                    property_split = property.split('.')
                    value = sidecar_contents
                    for subproperty in property_split:
                        value = value[subproperty]

                self.update_metadata(book_uuid, target, value)

            debug_print('updated metadata for ', book_uuid)
