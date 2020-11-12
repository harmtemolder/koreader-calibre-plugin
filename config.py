#!/usr/bin/env python3

__license__   = 'GNU GPLv3'
__copyright__ = '2020, harmtemolder <mail at harmtemolder.com>'
__docformat__ = 'restructuredtext en'

from functools import partial
import os
import sys

from calibre.devices.usbms.driver import debug_print as _debug_print
from calibre.utils.config import JSONConfig
from PyQt5.Qt import (QWidget, QHBoxLayout, QLabel, QLineEdit, QDialog,
                      QVBoxLayout, QPushButton, QMessageBox)

prefs = JSONConfig(os.path.join('plugins', 'KOReader Sync.json'))
prefs.defaults['hello_world_msg'] = 'Hello, World!'

sys.path.append('/Applications/PyCharm.app/Contents/debug-eggs/pydevd-pycharm.egg')
import pydevd_pycharm

debug_print = partial(_debug_print, ' koreader:config:', sep='')


class ConfigWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        debug_print('ConfigWidget:__init__:start')
        self.l = QHBoxLayout()
        self.setLayout(self.l)

        self.label = QLabel('Hello world &message:')
        self.l.addWidget(self.label)

        self.msg = QLineEdit(self)
        self.msg.setText(prefs['hello_world_msg'])
        self.l.addWidget(self.msg)
        self.label.setBuddy(self.msg)

    def save_settings(self):
        debug_print('ConfigWidget:save_settings:start')
        prefs['hello_world_msg'] = self.msg.text()


class SettingsDialog(QDialog):
    def __init__(self, gui, icon, do_user_config):
        debug_print('SettingsDialog:__init__:start')
        QDialog.__init__(self, gui)
        self.gui = gui
        self.action = gui.iactions['KOReader Sync']
        self.do_user_config = do_user_config

        self.db = gui.current_db

        self.l = QVBoxLayout()
        self.setLayout(self.l)

        self.label = QLabel(prefs['hello_world_msg'])
        self.l.addWidget(self.label)

        self.setWindowTitle('Interface Plugin Demo')
        self.setWindowIcon(icon)

        # About
        self.about_button = QPushButton('About', self)
        self.about_button.clicked.connect(self.about)
        self.l.addWidget(self.about_button)

        # sync_to_calibre
        self.sync_to_calibre_button = QPushButton('sync_to_calibre', self)
        self.sync_to_calibre_button.clicked.connect(self.action.sync_to_calibre)
        self.l.addWidget(self.sync_to_calibre_button)

        # Configure this plugin
        self.conf_button = QPushButton(
            'Configure this plugin', self)
        self.conf_button.clicked.connect(self.config)
        self.l.addWidget(self.conf_button)

        self.resize(self.sizeHint())

    def about(self):
        debug_print('SettingsDialog:about:start')
        pydevd_pycharm.settrace('localhost', port=12345, stdoutToServer=True,stderrToServer=True)

        text = get_resources('about.txt').decode('utf-8')
        QMessageBox.about(
            self,
            'About the KOReader Sync plugin',
            text
        )

    def marked(self):
        debug_print('SettingsDialog:marked:start')
        db = self.db.new_api
        matched_ids = {book_id for book_id in db.all_book_ids() if len(db.formats(book_id)) == 1}

        self.db.set_marked_ids(matched_ids)

        self.gui.search.setEditText('marked:true')
        self.gui.search.do_search()

    def view(self):
        debug_print('SettingsDialog:view:start')
        most_recent = most_recent_id = None
        db = self.db.new_api
        for book_id, timestamp in db.all_field_for('timestamp', db.all_book_ids()).items():
            if most_recent is None or timestamp > most_recent:
                most_recent = timestamp
                most_recent_id = book_id

        if most_recent_id is not None:
            view_plugin = self.gui.iactions['View']
            view_plugin._view_calibre_books([most_recent_id])

    def update_metadata(self):
        debug_print('SettingsDialog:update_metadata:start')
        '''
        Set the metadata in the files in the selected book's record to
        match the current metadata in the database.
        '''
        from calibre.ebooks.metadata.meta import set_metadata
        from calibre.gui2 import error_dialog, info_dialog

        # Get currently selected books
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, 'Cannot update metadata',
                                'No books selected', show=True)
        # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        db = self.db.new_api
        for book_id in ids:
            # Get the current metadata for this book from the db
            mi = db.get_metadata(book_id, get_cover=True, cover_as_data=True)
            fmts = db.formats(book_id)
            if not fmts:
                continue
            for fmt in fmts:
                fmt = fmt.lower()
                # Get a python file object for the format. This will be either
                # an in memory file or a temporary on disk file
                ffile = db.format(book_id, fmt, as_file=True)
                ffile.seek(0)
                # Set metadata in the format
                set_metadata(ffile, mi, fmt)
                ffile.seek(0)
                # Now replace the file in the calibre library with the updated
                # file. We dont use add_format_with_hooks as the hooks were
                # already run when the file was first added to calibre.
                db.add_format(book_id, fmt, ffile, run_hooks=False)

        info_dialog(self, 'Updated files',
                    'Updated the metadata in the files of %d book(s)'%len(ids),
                    show=True)

    def config(self):
        debug_print('SettingsDialog:config:start')
        self.do_user_config(parent=self)
        self.label.setText(prefs['hello_world_msg'])
