#!/usr/bin/env python3

"""Config for KOReader Sync plugin for Calibre."""

import math
import os
import json
from functools import partial

from PyQt5.Qt import (
    QComboBox,
    QCheckBox,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QSpinBox,
    QFrame,
    Qt,
)

from PyQt5.QtGui import QPixmap
from calibre.constants import numeric_version
from calibre.devices.usbms.driver import debug_print as root_debug_print
from calibre.utils.config import JSONConfig
from calibre_plugins.koreader import clean_bookmarks

__license__ = 'GNU GPLv3'
__copyright__ = '2021, harmtemolder <mail at harmtemolder.com>'
__modified_by__ = 'kyxap kyxappp@gmail.com'
__modification_date__ = '2024'
__docformat__ = 'restructuredtext en'

SUPPORTED_DEVICES = [
    'FOLDER_DEVICE',
    'KINDLE2',
    'KOBO',
    'KOBOTOUCH',
    'KOBOTOUCHEXTENDED',
    'POCKETBOOK622',
    'POCKETBOOK626',
    'SMART_DEVICE_APP',
    'TOLINO',
    'USER_DEFINED',
    'POCKETBOOK632',
]
UNSUPPORTED_DEVICES = [
    'MTP_DEVICE',
]

COLUMNS = [{
    'name': 'column_percent_read',
    'label': 'Percent read column (float):',
    'tooltip': 'A "Floating point numbers" column to store the current\n'
               'percent read, with "Format for numbers" set to `{:.0%}`.',
    'type': 'float',
    'sidecar_property': ['percent_finished'],
    'transform': (lambda value: float(value))
}, {
    'name': 'column_percent_read_int',
    'label': 'Percent read column (int):',
    'tooltip': 'An "Integers" column to store the current percent read.',
    'type': 'int',
    'sidecar_property': ['percent_finished'],
    'transform': (lambda value: math.floor(float(value) * 100))
}, {
    'name': 'column_last_read_location',
    'label': 'Last read location column:',
    'tooltip': 'A regular "Text" column to store the location you last\n'
               'stopped reading at.',
    'type': 'text',
    'sidecar_property': ['last_xpointer'],
}, {
    'name': 'column_rating',
    'label': 'Rating column:',
    'tooltip': 'A "Rating" column to store your rating of the book,\n'
               'as entered on the book’s status page.',
    'type': 'rating',
    'sidecar_property': ['summary', 'rating'],
    'transform': (lambda value: value * 2),  # calibre uses a 10-point scale
}, {
    'name': 'column_review',
    'label': 'Review column:',
    'tooltip': 'A "Long text" column to store your review of the book,\n'
               'as entered on the book’s status page.',
    'type': 'comments',
    'sidecar_property': ['summary', 'note'],
}, {
    'name': 'column_status',
    'label': 'Reading status column (text):',
    'tooltip': 'A regular "Text" column to store the reading status of the\n'
               'book, as entered on the book status page ("Finished",\n'
               '"Reading", "On hold").',
    'type': 'text',
    'sidecar_property': ['summary', 'status'],
}, {
    'name': 'column_status_bool',
    'label': 'Reading status column (yes/no):',
    'tooltip': 'A "Yes/No" column to store the reading status of the book,\n'
               'as a boolean ("Yes" = "Finished", "No" = everything else).',
    'type': 'bool',
    'sidecar_property': ['summary', 'status'],
    'transform': (lambda val: bool(val == 'complete')),
}, {
    'name': 'column_bookmarks',
    'label': 'Bookmarks column',
    'tooltip': 'A "Long text" column to store your bookmarks and\n'
               'highlights.',
    'type': 'comments',
    'sidecar_property': ['annotations'],
    'transform': clean_bookmarks,
}, {
    'name': 'column_md5',
    'label': 'MD5 hash column:',
    'tooltip': 'A regular "Text" column to store the MD5 hash KOReader uses\n'
               'to sync progress to a KOReader Sync Server. ("Progress sync"\n'
               'in the KOReader app.) This might allow for syncing progress\n'
               'to calibre without having to connect your KOReader device,\n'
               'in the future.',
    'type': 'text',
    'sidecar_property': ['partial_md5_checksum'],
}, {
    'name': 'column_date_synced',
    'label': 'Date Synced column:',
    'tooltip': 'A "Date" column to store when the last sync was performed.',
    'type': 'datetime',
    'sidecar_property': ['calculated', 'date_synced'],
}, {
    'name': 'column_date_sidecar_modified',
    'label': 'Date Modified column:',
    'tooltip': 'A "Date" column to store when the sidecar file was last '
               'modified. Works for wired connection only, wireless will be '
               'always empty',
    'type': 'datetime',
    'sidecar_property': ['calculated', ''],
}, {
    'name': 'column_sidecar',
    'label': 'Raw sidecar column:',
    'tooltip': 'A "Long text" column to store the contents of the\n'
               'metadata sidecar as JSON, with "Interpret this column as" set to\n'
               '"Plain text". This is required to sync metadata back to KOReader sidecars.',
    'type': 'comments',
    'sidecar_property': [],  # `[]` gives the entire sidecar dict
    'transform': (lambda d: json.dumps(
        {k: d[k] for k in d if k != 'calculated'},
        skipkeys=True,
        indent=2,
        default=str
    )),
}]
CHECKBOXES = [{
    'name': 'checkbox_sync_if_more_recent',
    'addToLayout': True,
    'label': 'Sync only if changes are more recent:',
    'tooltip': 'Sync book only if the metadata is more recent. Requires\n'
               '"Date Modified Column" or "Percent read column" to be synced',
}, {
    'name': 'checkbox_no_sync_if_finished',
    'addToLayout': True,
    'label': 'No sync if book has already been finished:',
    'tooltip': 'Do not sync book if it has already been finished. Requires\n'
               '"Percent read column" or "Reading status column" to be synced',
}, {
    'name': 'checkbox_enable_automatic_sync',
    'addToLayout': True,
    'label': 'Automatic Sync on device connection:',
    'tooltip': 'Sync from KOReader automatically on device connection. \n'
               'Restart calibre to apply this setting',
}, {
    'name': 'checkbox_enable_scheduled_progressync',
    'addToLayout': False,
    'label': 'Enable Daily ProgressSync:',
    'tooltip': 'Enable daily sync of reading progress and location using KOReader\'s ProgressSync server.',
}]

CONFIG = JSONConfig(os.path.join('plugins', 'KOReader Sync.json'))
for this_column in COLUMNS:
    CONFIG.defaults[this_column['name']] = ''
for this_checkbox in CHECKBOXES:
    CONFIG.defaults[this_checkbox['name']] = False
CONFIG.defaults['progress_sync_url'] = 'https://sync.koreader.rocks:443'
CONFIG.defaults['progress_sync_username'] = ''
CONFIG.defaults['progress_sync_password'] = ''
CONFIG.defaults['scheduleSyncHour'] = 4
CONFIG.defaults['scheduleSyncMinute'] = 0

if numeric_version >= (5, 5, 0):
    module_debug_print = partial(root_debug_print, ' koreader:config:', sep='')
else:
    module_debug_print = partial(root_debug_print, 'koreader:config:')


class ConfigWidget(QWidget):  # https://doc.qt.io/qt-5/qwidget.html
    def __init__(self, plugin_action):
        QWidget.__init__(self)
        debug_print = partial(module_debug_print, 'ConfigWidget:__init__:')
        debug_print('start')
        self.action = plugin_action

        # Set up main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add icon and title
        title_layout = TitleLayout(
            self,
            'images/icon.png',
            f'Configure {self.action.version}',
        )
        layout.addLayout(title_layout)

        # Add custom column dropdowns
        custom_columns_layout = CustomColumnsLayout(self)
        layout.addLayout(custom_columns_layout)

        # Add custom checkboxes
        custom_checkbox_layout = CustomCheckboxLayout(self)
        layout.addLayout(custom_checkbox_layout)

        # Add separator and header
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        header_label = QLabel(
            "This plugin supports use of KOReader's built-in ProgressSync server to update reading progress and location without the device connected. "
            "You must have an MD5 column mapped and use Binary matching in KOReader's ProgressSync Settings (default).\n"
            "This functionality can optionally be scheduled into a daily sync from within calibre. "
            "Enter scheduled time in military time, default is 4 AM local time. You must restart calibre after making changes to scheduled sync settings. "
        )
        header_label.setWordWrap(True)
        layout.addWidget(header_label)

        # Add scheduled sync options
        scheduled_sync_layout = QHBoxLayout()
        scheduled_sync_layout.setAlignment(Qt.AlignLeft)
        self.enable_scheduled_sync_checkbox = QCheckBox('Enable Daily ProgressSync')
        self.enable_scheduled_sync_checkbox.setCheckState(Qt.Checked if CONFIG['checkbox_enable_scheduled_progressync'] else Qt.Unchecked)
        scheduled_sync_layout.addWidget(self.enable_scheduled_sync_checkbox)

        scheduled_sync_layout.addWidget(QLabel('Scheduled Time:'))

        self.schedule_hour_input = QSpinBox()
        self.schedule_hour_input.setRange(0, 23)
        self.schedule_hour_input.setValue(CONFIG['scheduleSyncHour'])
        self.schedule_hour_input.setSuffix('h')
        scheduled_sync_layout.addWidget(self.schedule_hour_input)

        scheduled_sync_layout.addWidget(QLabel(':'))

        self.schedule_minute_input = QSpinBox()
        self.schedule_minute_input.setRange(0, 59)
        self.schedule_minute_input.setValue(CONFIG['scheduleSyncMinute'])
        self.schedule_minute_input.setSuffix('m')
        scheduled_sync_layout.addWidget(self.schedule_minute_input)

        layout.addLayout(scheduled_sync_layout)

        # Add ProgressSync Account button
        progress_sync_button = QPushButton('Add ProgressSync Account', self)
        progress_sync_button.clicked.connect(self.show_progress_sync_popup)
        layout.addWidget(progress_sync_button)

    def show_progress_sync_popup(self):
        self.progress_sync_popup = ProgressSyncPopup(self)
        self.progress_sync_popup.show()

    def save_settings(self):
        debug_print = partial(module_debug_print,
                              'ConfigWidget:save_settings:')
        debug_print('old CONFIG = ', CONFIG)

        for column in COLUMNS:
            CONFIG[column['name']] = column['combo'].get_selected_column()

        for checkbox in CHECKBOXES:
            CONFIG[checkbox['name']] = checkbox['checkbox'].checkState() == Qt.Checked

        CONFIG['checkbox_enable_scheduled_progressync'] = self.enable_scheduled_sync_checkbox.checkState() == Qt.Checked
        CONFIG['scheduleSyncHour'] = self.schedule_hour_input.value()
        CONFIG['scheduleSyncMinute'] = self.schedule_minute_input.value()

        debug_print('new CONFIG = ', CONFIG)

class ProgressSyncPopup(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setWindowTitle('Add ProgressSync Account')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.url_label = QLabel('ProgressSync Server URL:', self)
        self.url_input = QLineEdit(self)
        self.url_input.setText(CONFIG['progress_sync_url'])
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        self.username_label = QLabel('Username:', self)
        self.username_input = QLineEdit(self)
        self.username_input.setText(CONFIG['progress_sync_username'])
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel('Password:', self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.note_label = QLabel(
            'Enter any custom server or leave the default filled in. '
            'Enter your username and password. Then click log in, this does not validate your account so make sure you enter the correct info.'
            'Also make sure you have one or more of the following columns set up: column_percent_read, column_percent_read_int, column_last_read_location',
            self
        )
        layout.addWidget(self.note_label)

        self.login_button = QPushButton('Log In', self)
        self.login_button.clicked.connect(self.save_progress_sync_settings)
        layout.addWidget(self.login_button)

    def save_progress_sync_settings(self):
        CONFIG['progress_sync_url'] = self.url_input.text()
        CONFIG['progress_sync_username'] = self.username_input.text()
        CONFIG['progress_sync_password'] = self.hash_password(self.password_input.text())
        self.close()

    def hash_password(self, password):
        import hashlib
        return hashlib.md5(password.encode()).hexdigest()

class TitleLayout(QHBoxLayout):
    """A sub-layout to the main layout used in ConfigWidget that contains an
    icon and title.
    """

    def __init__(self, parent, icon, title):
        QHBoxLayout.__init__(self)

        # Add icon
        icon_label = QLabel(parent)
        pixmap = QPixmap()
        pixmap.loadFromData(get_resources(icon))
        icon_label.setPixmap(pixmap)
        icon_label.setMaximumSize(64, 64)
        icon_label.setScaledContents(True)
        self.addWidget(icon_label)

        # Add title
        title_label = QLabel(f'<h2>{title}</h2>', parent)
        self.addWidget(title_label)

        # Add empty space
        self.addStretch()

        # Add Readme hyperlink
        readme_label = QLabel('<a href="#">Readme</a>', parent)
        readme_label.setTextInteractionFlags(
            Qt.LinksAccessibleByMouse | Qt.LinksAccessibleByKeyboard)
        readme_label.linkActivated.connect(parent.action.show_readme)
        self.addWidget(readme_label)

        # Add About hyperlink
        about_label = QLabel('<a href="#">About</a>', parent)
        about_label.setTextInteractionFlags(
            Qt.LinksAccessibleByMouse | Qt.LinksAccessibleByKeyboard)
        about_label.linkActivated.connect(parent.action.show_about)
        self.addWidget(about_label)


class CustomColumnsLayout(QGridLayout):
    """A sub-layout to the main layout used in ConfigWidget that contains a
    grid of dropdowns for the mapping from KOReader metadata properties to
    calibre’s custom columns.
    """

    def __init__(self, parent):
        QGridLayout.__init__(self)
        self.action = parent.action
        row = 1

        # Get available columns per type
        available_columns = {
            'comments': self.get_custom_columns(['comments']),
            'datetime': self.get_custom_columns(['datetime']),
            'float': self.get_custom_columns(['float']),
            'int': self.get_custom_columns(['int']),
            'rating': self.get_rating_columns(),  # Includes built-in
            'text': self.get_custom_columns(['text']),
            'bool': self.get_custom_columns(['bool']),
        }

        # Add custom column dropdowns
        for column in COLUMNS:
            label = QLabel(column['label'], parent)
            label.setToolTip(column['tooltip'])
            column['combo'] = CustomColumnComboBox(
                parent,
                available_columns[column['type']],
                CONFIG[column['name']])
            label.setBuddy(column['combo'])
            self.addWidget(label, row, 1, Qt.AlignRight)
            self.addWidget(column['combo'], row, 2, 1, 2)
            row += 1

    def get_custom_columns(self, column_types):
        custom_columns = self.action.gui.library_view.model().custom_columns
        available_columns = {}

        for key, column in custom_columns.items():
            type_ = column['datatype']
            if type_ in column_types and not column['is_multiple']:
                available_columns[key] = column

        return available_columns

    def get_rating_columns(self):
        rating_columns = self.get_custom_columns(['rating'])

        # Add built-in rating column as well
        rating_column_name = self.action.gui.library_view.model().orig_headers[
            'rating']
        rating_columns['rating'] = {'name': rating_column_name}

        return rating_columns

class CustomCheckboxLayout(QGridLayout):
    """A sub-layout to the main layout used in ConfigWidget that contains a
    grid of checkboxes for various settings.
    """

    def __init__(self, parent):
        QGridLayout.__init__(self)
        self.action = parent.action
        row = 1

        # Add custom checkboxes
        for checkbox in CHECKBOXES:
            label = QLabel(checkbox['label'], parent)
            label.setToolTip(checkbox['tooltip'])
            checkbox['checkbox'] = QCheckBox()
            checkbox['checkbox'].setCheckState(Qt.Checked if CONFIG[checkbox['name']] else Qt.Unchecked)
            label.setBuddy(checkbox['checkbox'])
            if checkbox['addToLayout']:
                self.addWidget(label, row, 1, Qt.AlignRight)
                self.addWidget(checkbox['checkbox'], row, 2, 1, 2)
                row += 1

class CustomColumnComboBox(QComboBox):
    def __init__(self, parent, custom_columns=None, selected_column=''):
        QComboBox.__init__(self, parent)
        if custom_columns is None:
            custom_columns = {}
        self.populate_combo(custom_columns, selected_column)

    def populate_combo(self, custom_columns, selected_column):
        self.clear()
        self.column_names = ['']
        self.addItem('do not sync')
        selected_idx = 0

        for key in sorted(custom_columns.keys()):
            self.column_names.append(key)
            display_name = f'{custom_columns[key]["name"]} ({key})'
            self.addItem(display_name)
            if key == selected_column:
                selected_idx = len(self.column_names) - 1

        self.setCurrentIndex(selected_idx)

    def get_selected_column(self):
        return self.column_names[self.currentIndex()]
