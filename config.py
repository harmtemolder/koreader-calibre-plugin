#!/usr/bin/env python

__license__   = 'GPL v3'
__copyright__ = '2020, harmtemolder <mail at harmtemolder.com>'
__docformat__ = 'restructuredtext en'

import os

from PyQt5.Qt import QWidget, QHBoxLayout, QLabel, QLineEdit
from calibre.utils.config import JSONConfig

prefs = JSONConfig(os.path.join('plugins', 'KOReader Sync.json'))
prefs.defaults['hello_world_msg'] = 'Hello, World!'


class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QHBoxLayout()
        self.setLayout(self.l)

        self.label = QLabel('Hello world &message:')
        self.l.addWidget(self.label)

        self.msg = QLineEdit(self)
        self.msg.setText(prefs['hello_world_msg'])
        self.l.addWidget(self.msg)
        self.label.setBuddy(self.msg)

    def save_settings(self):
        prefs['hello_world_msg'] = self.msg.text()
