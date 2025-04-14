#!/usr/bin/env python3

"""Config for KOReader Sync plugin for Calibre."""

import os
import json
from functools import partial

from PyQt5.Qt import (
    QComboBox,
    QCheckBox,
    QGroupBox,
    QPushButton,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QWidget,
    QSpinBox,
    QFrame,
    QDialog,
    Qt,
)

from PyQt5.QtGui import QPixmap
from calibre.constants import numeric_version
from calibre.devices.usbms.driver import debug_print as root_debug_print
from calibre.utils.config import JSONConfig
from calibre_plugins.koreader import clean_bookmarks
from calibre.gui2 import show_restart_warning, error_dialog
from calibre.customize.ui import initialized_plugins
from calibre.customize import PluginInstallationType

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

SUPPORTS_CREATE_CUSTOM_COLUMN = False
try:
    from calibre.gui2.preferences.create_custom_column import CreateNewCustomColumn
    SUPPORTS_CREATE_CUSTOM_COLUMN = True
except ImportError:
    SUPPORTS_CREATE_CUSTOM_COLUMN = False

# List of default 'lookup names' for the custom columns
# CCD = Custom Column Default (lookup name)
SYNC_CCD_LOOKUP_READING_PROGRESS_FLOAT  = '#ko_progfloat'
SYNC_CCD_LOOKUP_READING_PROGRESS_INT    = '#ko_progint'
SYNC_CCD_LOOKUP_LOC                     = '#ko_loc'
SYNC_CCD_LOOKUP_RATING                  = '#ko_rating'
SYNC_CCD_LOOKUP_REVIEW_TEXT             = '#ko_review'
SYNC_CCD_LOOKUP_STATUS_TEXT             = '#ko_status'
SYNC_CCD_LOOKUP_STATUS_YN               = '#ko_statusbool'
SYNC_CCD_LOOKUP_BOOKMARKS               = '#ko_bookmarks'
SYNC_CCD_LOOKUP_MD5                     = '#ko_md5'
SYNC_CCD_LOOKUP_DATE_SYNC               = '#ko_lastsync'
SYNC_CCD_LOOKUP_DATE_MOD                = '#ko_lastmod'
SYNC_CCD_LOOKUP_DATE_STARTED            = '#ko_start'
SYNC_CCD_LOOKUP_DATE_FINISHED           = '#ko_finish'
SYNC_CCD_LOOKUP_RAW_SIDECAR             = '#ko_sidecar'

'''
Each entry in the below dict has the following keys
column_heading: Default custom column heading
datatype: Default custom column datatype (column type)
is_multiple (optional): only for text columns, whether to allow multiple values. True = "Comma separated text..." and False = "Text, column shown in the Tag browser"
description: Default custom column description
config_name: Name of the config item to store the selected column
config_label: Label for the item in the Config UI
config_tool_tip: Tooltip for the item in the Config UI
column_types: list of calibre column types to show in the combo box (int, float, text, comments, rating, datetime, bool)
sidecar_property (optional): Reference to the sidecar_property for use in action.py
transform (optional): lambda expression to be applied in formatting the value
'''
CUSTOM_COLUMN_DEFAULTS = {
    SYNC_CCD_LOOKUP_READING_PROGRESS_FLOAT : { # Does not currently apply formatting {:.0%}
        'column_heading': _("KOReader Precise Progress"),
        'datatype' : 'float',
        'description' : _("Reading progress for the book with decimal precision."),
        'config_name' : 'column_percent_read',
        'config_label' : _('Percent read column (float):'),
        'config_tool_tip' : _('A "Floating point numbers" column to store the current\n'
                'percent read, with "Format for numbers" set to `{:.0%}`.'),
        "column_types": ['float'],
        'sidecar_property': ['percent_finished'],
        'transform': (lambda value: float(value)),
    },
    SYNC_CCD_LOOKUP_READING_PROGRESS_INT : {
        'column_heading': _("KOReader Progress"),
        'datatype' : 'int',
        'description' : _("Reading progress for the book."),
        'config_name' : 'column_percent_read_int',
        'config_label' : _('Percent read column (int):'),
        'config_tool_tip' : _('An "Integers" column to store the current percent read.'),
        "column_types": ['int'],
        'sidecar_property': ['percent_finished'],
        'transform': (lambda value: round(float(value) * 100)),
    },
    SYNC_CCD_LOOKUP_LOC : {
        'column_heading': _("KOReader Last Location"),
        'datatype' : 'text',
        'is_multiple' : False,
        'description' : _("Last location you stopped reading at in the book."),
        'config_name' : 'column_last_read_location',
        'config_label' : _('Last read location column:'),
        'config_tool_tip' : _('A regular "Text" column to store the location you last\n'
                'stopped reading at.'),
        "column_types": ['text'],
        'sidecar_property': ['last_xpointer'],
    },
    SYNC_CCD_LOOKUP_RATING : {
        'column_heading': _("KOReader Rating"),
        'datatype' : 'rating',
        'description' : _("Rating for the book."),
        'config_name' : 'column_rating',
        'config_label' : _('Rating column:'),
        'config_tool_tip' : _('A "Rating" column to store your rating of the book,\n'
               'as entered on the book’s status page.'),
        "column_types": ['rating'],
        'sidecar_property': ['summary', 'rating'],
        'transform': (lambda value: value * 2),  # calibre uses a 10-point scale,
    },
    SYNC_CCD_LOOKUP_REVIEW_TEXT : { # Unsure about Interpret this column as
        'column_heading': _("KOReader Review"),
        'datatype' : 'comments',
        'description' : _("Review of book."),
        'config_name' : 'column_review',
        'config_label' : _('Review column:'),
        'config_tool_tip' : _('A "Long text" column to store your review of the book,\n'
               'as entered on the book’s status page.'),
        "column_types": ['comments'],
        'sidecar_property': ['summary', 'note'],
    },
    SYNC_CCD_LOOKUP_STATUS_TEXT : {
        'column_heading': _("KOReader Book Status"),
        'datatype' : 'text',
        'is_multiple' : False,
        'description' : _("Reading status of the book, either Finished, Reading, or On hold."),
        'config_name' : 'column_status',
        'config_label' : _('Reading status column (text):'),
        'config_tool_tip' : _('A regular "Text" column to store the reading status of the\n'
               'book, as entered on the book status page ("Finished",\n'
               '"Reading", "On hold").'),
        "column_types": ['text'],
        'sidecar_property': ['summary', 'status'],
    },
    SYNC_CCD_LOOKUP_STATUS_YN : {
        'column_heading': _("KOReader Book Status Y/N"),
        'datatype' : 'bool',
        'description' : _("Yes if the book is marked as finished in KOReader, otherwise No."),
        'config_name' : 'column_status_bool',
        'config_label' : _('Reading status column (yes/no):'),
        'config_tool_tip' : _('A "Yes/No" column to store the reading status of the book,\n'
               'as a boolean ("Yes" = "Finished", "No" = everything else).'),
        "column_types": ['bool'],
        'sidecar_property': ['summary', 'status'],
        'transform': (lambda val: bool(val == 'complete')),
    },
    SYNC_CCD_LOOKUP_BOOKMARKS : { # Unsure about Interpret this column as
        'column_heading': _("KOReader Bookmarks"),
        'datatype' : 'comments',
        'description' : _("All the bookmarks and highlights from KOReader."),
        'config_name' : 'column_bookmarks',
        'config_label' : _('Bookmarks column:'),
        'config_tool_tip' : _('A "Long text" column to store your bookmarks and highlights.'),
        "column_types": ['comments'],
        'sidecar_property': ['annotations'],
        'transform': clean_bookmarks,
    },
    SYNC_CCD_LOOKUP_MD5 : {
        'column_heading': _("KOReader MD5"),
        'datatype' : 'text',
        'is_multiple' : False,
        'description' : _("MD5 hash used by KOReader, allowed for ProgressSync Support."),
        'config_name' : 'column_md5',
        'config_label' : _('MD5 hash column:'),
        'config_tool_tip' : _('A regular "Text" column to store the MD5 hash KOReader uses\n'
               'to sync progress to a KOReader Sync Server. ("Progress sync"\n'
               'in the KOReader app.)'),
        "column_types": ['text'],
        'sidecar_property': ['partial_md5_checksum'],
    },
    SYNC_CCD_LOOKUP_DATE_SYNC : {
        'column_heading': _("Date KOReader Synced"),
        'datatype' : 'datetime',
        'description' : _("Date when the book was last synced from KOReader."),
        'config_name' : 'column_date_synced',
        'config_label' : _('Date Synced column:'),
        'config_tool_tip' : _('A "Date" column to store when the last sync was performed.'),
        "column_types": ['datetime'],
        'sidecar_property': ['calculated', 'date_synced'],
    },
    SYNC_CCD_LOOKUP_DATE_MOD : {
        'column_heading': _("Date KOReader Modified"),
        'datatype' : 'datetime',
        'description' : _("Date when the book was last modified in KOReader. Wired sync only."),
        'config_name' : 'column_date_sidecar_modified',
        'config_label' : _('Date Modified column:'),
        'config_tool_tip' : _('A "Date" column to store when the sidecar file was last '
               'modified. Works for wired connection only, wireless will be '
               'always empty'),
        "column_types": ['datetime'],
        'sidecar_property': ['calculated', 'date_sidecar_modified'],
    },
    SYNC_CCD_LOOKUP_DATE_STARTED : {
        'column_heading': _("Date KOReader Started"),
        'datatype' : 'datetime',
        'description' : _("Date when the book was started."),
        'config_name' : 'column_date_book_started',
        'config_label' : _('Date Book Started column:'),
        'config_tool_tip' : _('A "Date" column to store when the book was started. '
               'Will only be set once when synced with reading status.'),
        "column_types": ['datetime'],
        'sidecar_property': ['calculated', 'date_book_started'], #'summary', 'modified'
    },
    SYNC_CCD_LOOKUP_DATE_FINISHED : {
        'column_heading': _("Date KOReader Finished"),
        'datatype' : 'datetime',
        'description' : _("Date when the book was finished."),
        'config_name' : 'column_date_book_finished',
        'config_label' : _('Date Book Finished column:'),
        'config_tool_tip' : _('A "Date" column to store when the book was finished. '
               'Will only be set once when synced with finished status.'),
        "column_types": ['datetime'],
        'sidecar_property': ['calculated', 'date_book_finished'],
    },
    SYNC_CCD_LOOKUP_RAW_SIDECAR : { # Unsure about Interpret this column as
        'column_heading': _("KOReader Raw Sidecar"),
        'datatype' : 'comments',
        'description' : _("Raw sidecar data directly from KOReader. Allows sync to KOReader, also serves as a backup."),
        'config_name' : 'column_sidecar',
        'config_label' : _('Raw sidecar column:'),
        'config_tool_tip' : _('A "Long text" column to store the contents of the\n'
               'metadata sidecar as JSON, with "Interpret this column as" set to\n'
               '"Plain text". This is required to sync metadata back to KOReader sidecars.'),
        "column_types": ['comments'],
        'sidecar_property': [],  # `[]` gives the entire sidecar dict
        'transform': (lambda d: json.dumps(
            {k: d[k] for k in d if k != 'calculated'},
            skipkeys=True,
            indent=2,
            default=str
        )),
    },
}

CHECKBOXES = { # Each entry in the below dict is keyed with config_name
    'checkbox_sync_if_more_recent': {
        'config_label': 'Sync only if changes are more recent',
        'config_tool_tip': 'Sync book only if the metadata is more recent. Requires\n'
                '"Date Modified Column" or "Percent read column" to be synced',
    },
    'checkbox_no_sync_if_finished': {
        'config_label': 'No sync if book has already been finished',
        'config_tool_tip': 'Do not sync book if it has already been finished. Requires\n'
                '"Percent read column" or "Reading status column" to be synced',
    },
    'checkbox_enable_automatic_sync': {
        'config_label': 'Automatic Sync on device connection',
        'config_tool_tip': 'Sync from KOReader automatically on device connection. \n'
                'Restart calibre to apply this setting',
    },
    'checkbox_enable_scheduled_progressync': {
        'config_label': 'Enable Daily ProgressSync',
        'config_tool_tip': 'Enable daily sync of reading progress and location using \n'
        'KOReader\'s ProgressSync server.',
    },
}

CONFIG = JSONConfig(os.path.join('plugins', 'KOReader Sync.json'))
for this_column in CUSTOM_COLUMN_DEFAULTS.values():
    CONFIG.defaults[this_column['config_name']] = ''
for this_checkbox in CHECKBOXES:
    CONFIG.defaults[this_checkbox] = False
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
        self.must_restart = False

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
        self._get_create_new_custom_column_instance = None
        self.sync_custom_columns = {}
        bottom_options_layout = QHBoxLayout()
        layout.addLayout(bottom_options_layout)
        columns_group_box = QGroupBox(_('Synchronisable Custom Columns:'), self)
        bottom_options_layout.addWidget(columns_group_box)
        columns_group_box_layout = QHBoxLayout()
        columns_group_box.setLayout(columns_group_box_layout)
        columns_group_box_layout2 = QFormLayout()
        columns_group_box_layout.addLayout(columns_group_box_layout2)
        columns_group_box_layout.addStretch()

        for columnName, metadata in CUSTOM_COLUMN_DEFAULTS.items():
            self.sync_custom_columns[columnName] = {'current_columns': self.get_custom_columns(metadata['column_types'])}
            self._column_combo = self.create_custom_column_controls(columns_group_box_layout2, columnName)
            metadata['comboBox'] = self._column_combo
            self._column_combo.populate_combo(
                self.sync_custom_columns[columnName]['current_columns'],
                CONFIG[metadata['config_name']]
                )

        # Add custom checkboxes
        layout.addLayout(self.add_checkbox('checkbox_sync_if_more_recent'))
        layout.addLayout(self.add_checkbox('checkbox_no_sync_if_finished'))

        layout.addLayout(self.add_checkbox('checkbox_enable_automatic_sync'))

        # Progress Sync Section
        layout.addWidget(self.create_separator())
        ps_header_label = QLabel(
            "This plugin supports use of KOReader's built-in ProgressSync server to update reading progress and location without the device connected. "
            "You must have an MD5 column mapped and use Binary matching in KOReader's ProgressSync Settings (default).\n"
            "You also need a reading progress column and status text column.\n"
            "This functionality can optionally be scheduled into a daily sync from within calibre. "
            "Enter scheduled time in military time, default is 4 AM local time. You must restart calibre after making changes to scheduled sync settings. "
        )
        ps_header_label.setWordWrap(True)
        layout.addWidget(ps_header_label)

        # Add scheduled sync options
        scheduled_sync_layout = QHBoxLayout()
        scheduled_sync_layout.setAlignment(Qt.AlignLeft)
        scheduled_sync_layout.addLayout(self.add_checkbox('checkbox_enable_scheduled_progressync'))
        scheduled_sync_layout.addWidget(QLabel('Scheduled Time:'))
        self.schedule_hour_input = QSpinBox()
        self.schedule_hour_input.setRange(0, 23)
        self.schedule_hour_input.setValue(CONFIG['scheduleSyncHour'])
        self.schedule_hour_input.setSuffix('h')
        self.schedule_hour_input.wheelEvent = lambda event: event.ignore()
        scheduled_sync_layout.addWidget(self.schedule_hour_input)
        scheduled_sync_layout.addWidget(QLabel(':'))
        self.schedule_minute_input = QSpinBox()
        self.schedule_minute_input.setRange(0, 59)
        self.schedule_minute_input.setValue(CONFIG['scheduleSyncMinute'])
        self.schedule_minute_input.setSuffix('m')
        self.schedule_minute_input.wheelEvent = lambda event: event.ignore()
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

        # Check relevant settings for changes in order to show restart warning
        needRestart = ( self.must_restart or # Custom Column Addition
            CONFIG['checkbox_enable_automatic_sync'] != (CHECKBOXES['checkbox_enable_automatic_sync']['checkbox'].checkState() == Qt.Checked) or
            CONFIG['checkbox_enable_scheduled_progressync'] != (CHECKBOXES['checkbox_enable_scheduled_progressync']['checkbox'].checkState() == Qt.Checked) or
            CONFIG['scheduleSyncHour'] != self.schedule_hour_input.value() or
            CONFIG['scheduleSyncMinute'] != self.schedule_minute_input.value()
        )
        
        # Save Column Settings
        for values in CUSTOM_COLUMN_DEFAULTS.values():
            CONFIG[values['config_name']] = values['comboBox'].get_selected_column()

        # Save Checkbox Settings
        for config_name in CHECKBOXES:
            CONFIG[config_name] = CHECKBOXES[config_name]['checkbox'].checkState() == Qt.Checked
        
        # Save Scheduled ProgressSync Settings
        CONFIG['scheduleSyncHour'] = self.schedule_hour_input.value()
        CONFIG['scheduleSyncMinute'] = self.schedule_minute_input.value()
        # NOTE: Server/Credentials are saved by the ProgressSyncPopup

        debug_print('new CONFIG = ', CONFIG)
        if needRestart and show_restart_warning('Changes have been made that require a restart to take effect. \n Restart now?'):
            self.action.gui.quit(restart=True)

    def add_checkbox(self, checkboxKey):
        layout = QHBoxLayout()
        checkboxMeta = CHECKBOXES[checkboxKey]
        checkbox = QCheckBox()
        checkbox.setCheckState(Qt.Checked if CONFIG[checkboxKey] else Qt.Unchecked)
        label = QLabel(checkboxMeta['config_label'])
        label.setToolTip(checkboxMeta['config_tool_tip'])
        label.setBuddy(checkbox)
        label.mousePressEvent = lambda event, checkbox=checkbox: checkbox.toggle()
        layout.addWidget(checkbox)
        layout.addWidget(label)
        layout.addStretch()
        CHECKBOXES[checkboxKey]['checkbox'] = checkbox
        return layout

    def create_custom_column_controls(self, columns_group_box_layout, custom_col_name, min_width=300):
        current_Location_label = QLabel(CUSTOM_COLUMN_DEFAULTS[custom_col_name]['config_label'], self)
        current_Location_label.setToolTip(CUSTOM_COLUMN_DEFAULTS[custom_col_name]['config_tool_tip'])
        create_column_callback=partial(self.create_custom_column, custom_col_name) if SUPPORTS_CREATE_CUSTOM_COLUMN else None
        avail_columns = self.sync_custom_columns[custom_col_name]['current_columns']
        custom_column_combo = CustomColumnComboBox(self, avail_columns, create_column_callback=create_column_callback)
        custom_column_combo.setMinimumWidth(min_width)
        current_Location_label.setBuddy(custom_column_combo)
        columns_group_box_layout.addRow(current_Location_label, custom_column_combo)
        self.sync_custom_columns[custom_col_name]['combo_box'] = custom_column_combo
        return custom_column_combo

    def create_custom_column(self, lookup_name=None):
        display_params = {
            'description': CUSTOM_COLUMN_DEFAULTS[lookup_name]['description']
        }
        datatype = CUSTOM_COLUMN_DEFAULTS[lookup_name]['datatype']
        column_heading  = CUSTOM_COLUMN_DEFAULTS[lookup_name]['column_heading']
        is_multiple = CUSTOM_COLUMN_DEFAULTS[lookup_name].get('is_multiple', False)

        new_lookup_name = lookup_name

        create_new_custom_column_instance = self.get_create_new_custom_column_instance
        result = create_new_custom_column_instance.create_column(new_lookup_name, column_heading, datatype, is_multiple, display=display_params, generate_unused_lookup_name=True, freeze_lookup_name=False)
        if result[0] == CreateNewCustomColumn.Result.COLUMN_ADDED:
            self.sync_custom_columns[lookup_name]['current_columns'][result[1]] = {'name': column_heading}
            self.sync_custom_columns[lookup_name]['combo_box'].populate_combo(
                self.sync_custom_columns[lookup_name]['current_columns'], 
                result[1]
                )
            self.must_restart = True
            return True
        return False

    @property
    def get_create_new_custom_column_instance(self):
        if self._get_create_new_custom_column_instance is None and SUPPORTS_CREATE_CUSTOM_COLUMN:
            self._get_create_new_custom_column_instance = CreateNewCustomColumn(self.action.gui)
        return self._get_create_new_custom_column_instance

    def get_custom_columns(self, column_types):
        if SUPPORTS_CREATE_CUSTOM_COLUMN:
            custom_columns = self.get_create_new_custom_column_instance.current_columns()
        else:
            custom_columns = self.action.gui.library_view.model().custom_columns
        available_columns = {}
        for key, column in custom_columns.items():
            typ = column['datatype']
            if typ in column_types:
                available_columns[key] = column
        if 'rating' in column_types: # Add rating columns if requested
            ratings_column_name = self.action.gui.library_view.model().orig_headers['rating']
            available_columns['rating'] = {'name': ratings_column_name}

        return available_columns
    
    def create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        return separator

class ProgressSyncPopup(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
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
            'Enter any custom server or leave the default filled in.\n'
            'Enter your username and password. Then click log in, this does not validate your account so make sure you enter the correct info.\n'
            'Make sure you have one or more of the following columns set up: column_percent_read, column_percent_read_int, column_last_read_location\n'
            'You must have a percent read (int or float) and status text column.',
            self
        )
        self.note_label.setWordWrap(True)
        layout.addWidget(self.note_label)

        self.login_button = QPushButton('Log In', self)
        self.login_button.clicked.connect(self.save_progress_sync_settings)
        layout.addWidget(self.login_button)

    def save_progress_sync_settings(self):
        CONFIG['progress_sync_url'] = self.url_input.text()
        CONFIG['progress_sync_username'] = self.username_input.text()
        CONFIG['progress_sync_password'] = self.hash_password(self.password_input.text())
        self.accept()

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

class CustomColumnComboBox(QComboBox):
    CREATE_NEW_COLUMN_ITEM = _("Create new column")

    def __init__(self, parent, custom_columns={}, selected_column='', create_column_callback=None):
        super(CustomColumnComboBox, self).__init__(parent)
        self.create_column_callback = create_column_callback
        self.current_index = 0
        self.initial_items=['do not sync']
        if create_column_callback is not None:
            self.currentTextChanged.connect(self.current_text_changed)
        self.populate_combo(custom_columns, selected_column)

    def populate_combo(self, custom_columns, selected_column, show_lookup_name=True):
        self.clear()
        self.column_names = []
        selected_idx = 0

        if isinstance(self.initial_items, dict):
            for key in sorted(self.initial_items.keys()):
                self.column_names.append(key)
                display_name = self.initial_items[key]
                self.addItem(display_name)
                if key == selected_column:
                    selected_idx = len(self.column_names) - 1
        else:
            for display_name in self.initial_items:
                self.column_names.append(display_name)
                self.addItem(display_name)
                if display_name == selected_column:
                    selected_idx = len(self.column_names) - 1

        for key in sorted(custom_columns.keys()):
            self.column_names.append(key)
            display_name = '%s (%s)'%(key, custom_columns[key]['name']) if show_lookup_name else custom_columns[key]['name']
            self.addItem(display_name)
            if key == selected_column:
                selected_idx = len(self.column_names) - 1
        
        if self.create_column_callback is not None:
            self.addItem(self.CREATE_NEW_COLUMN_ITEM)
            self.column_names.append(self.CREATE_NEW_COLUMN_ITEM)

        self.setCurrentIndex(selected_idx)

    def get_selected_column(self):
        selected_column = self.column_names[self.currentIndex()]
        if selected_column == self.CREATE_NEW_COLUMN_ITEM:
            selected_column = ''
        if selected_column == 'do not sync':
            selected_column = ''
        return selected_column

    def current_text_changed(self, new_text):
        if new_text == self.CREATE_NEW_COLUMN_ITEM:
            result = self.create_column_callback()
            if not result:
                self.setCurrentIndex(self.current_index)
        else:
            self.current_index = self.currentIndex()
    
    def wheelEvent(self, event): # Prevents the mouse wheel from changing the selected item
        event.ignore()