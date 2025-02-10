#!/usr/bin/env python3

"""KOReader Sync Plugin for Calibre."""

from datetime import datetime
from functools import partial
import io
import json
import os
import re
import sys

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import brotli

from PyQt5.Qt import QUrl, QTimer, QTime
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
from calibre.gui2.device import device_signals
from calibre.gui2 import (
    error_dialog,
    warning_dialog,
    info_dialog,
    open_url,
)
from calibre.devices.usbms.driver import debug_print as root_debug_print
from calibre.constants import numeric_version
from enum import Enum, auto

__license__ = 'GNU GPLv3'
__copyright__ = '2021, harmtemolder <mail at harmtemolder.com>'
__modified_by__ = 'kyxap kyxappp@gmail.com'
__modification_date__ = '2024'
__docformat__ = 'restructuredtext en'

if numeric_version >= (5, 5, 0):
    module_debug_print = partial(root_debug_print, ' koreader:action:', sep='')
else:
    module_debug_print = partial(root_debug_print, 'koreader:action:')

if DEBUG and PYDEVD:
    try:
        sys.path.append(
            # '/Applications/PyCharm.app/Contents/debug-eggs/pydevd-pycharm.egg'  # macOS
            '/opt/pycharm-professional/debug-eggs/pydevd-pycharm.egg'
            # Manjaro Linux
        )
        import pydevd_pycharm

        pydevd_pycharm.settrace(
            'localhost', stdoutToServer=True, stderrToServer=True,
            suspend=False
        )
    except Exception as e:
        module_debug_print('could not start pydevd_pycharm, e = ', e)
        PYDEVD = False


class GetSidecarStatus(Enum):
    PATH_NOT_FOUND = auto()
    DECODE_FAILED = auto()


class OperationStatus(Enum):
    PASS = auto()
    FAIL = auto()
    SKIP = auto()


def is_system_path(path):
    """
    KOreader user may have some files in the root which we want to skip to
    avoid showing warning message

    :param path: path to sidecar file (*.lua)
    :return: true/false if partial match found
    """
    to_ignore = ['kfmon.sdr', 'koreader.sdr']
    return any(substring in path for substring in to_ignore)


def append_results(results, status_msg, book_uuid, sidecar_path):
    debug_print = partial(
        module_debug_print,
        'KoreaderAction:append_results:'
    )
    debug_print(f'{sidecar_path} - {status_msg}')
    return results.append(
        {
            'status': status_msg,
            'book_uuid': book_uuid,
            'sidecar_path': sidecar_path,
        }
    )


def parse_sidecar_lua(sidecar_lua):
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
        if type(decoded_lua['bookmarks']) is list:
            decoded_lua['bookmarks'] = {i+1: bookmark for i, bookmark in enumerate(decoded_lua['bookmarks'])}  # Starts from 1

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


class KoreaderAction(InterfaceAction):
    name = KoreaderSync.name
    action_spec = (name, 'edit-redo.png', KoreaderSync.description, None)
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

        # TODO: Sync calibre to KOReader is disabled see more in #8
        self.create_menu_action(
            self.qaction.menu(),
            'Sync missing to KOReader',
            'Sync missing to KOReader',
            icon='edit-undo.png',
            description='If calibre has an entry in the "Raw sidecar column", '
                        'but KOReader does not have a sidecar file, push the '
                        'metadata from calibre to a new sidecar file.',
            triggered=self.sync_missing_sidecars_to_koreader
        )

        self.create_menu_action(
            self.qaction.menu(),
            'Sync from ProgressSync',
            'Sync from ProgressSync',
            icon='convert.png',
            description='Use KOReader''s built in ProgressSync Plugin '
                        'to update percentRead int or float.',
            triggered=self.sync_progress_from_progresssync
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
            description='Readme for KOReader Sync',
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
        
        # Start the scheduled progress sync if enabled
        if CONFIG["checkbox_enable_scheduled_progressync"]:
            self.scheduled_progress_sync()

        # Start the device connection watcher if enabled
        if CONFIG["checkbox_enable_automatic_sync"]:
            device_signals.device_metadata_available.connect(self._on_device_metadata_available)

    def show_config(self):
        self.interface_action_base_plugin.do_user_config(self.gui)

    def show_readme(self):
        debug_print = partial(module_debug_print, 'KoreaderAction:show_readme:')
        debug_print('start')
        readme_url = QUrl(
            'https://github.com/harmtemolder/koreader-calibre-plugin#readme'
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

    def _on_device_metadata_available(self):
        self.sync_to_calibre()

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
            f'found {len(device.books())} paths to books:\n\t',
            '\n\t'.join([book.path for book in device.books()])
        )

        debug_print(
            f'found {len(device.books())} lpaths to books:\n\t',
            '\n\t'.join([book.lpath for book in device.books()])
        )

        for book in device.books():
            debug_print(f'uuid to path: {book.uuid} - {book.path}')

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
                return GetSidecarStatus.PATH_NOT_FOUND

            contents = outfile.getvalue()

            try:
                decoded_contents = contents.decode()
            except UnicodeDecodeError:
                debug_print('could not decode ', contents)
                return GetSidecarStatus.DECODE_FAILED

            debug_print(f'Parsing: {path}')
            parsed_contents = parse_sidecar_lua(decoded_contents)
            parsed_contents['calculated'] = {}
            try:
                parsed_contents['calculated'][
                    'date_sidecar_modified'] = datetime.fromtimestamp(
                    os.path.getmtime(path)).replace(tzinfo=local_tz
                                                    )
            except:
                pass
            parsed_contents['calculated'][
                'date_synced'] = datetime.now().replace(tzinfo=local_tz)

        return parsed_contents

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
            debug_print('Looking uuid in calibre db: ', uuid)
            db = self.gui.current_db.new_api
            book_id = db.lookup_by_uuid(uuid)
        except:
            book_id = None

        if not book_id:
            debug_print(f'could not find {uuid} in calibre\'s library')
            return OperationStatus.SKIP, {
                'result': 'could not find uuid in calibre\'s library, have you deleted this book from library?'}

        # Get the current metadata for the book from the library
        metadata = db.get_metadata(book_id)

        # Check config to sync only if data is more recent
        if CONFIG['checkbox_sync_if_more_recent']:
            date_modified_key = CONFIG['column_date_sidecar_modified']
            current_date_modified = metadata.get(date_modified_key)
            new_date_modified = keys_values_to_update.get(date_modified_key)
            if current_date_modified is not None and new_date_modified is not None:
                if current_date_modified.timestamp() >= new_date_modified.timestamp():
                    debug_print(
                        f'book {book_id} date_modified {new_date_modified} older than current {current_date_modified}')
                    return OperationStatus.SKIP, {
                        'result': 'skipped, data in calibre is newer',
                        'book_id': book_id,
                    }
            # Fallback if no 'Date Modified Column' is set or not obtainable (wireless)
            elif new_date_modified is None:
                read_percent_key = CONFIG['column_percent_read'] or CONFIG[
                    'column_percent_read_int']
                current_read_percent = metadata.get(read_percent_key)
                new_read_percent = keys_values_to_update.get(read_percent_key)
                if current_read_percent is not None and new_read_percent is not None:
                    if current_read_percent >= new_read_percent:
                        debug_print(
                            f'book {book_id} read_percent {new_read_percent} lower or equal than current {current_read_percent}')
                        return OperationStatus.SKIP, {
                            'result': 'skipped, read Percent is lower or equal to the one stored in calibre',
                            'book_id': book_id,
                        }
                elif current_read_percent is not None and new_read_percent is None:
                    debug_print(
                        f'book {book_id} read_percent is None but existing is {current_read_percent}')
                    return OperationStatus.SKIP, {
                        'result': 'skipped, no new read percent found',
                        'book_id': book_id,
                    }

        # Check config to sync only if the book is not yet finished
        if CONFIG['checkbox_no_sync_if_finished']:
            read_percent_key = CONFIG['column_percent_read'] or CONFIG[
                'column_percent_read_int']
            current_read_percent = metadata.get(read_percent_key)
            status_key = CONFIG['column_status']
            current_status = metadata.get(status_key)
            if current_read_percent is not None and current_read_percent >= 100 \
                or current_status is not None and current_status == "complete":
                debug_print(f'book {book_id} was already finished')
                return OperationStatus.SKIP, {
                    'result': 'skipped, book already finished',
                    'book_id': book_id,
                }

        # Check and correct reading status if required
        status_key = CONFIG['column_status']
        if status_key:
            new_status = keys_values_to_update.get(status_key)
            if not new_status:
                read_percent_key = CONFIG['column_percent_read'] or CONFIG[
                    'column_percent_read_int']
                new_read_percent = keys_values_to_update.get(read_percent_key)
                current_status = metadata.get(status_key)
                if new_read_percent and current_status != "abandoned":
                    if new_read_percent > 0 and new_read_percent < 100 and current_status != "reading":
                        debug_print(
                            f'book {book_id} set column_status to reading')
                        keys_values_to_update[status_key] = "reading"
                        status_bool_key = CONFIG['column_status_bool']
                        if status_bool_key:
                            keys_values_to_update[status_bool_key] = False
                    elif new_read_percent >= 100 and current_status != "complete":
                        debug_print(
                            f'book {book_id} set column_status to complete')
                        keys_values_to_update[status_key] = "complete"
                        status_bool_key = CONFIG['column_status_bool']
                        if status_bool_key:
                            keys_values_to_update[status_bool_key] = True

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

        return OperationStatus.PASS, {
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
                'result': f"Could not find uuid {book_uuid} in Calibre's "
                          f"library."
            }

        # Get the current metadata for the book from the library
        metadata = db.get_metadata(book_id)
        sidecar_metadata = metadata.get(CONFIG["column_sidecar"])
        if not sidecar_metadata:
            return "no_metadata", {
                'result': f'No KOReader metadata for book_id {book_id}, no '
                          f'need to push.'
            }
        sidecar_dict = json.loads(sidecar_metadata)
        sidecar_lua = lua.encode(sidecar_dict)
        sidecar_lua_formatted = f"-- we can read Lua syntax here!\nreturn {sidecar_lua}\n"
        try:
            os.makedirs(os.path.dirname(path))
        except FileExistsError:
            # dir exists, so we're fine
            pass
        except PermissionError as perm_e:
            return "failure", {
                'result': f'Unable to create directory at: '
                          f'{path} due to {perm_e}',
                'book_id': book_id,
            }
        except OSError as os_e:
            return "failure", {
                'result': f'Unexpectable exception is occurred, '
                          f'please report: {os_e}',
                'book_id': book_id,
            }

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

        if CONFIG["column_sidecar"] == '':
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
        debug_print('sidecar_paths: ', sidecar_paths)
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
            result, details = self.push_metadata_to_koreader_sidecar(book_uuid,
                                                                     path)
            if result == "success":
                num_success += 1
                results.append(
                    {
                        **details,
                        'book_uuid': book_uuid,
                        'sidecar_path': path,
                    }
                )
            elif result == "failure":
                num_fail += 1
                results.append(
                    {
                        **details,
                        'book_uuid': book_uuid,
                        'sidecar_path': path,
                    }
                )
            elif result == "no_metadata":
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

    def sync_progress_from_progresssync(self):
        """Use KOReader's ProgressSync Server to update Calibre metadata rather than a manual sync.

        Intended to easily update Calibre with the lastest reading progress from KOReader.

        :return:
        """

        debug_print = partial(
            module_debug_print,
            'KoreaderAction:sync_progress_from_progresssync:'
        )

        if CONFIG["column_md5"] == '':
            error_dialog(
                self.gui,
                'Failure',
                'MD5 column not mapped, impossible to get metadata from Progress Sync Server',
                show=True,
                show_copy_button=False
            )
            return None
        
        if CONFIG["progress_sync_password"] == '':
            error_dialog(
                self.gui,
                'Failure',
                'Progress Sync Account is not logged in, add credentials in plugin settings',
                show=True,
                show_copy_button=False
            )
            return None
        
        'Get list of books with MD5 column'
        db = self.gui.current_db.new_api
        md5_column = CONFIG["column_md5"]
        books_with_md5 = db.search(f'{md5_column}:!''')
        
        results = []
        num_success = 0
        num_skip = 0

        headers = {
            'x-auth-user': CONFIG["progress_sync_username"],
            'x-auth-key': CONFIG["progress_sync_password"],
            'Accept': 'application/vnd.koreader.v1+json',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'User-Agent': f'CalibreKOReaderSync/{self.version}'
        }

        for book_id in books_with_md5:
            metadata = db.get_metadata(book_id)
            md5_value = metadata.get(md5_column)

            try:
                url = f'{CONFIG["progress_sync_url"]}/syncs/progress/{md5_value}'
                request = Request(url, headers=headers)
                with urlopen(request, timeout=20) as response:
                    response_data = response.read()
                    if response_data == b'{}':
                        results.append({
                            'book_id': book_id,
                            'md5_value': md5_value,
                            'error': 'No ProgressSync entry for md5 hash'
                        })
                        num_skip += 1
                        continue
                    progress_data =  json.loads(brotli.decompress(response_data).decode('utf-8'))
                
                results.append({
                    'book_id': book_id,
                    'md5_value': md5_value,
                    **progress_data
                })
                num_success += 1
                
                # List of keys to check
                ProgressSync_Columns = ['column_percent_read', 'column_percent_read_int', 'column_last_read_location']

                # Map of progress_data keys to match each config key
                progress_mapping = { 
                    'column_percent_read': progress_data['percentage'],
                    'column_percent_read_int': round(progress_data['percentage']*100),
                    'column_last_read_location': progress_data['progress']
                    # Device, Device ID, and timestamps could also be added
                }

                # Dictionary to store values to be updated
                keys_values_to_update = {}

                for key in ProgressSync_Columns:
                    internal_column = CONFIG.get(key, '')  # Get internal column name from CONFIG
                    if not internal_column:  # Skip if internal column name is blank
                        continue
                    
                    current_value = metadata.get(internal_column)  # Get current value from metadata
                    remote_value = progress_mapping[key]

                    # Compare current and remote values
                    if current_value != remote_value:
                        keys_values_to_update[internal_column] = remote_value

                # Update only if there are differences
                if keys_values_to_update:
                    self.update_metadata(metadata.get('uuid'), keys_values_to_update)

            except (HTTPError, URLError) as e:
                msg = f'Failed to make progress sync query: {url}, error: {str(e)}'
                debug_print(msg)
                results.append({
                    'book_id': book_id,
                    'md5_value': md5_value,
                    'error': 'No data received'
                })
                num_skip += 1

        results_message = (
            f'Total books with MD5 values: {len(books_with_md5)}\n\n'
            f'Successful syncs: {num_success}\n'
            f'Failed syncs: {num_skip}\n\n'
        )

        if num_success > 0 and num_skip == 0:
            info_dialog(
                self.gui,
                'Progress sync finished',
                results_message + 'All looks good!\n\n',
                det_msg=json.dumps(results, indent=2),
                show=True,
                show_copy_button=False
            )
        elif num_skip > 0:
            error_dialog(
                self.gui,
                'Some syncs failed',
                results_message + 'There were some errors during the sync process!\n'
                                'Please investigate and report if it looks like a bug\n\n',
                det_msg=json.dumps(results, indent=2),
                show=True,
                show_copy_button=False
            )
        else:
            warning_dialog(
                self.gui,
                'No successful syncs',
                results_message + 'No successful syncs\n'
                                'Please investigate and report if it looks like a bug\n\n',
                det_msg=json.dumps(results, indent=2),
                show=True,
                show_copy_button=False
            )

    def scheduled_progress_sync(self):
        def scheduledTask():
            self.sync_progress_from_progresssync()

        def main():
            # Get current local time
            currentTime = QTime.currentTime()

            # Set target time to user inputted time
            targetTime = QTime(CONFIG["scheduleSyncHour"], CONFIG["scheduleSyncMinute"])

            # Calculate the time difference
            timeDiff = currentTime.msecsTo(targetTime)
            
            # If target time has already passed today, set the target time for tomorrow
            if timeDiff < 0:
                timeDiff = timeDiff + 86400000

            # Create a QTimer to trigger the task at the desired time
            QTimer.singleShot(timeDiff, scheduledTask)

            # After the task, set another timer for the next day
            QTimer.singleShot(24 * 3600 * 1000, scheduledTask)
        
        main() # Runs scheduled_progress_sync

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
        debug_print('sidecar_paths:', sidecar_paths)

        results = []
        num_success = 0
        num_fail = 0
        num_skip = 0

        for book_uuid, sidecar_path in sidecar_paths.items():
            debug_print('Trying to get sidecar from ', device,
                        ', with sidecar_path: ', sidecar_path)

            # pre-checks before parsing
            if book_uuid is None:
                status = 'skipped, no UUID'
                append_results(results, status, book_uuid, sidecar_path)
                num_skip += 1
                continue

            sidecar_contents = self.get_sidecar(device, sidecar_path)

            debug_print("sidecar_contents:", sidecar_contents)

            if sidecar_contents is GetSidecarStatus.PATH_NOT_FOUND:
                status = ('skipped, sidecar does not exist '
                          '(seems like book is never opened)')
                append_results(results, status, book_uuid, sidecar_path)
                num_skip += 1
                continue

            elif sidecar_contents is GetSidecarStatus.DECODE_FAILED:
                status = 'decoding is failed see debug for more details'
                append_results(results, status, book_uuid, sidecar_path)
                num_fail += 1
                continue

            else:
                debug_print('sidecar_contents is found!')

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
                        debug_print(
                            f'subproperty "{subproperty}" not found in value')
                        value = None
                        break

                if not value:
                    continue

                # Transform value if required
                if 'transform' in column:
                    debug_print('transforming value for ', target)
                    value = column['transform'](value)

                keys_values_to_update[target] = value

            operation_status, result = self.update_metadata(
                book_uuid, keys_values_to_update
            )

            results.append(
                {
                    **result,
                    'book_uuid': book_uuid,
                    'sidecar_path': sidecar_path,
                    # too much data, hard to read for user
                    # 'updated': json.dumps(keys_values_to_update, default=str),
                }
            )

            if operation_status == OperationStatus.PASS:
                num_success += 1
            elif operation_status == OperationStatus.FAIL:
                num_fail += 1
            elif operation_status == OperationStatus.SKIP:
                num_skip += 1

        results_message = (
            f'Total targets found: {len(sidecar_paths)}\n\n'
            f'Metadata sync succeeded for: {num_success}\n'
            f'Metadata sync skipped for: {num_skip}\n'
            f'Metadata sync failed for: {num_fail}\n\n'
        )

        if num_success > 0 and num_fail == 0:
            info_dialog(
                self.gui,
                'Metadata sync finished',
                results_message + f'All looks good!\n\n',
                det_msg=json.dumps(results, indent=2),
                show=True,
                show_copy_button=False
            )
        elif num_fail > 0:
            error_dialog(
                self.gui,
                'Some sync failed',
                results_message + f'There was some error during sync process!\n'
                                  f'Please investigate and report if it looks '
                                  f'like a bug\n\n',
                det_msg=json.dumps(results, indent=2),
                show=True,
                show_copy_button=False
            )
        elif num_success == 0 and num_fail == 0:
            warning_dialog(
                self.gui,
                'No errors but not successful syncs',
                results_message + f'No errors but no successful syncs\n'
                                  f'Do you have book(s) which are ready to be '
                                  f'sync?\n'
                                  f'Please investigate and report if it looks '
                                  f'like a bug\n\n',
                det_msg=json.dumps(results, indent=2),
                show=True,
                show_copy_button=False
            )
        else:
            error_dialog(
                self.gui,
                'Edge case',
                results_message + f'Seems like and bug, please report ASAP\n\n',
                det_msg=json.dumps(results, indent=2),
                show=True,
                show_copy_button=False
            )
