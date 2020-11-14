#!/usr/bin/env python3

__license__   = 'GNU GPLv3'
__copyright__ = '2020, harmtemolder <mail at harmtemolder.com>'
__docformat__ = 'restructuredtext en'

from functools import partial
import os

from calibre.devices.usbms.driver import debug_print as root_debug_print
from calibre.utils.config import JSONConfig
from PyQt5.Qt import (
    QComboBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QWidget,
    Qt,
)

prefs = JSONConfig(os.path.join('plugins', 'KOReader Sync.json'))
prefs.defaults['hello_world_msg'] = 'Hello, World!'
prefs.defaults['percent_read_column'] = ''
prefs.defaults['sidecar_column'] = ''

module_debug_print = partial(root_debug_print, ' koreader:config:', sep='')

class ConfigWidget(QWidget):  # https://doc.qt.io/qt-5/qwidget.html
    def __init__(self, plugin_action):
        QWidget.__init__(self)
        debug_print = partial(module_debug_print, 'ConfigWidget:__init__:')
        debug_print('ConfigWidget:__init__:start')
        self.action = plugin_action
        layout = QGridLayout()
        self.setLayout(layout)

        # Get available columns per type
        comments_columns = self.get_comments_custom_columns()
        datetime_columns = self.get_datetime_custom_columns()
        float_columns = self.get_float_custom_columns()
        rating_columns = self.get_rating_columns()
        text_columns = self.get_text_custom_columns()

        # Map percent_finished to percent_read
        percent_read_label = QLabel('Percent Read Column:', self)
        percent_read_label.setToolTip(
            'Column used to store the current percent read. It must be of the '
            'type “Floating point numbers”. Leave this blank if you do not '
            'want to store or restore the percentage read.')
        self.percent_read_combo = CustomColumnComboBox(
            self, float_columns, prefs['percent_read_column'])
        percent_read_label.setBuddy(self.percent_read_combo)
        layout.addWidget(percent_read_label, 1, 1, Qt.AlignRight)
        layout.addWidget(self.percent_read_combo, 1, 2)

        # Map entire sidecar
        sidecar_label = QLabel('Raw Sidecar Column:', self)
        sidecar_label.setToolTip(
            'Column used to store the entire contents of the sidecar ('
            'converted to a Python dict). Useful for debugging, but not much '
            'else. It must be of the type “Long text”. Leave this blank if '
            'you do not want to store or restore the sidecar contents.')
        self.sidecar_combo = CustomColumnComboBox(
            self, comments_columns, prefs['sidecar_column'])
        sidecar_label.setBuddy(self.sidecar_combo)
        layout.addWidget(sidecar_label, 2, 1, Qt.AlignRight)
        layout.addWidget(self.sidecar_combo, 2, 2)

        # Hello world message
        hello_world_label = QLabel('Hello world message:', self)
        self.hello_world_input = QLineEdit(self)
        self.hello_world_input.setText(prefs['hello_world_msg'])
        hello_world_label.setBuddy(self.hello_world_input)
        layout.addWidget(hello_world_label, 3, 1)
        layout.addWidget(self.hello_world_input, 4, 1, 1, 2)

        # sync_to_calibre
        sync_to_calibre_button = QPushButton('sync_to_calibre', self)
        sync_to_calibre_button.clicked.connect(self.action.sync_to_calibre)
        layout.addWidget(sync_to_calibre_button, 5, 1, 1, 2, Qt.AlignHCenter)

        # About button
        about_button = QPushButton('About', self)
        about_button.clicked.connect(self.about)
        layout.addWidget(about_button, 6, 1, 1, 2, Qt.AlignHCenter)

    def save_settings(self):
        debug_print = partial(module_debug_print, 'ConfigWidget:save_settings:')
        debug_print('old prefs = ', prefs)
        prefs['percent_read_column'] = self.percent_read_combo.get_selected_column()
        prefs['sidecar_column'] = self.sidecar_combo.get_selected_column()
        prefs['hello_world_msg'] = self.hello_world_input.text()
        debug_print('new prefs = ', prefs)

    def about(self):
        debug_print = partial(module_debug_print, 'ConfigWidget:about:')
        debug_print('start')
        text = get_resources('about.txt').decode('utf-8')
        QMessageBox.about(self, 'About the KOReader Sync plugin', text)

    def get_float_custom_columns(self):
        # "Floating point numbers"
        column_types = ['float']
        return self.get_custom_columns(column_types)

    def get_rating_columns(self):
        column_types = ['rating']
        custom_columns = self.get_custom_columns(column_types)

        # Add original rating column as well
        ratings_column_name = self.action.gui.library_view.model().orig_headers['rating']
        custom_columns['rating'] = {'name': ratings_column_name}

        return custom_columns

    def get_text_custom_columns(self):

        column_types = ['text']
        return self.get_custom_columns(column_types)

    def get_comments_custom_columns(self):
        # "Long text, like comments..."
        column_types = ['comments']
        return self.get_custom_columns(column_types)

    def get_datetime_custom_columns(self):
        # "Date"
        column_types = ['datetime']
        return self.get_custom_columns(column_types)

    def get_custom_columns(self, column_types):
        custom_columns = self.action.gui.library_view.model().custom_columns
        available_columns = {}

        for key, column in custom_columns.items():
            type_ = column['datatype']
            if type_ in column_types and not column['is_multiple']:
                available_columns[key] = column

        return available_columns


class CustomColumnComboBox(QComboBox):
    def __init__(self, parent, custom_columns={}, selected_column=''):
        QComboBox.__init__(self, parent)
        self.populate_combo(custom_columns, selected_column)

    def populate_combo(self, custom_columns, selected_column):
        self.clear()
        self.column_names = ['']
        self.addItem('do not sync')
        selected_idx = 0

        for key in sorted(custom_columns.keys()):
            self.column_names.append(key)
            display_name = '{} ({})'.format(custom_columns[key]['name'], key)
            self.addItem(display_name)
            if key == selected_column:
                selected_idx = len(self.column_names) - 1

        self.setCurrentIndex(selected_idx)

    def get_selected_column(self):
        return self.column_names[self.currentIndex()]
