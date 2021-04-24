#!/usr/bin/env python3

import os

from calibre.utils.config import JSONConfig  # pylint: disable=no-name-in-module, disable=import-error
from calibre.customize import InterfaceActionBase  # pylint: disable=no-name-in-module, disable=import-error
from calibre.constants import DEBUG as _DEBUG  # pylint: disable=no-name-in-module, disable=import-error

__license__ = 'GNU GPLv3'
__copyright__ = '2021, harmtemolder <mail at harmtemolder.com>'
__docformat__ = 'restructuredtext en'


DEBUG = _DEBUG
DRY_RUN = True  # Used during debugging to skip the actual updating of metadata
PYDEVD = True  # Used during debugging to connect to PyCharm’s remote debugging


class KoreaderSync(InterfaceActionBase):
    name = 'KOReader Sync'
    description = 'Get metadata from a locally connected KOReader device '
    author = 'harmtemolder'
    version = (0, 2, 0)
    minimum_calibre_version = (5, 0, 1)  # Because Python 3
    config = JSONConfig(os.path.join('plugins', 'KOReader Sync.json'))
    actual_plugin = 'calibre_plugins.koreader.action:KoreaderAction'

    def is_customizable(self):
        return True

    def config_widget(self):
        if self.actual_plugin_:
            from calibre_plugins.koreader.config import ConfigWidget  # pylint: disable=import-error, disable=import-outside-toplevel
            return ConfigWidget(self.actual_plugin_)

    def save_settings(self, config_widget):
        config_widget.save_settings()
