#!/usr/bin/env python3

import os
from functools import partial

from calibre.constants import DEBUG as _DEBUG  # pylint: disable=no-name-in-module, disable=import-error
from calibre.constants import numeric_version  # pylint: disable=no-name-in-module, disable=import-error
from calibre.customize import InterfaceActionBase  # pylint: disable=no-name-in-module, disable=import-error
from calibre.devices.usbms.driver import debug_print as root_debug_print  # pylint: disable=no-name-in-module, disable=import-error
from calibre.utils.config import JSONConfig  # pylint: disable=no-name-in-module, disable=import-error

__license__ = 'GNU GPLv3'
__copyright__ = '2021, harmtemolder <mail at harmtemolder.com>'
__docformat__ = 'restructuredtext en'

DEBUG = _DEBUG
DRY_RUN = False  # Used during debugging to skip the actual updating of metadata
PYDEVD = True  # Used during debugging to connect to PyCharm’s remote debugging

if numeric_version >= (5, 5, 0):
    module_debug_print = partial(
        root_debug_print,
        ' koreader:__init__:',
        sep=''
        )
else:
    module_debug_print = partial(root_debug_print, 'koreader:__init__:')


class KoreaderSync(InterfaceActionBase):
    name = 'KOReader Sync'
    description = 'Get metadata from a locally connected KOReader device '
    author = 'harmtemolder'
    version = (0, 2, 5)
    minimum_calibre_version = (5, 0, 1)  # Because Python 3
    config = JSONConfig(os.path.join('plugins', 'KOReader Sync.json'))
    actual_plugin = 'calibre_plugins.koreader.action:KoreaderAction'

    def is_customizable(self):
        return True

    def config_widget(self):
        if self.actual_plugin_:
            from calibre_plugins.koreader.config import \
                ConfigWidget  # pylint: disable=import-error, disable=import-outside-toplevel
            return ConfigWidget(self.actual_plugin_)

    def save_settings(self, config_widget):
        config_widget.save_settings()


def clean_bookmarks(input):
    """Transforms KOReader's bookmark metadata into text that can be stored
    in calibre. I assume that all bookmarks have a `notes` attribute, which I
    use as the main text of the bookmark. All other attributes are stored in a
    HTML comment.

    :param input: dict with numbered keys and bookmark dict values
    :return: Markdown-formatted str of the bookmarks
    """
    debug_print = partial(root_debug_print, 'clean_bookmarks:')

    output = ''

    for k in input:
        bookmark = input[k]
        if not 'notes' in bookmark:
            debug_print('bookmark does not have `notes`', bookmark)
            continue

        output += '- {}'.format(bookmark.pop('notes'))

        if len(bookmark) > 0:
            output += ' <!-- '
            for attr in bookmark:
                output += '{}: {}, '.format(
                    attr,
                    bookmark[attr]
                )

            output = output[:-2] + ' -->'

        output += '\n'

    return output.strip()
