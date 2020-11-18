# KOReader calibre plugin
A calibre plugin to synchronize metadata from KOReader to calibre.

[KOReader](https://koreader.rocks/) creates sidecar files that hold read progress and annotations. This plugin reads the data from those sidecar files and updates calibre’s metadata based on them. It is inspired by [the Kobo Utilities plugin](https://www.mobileread.com/forums/showthread.php?t=215339), that synchronizes reading progress between the original Kobo firmware (“Nickel”) and custom columns in calibre.

Note that at the moment the sync is one-way—from the KOReader device to calibre—and only works for USB devices. Support for smart devices is on [the to-do list](https://git.sr.ht/~harmtemolder/koreader-calibre-plugin/tree/main/TODO).

## Using this plugin
### Download and install
1. Download the latest release from [here](https://git.sr.ht/~harmtemolder/koreader-calibre-plugin/tree/main/releases).
1. Go to your calibre’s “Preferences” > “Plugins” > “Load plugin from file” and point it to the downloaded ZIP file
1. Restart calibre

### Setup
1. Pick and choose the metadata you would like to sync and create the appropriate columns in calibre. These are your options:
  - A “Floating point numbers” column to store the **current percent read**, with “Format for numbers” set to `{:.0%}`.
  - A regular “Text” column to store the **location you last stopped reading at**.
  - A “Rating” column to store your **rating** of the book, as entered on the book’s status page.
  - A “Long text” column to store your **review** of the book, as entered on the book’s status page.
  - A regular “Text” column to store the **reading status** of the book, as entered on the book status page (“Finished”, “Reading”, “On hold”).
  - A “Date” column to store the **date on which the book’s status was last modified**. (This is probably the date on which you marked it as read.)
  - A regular “Text” column to store the **MD5 hash** KOReader uses to sync progress to a [**KOReader Sync Server**](https://github.com/koreader/koreader-sync-server#koreader-sync-server). (“Progress sync” in the KOReader app.) This might allow for syncing progress to calibre without having to connect your KOReader device, in the future.
  - A “Long text” column to store the **raw contents of the metadata sidecar**, with “Interpret this column as” set to “Plain text”.
1. Add “KOReader Sync” to “main toolbar when a device is connected”, if it isn’t there already.
1. Right-click the “KOReader Sync” icon and “Configure”.
1. Map the metadata you want to sync to the newly created calibre columns.
1. Click “OK” to save your mapping.
1. From now on just click the “KOReader Sync” icon to sync all mapped metadata for all books on the connected device to calibre.

### Issues
If you encounter any issues with the plugin, please submit them <a href="https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin">here</a>.

## Acknowledgements
- Contains [SirAnthony’s SLPP](https://github.com/SirAnthony/slpp) to parse Lua in Python.
- Some code borrowed from—and heavily inspired by—the great [Kobo Utilities](https://www.mobileread.com/forums/showthread.php?t=215339) calibre plugin.

## Contributing to this plugin
### Notes & Tips
- My first attempt was actually to sync calibre with KOReader’s read progress through the progress sync plugin and a [sync server](https://github.com/koreader/koreader-sync-server). Read [here](https://github.com/koreader/koreader/issues/6399#issuecomment-721826362) why that did not work. This plugin might actually make that possible now by allowing you to store KOReader’s MD5 hash in calibre.
- Right now this plugin only supports KOReader devices connected by USB. Adding support for wirelessly connected devices (using [the calibre plugin](https://github.com/koreader/koreader/tree/master/plugins/calibre.koplugin)) is next on the list. (See [calibre’s repository](https://github.com/kovidgoyal/calibre/tree/master/src/calibre/devices/smart_device_app) for their end of the latter.)
- calibre allows you to auto-connect to a folder device on boot, which greatly speeds up your workflow when testing. You can find this under “Preferences” > “Tweaks”, search for `auto_connect_to_folder`. Point that to the `dummy_device` folder in this repository. (I have included royalty free EPUBs for your and my convenience.)
- I work in PyCharm, which offers a remote debugging server. Follow [these steps](https://harmtemolder.com/calibre-development-in-pycharm/) to set that up. To enable that in this plugin, add `CALIBRE_PYDEVD=1` to your `env`.
-

### Building a release
If you do not have `slpp.py` yet, run:

```shell
make dependencies all
```

Otherwise this is enough:

```shell
make all
```

### Sending in your patches
Contributing patches on sourcehut works through `git send-email`. You can find this repository’s mailing list [here](https://lists.sr.ht/~harmtemolder/koreader-calibre-plugin).

## Changelog
All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1-alpha]: 2020-11-18
- Added support for all possible filetypes
- Added variables to easily enable a dry-run when debugging and remote debugging

## [0.1.0-alpha]: 2020-11-18
### Added
- Everything needed for a first working version of the plugin
- `dummy_device` and `dummy_library` for easy debugging
- `Makefile` to build a plugin release as a ZIP file
- `TODO` to keep to-dos in one place
- `environment.yml`, in case anyone wants to recreate my Conda environment
- This `README.md`

[Unreleased]: https://git.sr.ht/~harmtemolder/koreader-calibre-plugin/tree
[0.1.0-alpha]: https://git.sr.ht/~harmtemolder/koreader-calibre-plugin/tree/bf7a90655c01de3daba27af63d782605db9011a6
[0.1.1-alpha]: https://git.sr.ht/~harmtemolder/koreader-calibre-plugin/tree/c572732406499b0cc7a202a2af68324cfbe2e277
