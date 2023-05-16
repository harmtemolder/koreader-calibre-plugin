#!/usr/bin/env python3

"""KOReader Sync Plugin for Calibre."""

from datetime import datetime
from functools import partial
import io
import json
import os
import re
import sys

from PyQt5.Qt import QUrl
from calibre_plugins.koreader.slpp import slpp as lua
from calibre_plugins.koreader.config import (
    SUPPORTED_DEVICES,
    UNSUPPORTED_DEVICES,
    COLUMNS,
    CONFIG,
)
from calibre_plugins.koreader import (
    DEBUG,
    DRY_RUN,
    PYDEVD,
    KoreaderSync,
)

from calibre.utils.iso8601 import utc_tz, local_tz
from calibre.gui2.dialogs.message_box import MessageBox
from calibre.gui2.actions import InterfaceAction
from calibre.gui2 import (
    error_dialog,
    warning_dialog,
    info_dialog,
    open_url,
)
from calibre.devices.usbms.driver import debug_print as root_debug_print
from calibre.constants import numeric_version

__license__ = 'GNU GPLv3'
__copyright__ = '2021, harmtemolder <mail at harmtemolder.com>'
__docformat__ = 'restructuredtext en'

if numeric_version >= (5, 5, 0):
    module_debug_print = partial(root_debug_print, ' koreader:action:', sep='')
else:
    module_debug_print = partial(root_debug_print, 'koreader:action:')

if DEBUG and PYDEVD:
    try:
        sys.path.append(
            # '/Applications/PyCharm.app/Contents/debug-eggs/pydevd-pycharm.egg'  # macOS
            '/opt/pycharm-professional/debug-eggs/pydevd-pycharm.egg'  # Manjaro Linux
        )
        import pydevd_pycharm

        pydevd_pycharm.settrace(
            'localhost', stdoutToServer=True, stderrToServer=True,
            suspend=False
        )
    except Exception as e:
        module_debug_print('could not start pydevd_pycharm, e = ', e)
        PYDEVD = False


class KoreaderAction(InterfaceAction):
    name = KoreaderSync.name
    action_spec = (name, 'copy-to-library.png', KoreaderSync.description, None)
    action_add_menu = True
    action_menu_clone_qaction = 'Sync from KOReader'
    dont_add_to = frozenset(
        [
            'context-menu', 'context-menu-device', 'toolbar-child', 'menubar',
            'menubar-device', 'context-menu-cover-browser',
            'context-menu-split']
    )
    dont_remove_from = InterfaceAction.all_locations - dont_add_to
    action_type = 'current'

    def genesis(self):
        debug_print = partial(module_debug_print, 'KoreaderAction:genesis:')
        debug_print('start')

        base = self.interface_action_base_plugin
        self.version = f'{base.name} (v{".".join(map(str, base.version))})'

        # Overwrite icon with actual KOReader logo
        icon = get_icons(
            'images/icon.png'
        )
        self.qaction.setIcon(icon)

        # Left-click action
        self.qaction.triggered.connect(self.sync_to_calibre)

        # Right-click menu (already includes left-click action)
        self.create_menu_action(
            self.qaction.menu(),
            'Sync Missing Sidecars to KOReader',
            'Sync Missing Sidecars to KOReader',
            icon='config.png',
            description='Where Calibre has a raw metadata entry but KOReader '
                'does not have a sidecar file, push the metadata from Calibre '
                'to a new sidecar file.',
            triggered=self.sync_missing_sidecars_to_koreader
        )

        self.qaction.menu().addSeparator()

        self.create_menu_action(
            self.qaction.menu(),
            'Configure KOReader Sync',
            'Configure',
            icon='config.png',
            description='Configure KOReader Sync',
            triggered=self.show_config
        )

        self.qaction.menu().addSeparator()

        self.create_menu_action(
            self.qaction.menu(),
            'Readme for KOReader Sync',
            'Readme',
            icon='dialog_question.png',
            description='About KOReader Sync',
            triggered=self.show_readme
        )

        self.create_menu_action(
            self.qaction.menu(),
            'About KOReader Sync',
            'About',
            icon='dialog_information.png',
            description='About KOReader Sync',
            triggered=self.show_about
        )

    def show_config(self):
        self.interface_action_base_plugin.do_user_config(self.gui)

    def show_readme(self):
        debug_print = partial(module_debug_print, 'KoreaderAction:show_readme:')
        debug_print('start')
        readme_url = QUrl(
            'https://git.sr.ht/~harmtemolder/koreader-calibre'
            '-plugin#koreader-calibre-plugin'
        )
        open_url(readme_url)

    def show_about(self):
        debug_print = partial(module_debug_print, 'KoreaderAction:show_about:')
        debug_print('start')
        text = get_resources('about.txt').decode(
            'utf-8'
        )
        icon = get_icons(
            'images/icon.png'
        )

        about_dialog = MessageBox(
            MessageBox.INFO,
            f'About {self.version}',
            text,
            det_msg='',
            q_icon=icon,
            show_copy_button=False,
            parent=None,
        )

        return about_dialog.exec_()

    def apply_settings(self):
        debug_print = partial(
            module_debug_print,
            'KoreaderAction:apply_settings:'
        )
        debug_print('start')

    def get_connected_device(self):
        """Tries to get the connected device, if any

        :return: the connected device object or None
        """
        debug_print = partial(
            module_debug_print,
            'KoreaderAction:get_connected_device:'
        )

        try:
            is_device_present = self.gui.device_manager.is_device_present
        except:
            is_device_present = False

        if not is_device_present:
            debug_print('is_device_present = ', is_device_present)
            error_dialog(
                self.gui,
                'No device found',
                'No device found',
                det_msg='',
                show=True,
                show_copy_button=False
            )
            return None

        try:
            connected_device = self.gui.device_manager.connected_device
            connected_device_type = connected_device.__class__.__name__
        except:
            debug_print('could not get connected_device')
            error_dialog(
                self.gui,
                'Could not connect to device',
                'Could not connect to device',
                det_msg='',
                show=True,
                show_copy_button=False
            )
            return None

        debug_print('connected_device_type = ', connected_device_type)
        return connected_device

    def get_paths(self, device):
        """Retrieves paths to sidecars of all books in calibre's library
        on the device

        :param device: a device object
        :return: a dict of uuids with corresponding paths to sidecars
        """
        debug_print = partial(
            module_debug_print,
            'KoreaderAction:get_paths:'
        )

        debug_print(
            'found these paths to books:\n\t',
            '\n\t'.join([book.path for book in device.books()])
        )

        debug_print(
            'found these lpaths to books:\n\t',
            '\n\t'.join([book.lpath for book in device.books()])
        )

        paths = {
            book.uuid: re.sub(
                r'\.(\w+)$', r'.sdr/metadata.\1.lua', book.path
            )
            for book in device.books()
        }

        debug_print(
            f'generated {len(paths)} path(s) to sidecar Lua files:\n\t',
            '\n\t'.join(paths.values())
        )

        return paths

    def get_sidecar(self, device, path):
        """Requests the given path from the given device and returns the
        contents of a sidecar Lua as Python dict

        :param device: a device object
        :param path: a path to a sidecar Lua on the device
        :return: dict or None
        """
        debug_print = partial(
            module_debug_print,
            'KoreaderAction:get_sidecar:'
        )

        with io.BytesIO() as outfile:
            try:
                device.get_file(path, outfile)
            except:
                debug_print('could not get ', path)
                return None

            contents = outfile.getvalue()

            try:
                decoded_contents = contents.decode()
            except UnicodeDecodeError:
                debug_print('could not decode ', contents)
                return None

            debug_print(f'parsing {path}')
            parsed_contents = self.parse_sidecar_lua(decoded_contents)
            parsed_contents['calculated']['date_sidecar_modified'] = datetime.fromtimestamp(
                os.path.getmtime(path)).replace(tzinfo=local_tz
                )
            parsed_contents['calculated']['date_synced'] = datetime.now().replace(tzinfo=local_tz)

        return parsed_contents

    def parse_sidecar_lua(self, sidecar_lua):
        """Parses a sidecar Lua file into a Python dict

        :param sidecar_lua: the contents of a sidecar Lua as a str
        :return: a dict of those contents
        """
        debug_print = partial(
            module_debug_print,
            'KoreaderAction:parse_sidecar_lua:'
        )

        try:
            clean_lua = re.sub('^[^{]*', '', sidecar_lua).strip()
            decoded_lua = lua.decode(clean_lua)
        except:
            debug_print('could not decode sidecar_lua')
            decoded_lua = None

        if 'bookmarks' in decoded_lua:
            debug_print('calculating first and last bookmark dates')
            bookmark_dates = [
                datetime.strptime(
                    bookmark['datetime'],
                    '%Y-%m-%d %H:%M:%S'
                ).replace(tzinfo=utc_tz)
                for bookmark in decoded_lua['bookmarks'].values()
            ]

            if len(bookmark_dates) > 0:
                decoded_lua['calculated'] = {
                    'first_bookmark': min(bookmark_dates),
                    'last_bookmark': max(bookmark_dates),
                }

        return decoded_lua

    def update_metadata(self, uuid, keys_values_to_update):
        """Update multiple metadata columns for the given book.

        :param uuid: identifier for the book
        :param keys_values_to_update: a dict of keys to update with values
        :return: a dict of values that can be used to report back to the user
        """
        debug_print = partial(
            module_debug_print,
            'KoreaderAction:update_metadata:'
        )

        try:
            db = self.gui.current_db.new_api
            book_id = db.lookup_by_uuid(uuid)
        except:
            book_id = None

        if not book_id:
            debug_print(f'could not find {uuid} in calibre’s library')
            return False, {'result': 'could not find uuid in calibre’s library'}

        # Get the current metadata for the book from the library
        metadata = db.get_metadata(book_id)

        updates = []
        # Update that metadata locally
        for key, new_value in keys_values_to_update.items():
            old_value = metadata.get(key)

            if new_value != old_value:
                updates.append(key)
                metadata.set(key, new_value)

        # Write the updated metadata back to the library
        if len(updates) == 0:
            debug_print(
                'no changed metadata for uuid = ', uuid,
                ', id = ', book_id
            )
        elif DEBUG and DRY_RUN:
            debug_print(
                'would have updated the following fields for uuid = ',
                uuid, ', id = ', book_id, ': ', updates
            )
        else:
            db.set_metadata(
                book_id, metadata, set_title=False,
                set_authors=False
            )
            debug_print(
                'updated the following fields for uuid = ', uuid,
                ', id = ', book_id, ': ', updates
            )

        return True, {
            'result': 'success',
            'book_id': book_id,
        }

    def check_device(self, device):
        """Return .

        :param device: The connected device.
        :return: False if device is specifically not supported,
        otherwise True
        """

        debug_print = partial(
            module_debug_print,
            'KoreaderAction:check_device:'
        )

        if not device:
            return False

        device_class = device.__class__.__name__

        if device_class in UNSUPPORTED_DEVICES:
            debug_print('unsupported device, device_class = ', device_class)
            error_dialog(
                self.gui,
                'Device not supported',
                f'Devices of the type {device_class} are not supported by this plugin. I '
                f'have tried to get it working, but couldn’t. Sorry.',
                det_msg='',
                show=True,
                show_copy_button=False
            )
            return False
        elif device_class in SUPPORTED_DEVICES:
            return True
        else:
            debug_print(
                'not yet supported device, device_class = ',
                device_class
            )
            warning_dialog(
                self.gui,
                'Device not yet supported',
                f'Devices of the type {device_class} are not yet supported by this plugin. '
                f'Please check if there already is a feature request for this '
                f'<a href="https://github.com/harmtemolder/koreader-calibre-plugin/issues">'
                f'here</a>. If not, feel free to create one. I\'ll try to sync anyway.',
                det_msg='',
                show=True,
                show_copy_button=False
            )
            return True

    def push_metadata_to_koreader_sidecar(self, book_uuid, path):
        """Create a sidecar file for the given book.

        :param book_uuid: Calibre's uuid for the book
        :param path: path to sidecar file to create
        :return: tuple of bool and result dict
        """

        debug_print = partial(
            module_debug_print,
            'KoreaderAction:push_metadata_to_koreader_sidecar:'
        )

        try:
            db = self.gui.current_db.new_api
            book_id = db.lookup_by_uuid(book_uuid)
            debug_print(f"Book id is {book_id}")
        except:
            book_id = None

        if not book_id:
            debug_print(f'could not find {book_uuid} in calibre’s library')
            return "failure", {
                'result': f"Could not find uuid {book_uuid} in Calibre's library."
            }

        # Get the current metadata for the book from the library
        metadata = db.get_metadata(book_id)
        sidecar_metadata = metadata.get(CONFIG["column_sidecar"])
        if not sidecar_metadata:
            return "no_metadata", {
                'result': f'No KOReader metadata for book_id {book_id}, no need to push.'
            }
        sidecar_dict = json.loads(sidecar_metadata)
        sidecar_lua = lua.encode(sidecar_dict)
        # not certain if tabs need to be replaced with spaces but it can't hurt
        sidecar_lua = sidecar_lua.replace("\t", "    ")
        # something is happening in the decoding/encoding which is replacing [1] with ["1"]
        # which ofc breaks the settings file; this regex strips the "" marks
        sidecar_lua = re.sub(r'\["([0-9])+"\]', r'[\1]', sidecar_lua)
        sidecar_lua_formatted = f"-- we can read Lua syntax here!\nreturn {sidecar_lua}\n"
        try:
            os.makedirs(os.path.dirname(path))
        except FileExistsError:
            # dir exists, so we're fine
            pass

        with open(path, "w", encoding="utf-8") as f:
            debug_print(f"Writing to {path}")
            f.write(sidecar_lua_formatted)

        return "success", {
            'result': 'success',
            'book_id': book_id,
        }

    def sync_missing_sidecars_to_koreader(self):
        """Push the content of Calibre's raw metadata column to KOReader
        for any files which are missing in KOReader. Does not touch existing
        metadata sidecars on KOReader.

        Intended for e.g. setting up a new device and syncing to it for the first
        time.

        :return:
        """
        debug_print = partial(
            module_debug_print,
            'KoreaderAction:sync_missing_sidecars_to_koreader:'
        )

        if CONFIG["column_sidecar"] is '':
            error_dialog(
                self.gui,
                'Failure',
                'Raw metadata column not mapped, impossible to push metadata to sidecars',
                show=True,
                show_copy_button=False
            )
            return None

        device = self.get_connected_device()

        if not self.check_device(device):
            return None

        sidecar_paths = self.get_paths(device)
        sidecar_paths_exist = {}
        sidecar_paths_not_exist = {}
        for book_uuid, path in sidecar_paths.items():
            if os.path.exists(path):
                sidecar_paths_exist[book_uuid] = path
            else:
                sidecar_paths_not_exist[book_uuid] = path
        debug_print(
            "Sidecars not present on device:",
            "\n".join(sidecar_paths_not_exist.values())
        )

        results = []
        num_candidates = len(sidecar_paths_not_exist)
        num_success = 0
        num_no_metadata = 0
        num_fail = 0
        for book_uuid, path in sidecar_paths_not_exist.items():
            result, details = self.push_metadata_to_koreader_sidecar(book_uuid, path)
            if result is "success":
                num_success += 1
                results.append(
                    {
                        **details,
                        'book_uuid': book_uuid,
                        'sidecar_path': path,
                    }
                )
            elif result is "failure":
                num_fail += 1
                results.append(
                    {
                        **details,
                        'book_uuid': book_uuid,
                        'sidecar_path': path,
                    }
                )
            elif result is "no_metadata":
                num_no_metadata += 1
                results.append(
                    {
                        **details,
                        'book_uuid': book_uuid,
                        'sidecar_path': path,
                    }
                )

        results_message = (
            f'{num_candidates} books on device without sidecars.\n'
            f'Sidecar creation succeeded for {num_success}.\n'
            f'Sidecar creation failed for {num_fail}.\n'
            f'No attempt made for {num_no_metadata} (no metadata in Calibre to push).\n'
            f'See below for details.'
        )

        if num_success > 0 and num_fail > 0:
            warning_dialog(
                self.gui,
                'Results',
                results_message,
                det_msg=json.dumps(results, indent=2),
                show=True,
                show_copy_button=False
            )
        elif num_success > 0 or num_no_metadata > 0:  # and num_fail == 0
            info_dialog(
                self.gui,
                'Success',
                results_message,
                det_msg=json.dumps(results, indent=2),
                show=True,
                show_copy_button=False
            )
        else:
            error_dialog(
                self.gui,
                'Failure',
                results_message,
                det_msg=json.dumps(results, indent=2),
                show=True,
                show_copy_button=False
            )

    def sync_to_calibre(self):
        """This plugin’s main purpose. It syncs the contents of
        KOReader’s metadata sidecar files into calibre’s metadata.

        :return:
        """
        debug_print = partial(
            module_debug_print,
            'KoreaderAction:sync_to_calibre:'
        )

        device = self.get_connected_device()

        if not self.check_device(device):
            return None

        sidecar_paths = self.get_paths(device)

        results = []
        num_success = 0
        num_fail = 0

        for book_uuid, sidecar_path in sidecar_paths.items():
            sidecar_contents = self.get_sidecar(device, sidecar_path)

            if not sidecar_contents:
                debug_print('skipping uuid = ', book_uuid)
                results.append(
                    {
                        'result': 'could not get sidecar contents',
                        'book_uuid': book_uuid,
                        'sidecar_path': sidecar_path,
                    }
                )
                num_fail += 1
                continue

            debug_print('reading sidecar for ', book_uuid)
            keys_values_to_update = {}

            for column in COLUMNS:
                name = column['name']
                target = CONFIG[name]

                if target == '':
                    # No column mapped, so do not sync
                    continue

                sidecar_property = column['sidecar_property']
                value = sidecar_contents

                for subproperty in sidecar_property:
                    if subproperty in value:
                        value = value[subproperty]
                    else:
                        debug_print(f'subproperty "{subproperty}" not found in value')
                        value = None
                        break

                if not value:
                    continue

                # Transform value if required
                if 'transform' in column:
                    debug_print('transforming value for ', target)
                    value = column['transform'](value)

                keys_values_to_update[target] = value

            success, result = self.update_metadata(
                book_uuid, keys_values_to_update
            )
            results.append(
                {
                    **result,
                    'book_uuid': book_uuid,
                    'sidecar_path': sidecar_path,
                    'updated': json.dumps(keys_values_to_update, default=str),
                }
            )
            if success:
                num_success += 1
            else:
                num_fail += 1

        results_message = (
            f'Attempted to sync {len(sidecar_paths)}.\n'
            f'Metadata sync succeeded for {num_success}.\n'
            f'Metadata sync failed for {num_fail}.\n'
            f'(Failures may just be because you have not opened every book in '
            f'KOReader yet. See below for details.'
        )

        if num_success > 0 and num_fail > 0:
            warning_dialog(
                self.gui,
                'Results',
                results_message,
                det_msg=json.dumps(results, indent=2),
                show=True,
                show_copy_button=False
            )
        elif num_success > 0:  # and num_fail == 0
            info_dialog(
                self.gui,
                'Metadata synced for all books',
                results_message,
                det_msg=json.dumps(results, indent=2),
                show=True,
                show_copy_button=False
            )
        else:  # not num_success
            error_dialog(
                self.gui,
                'No metadata could be synced',
                results_message,
                det_msg=json.dumps(results, indent=2),
                show=True,
                show_copy_button=False
            )
