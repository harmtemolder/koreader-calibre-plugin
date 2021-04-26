# KOReader calibre plugin

A calibre plugin to synchronize metadata from KOReader to calibre.

[KOReader](https://koreader.rocks/) creates sidecar files that hold read progress and annotations. This plugin reads the data from those sidecar files and updates calibre's metadata based on them. It is inspired by [the Kobo Utilities plugin](https://www.mobileread.com/forums/showthread.php?t=215339), that synchronizes reading progress between the original Kobo firmware (“Nickel”) and custom columns in calibre.

Note that at the moment the sync is one-way—from the KOReader device to calibre—and only works for USB and [wireless](https://github.com/koreader/koreader/wiki/Calibre-wireless-connection) devices. For the latter, you'll need [KOReader 2021.04 or newer](https://github.com/koreader/koreader/releases).

Releases will also be uploaded to [this plugin thread on the MobileRead Forums](https://www.mobileread.com/forums/showthread.php?p=4060141). If you are on there as well, please let me know what you think of the plugin in that thread.

## Using this plugin

### Download and install

1. Go to your calibre's “Preferences” > “Plugins” > “Get new plugins” and search for “KOReader Sync”
2. Click “Install”
3. Restart calibre

#### Alternatively

1. Download the latest release from [here](https://git.sr.ht/~harmtemolder/koreader-calibre-plugin/tree/main/releases).
2. Go to your calibre's “Preferences” > “Plugins” > “Load plugin from file” and point it to the downloaded ZIP file
3. Restart calibre

### Setup

1. Pick and choose the metadata you would like to sync and create the appropriate columns in calibre. These are your options:
    - A “Floating point numbers” column to store the **current percent read**, with “Format for numbers” set to `{:.0%}`.
    - An “Integers” column to store the **current percent read**.
    - A regular “Text” column to store the **location you last stopped reading at**.
    - A “Rating” column to store your **rating** of the book, as entered on the book's status page.
    - A “Long text” column to store your **review** of the book, as entered on the book's status page.
    - A “Long text” column to store your **bookmarks and highlights** of the book, with “Interpret this column as” set to “Plain text formatted using markdown”. (Highlights are an unordered list with their metadata in an HTML comment.)
    - A regular “Text” column to store the **reading status** of the book, as entered on the book status page (“Finished”, “Reading”, “On hold”).
    - A “Date” column to store the **date on which the book's status was last modified**. (This is probably the date on which you marked it as read.)
    - A regular “Text” column to store the **MD5 hash** KOReader uses to sync progress to a [**KOReader Sync Server**](https://github.com/koreader/koreader-sync-server#koreader-sync-server). (“Progress sync” in the KOReader app.) This might allow for syncing progress to calibre without having to connect your KOReader device, in the future.
    - A “Long text” column to store the **raw contents of the metadata sidecar**, with “Interpret this column as” set to “Plain text”.
10. Add “KOReader Sync” to “main toolbar when a device is connected”, if it isn't there already.
11. Right-click the “KOReader Sync” icon and “Configure”.
12. Map the metadata you want to sync to the newly created calibre columns.
13. Click “OK” to save your mapping.
14. From now on just click the “KOReader Sync” icon to sync all mapped metadata for all books on the connected device to calibre.

### Things to consider

- The plugin overwrites existing metadata without asking. That usually isn’t a problem, because you will probably only add to KOReader’s metadata. But be aware that you might lose data in calibre if you’re not careful.

### Issues

If you encounter any issues with the plugin, please submit them [here](https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin).

## Acknowledgements

- Multiple tweaks and bug fixes by [Glen Sawyer](https://git.sr.ht/~snelg)
- Contains [SirAnthony's SLPP](https://github.com/SirAnthony/slpp) to parse Lua in Python.
- Some code borrowed from--and heavily inspired by--the great [Kobo Utilities](https://www.mobileread.com/forums/showthread.php?t=215339) calibre plugin.

## Contributing to this plugin

### Notes & Tips

- My first attempt was actually to sync calibre with KOReader's read progress through the progress sync plugin and a [sync server](https://github.com/koreader/koreader-sync-server). Read [here](https://github.com/koreader/koreader/issues/6399#issuecomment-721826362) why that did not work. This plugin might actually make that possible now by allowing you to store KOReader's MD5 hash in calibre...
- calibre allows you to auto-connect to a folder device on boot, which greatly speeds up your workflow when testing. You can find this under “Preferences” > “Tweaks”, search for `auto_connect_to_folder`. Point that to the `dummy_device` folder in this repository. (I have included royalty free EPUBs for your and my convenience.)
- If you're testing and don't actually want to update any metadata, set `DRY_RUN` to `True` in `__init__.py`.
- I work in PyCharm, which offers a remote debugging server. Follow [these steps](https://harmtemolder.com/calibre-development-in-pycharm/) to set that up. To enable that in this plugin, set `PYDEVD` to `True` in `__init__.py`.You might need to change `sys.path.append` in `action.py`.

### Downloading dependencies

```shell
make dependencies
```

### Testing in calibre

Make sure you have the dependencies. Then:

```shell
make dev
```

### Building a release

Make sure you have the dependencies and have set the correct version number in `Makefile`. Then:

```shell
make
```

### Sending in your patches

Contributing patches on sourcehut works through `git send-email`. You can find this repository's mailing list [here](https://lists.sr.ht/~harmtemolder/koreader-calibre-plugin).

## Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1-alpha] - 2021-04-26

### Added

- An extra column for read progress as integer (because that’s what [the Goodreads Sync plugin](https://www.mobileread.com/forums/showthread.php?t=123281) expects)

## [0.2.0-alpha] - 2021-04-24

### Added

- Support for highlights and bookmarks
- Counts to post-sync alerts
- An `.editorconfig` and `.pylintrc` to define code layout

### Changed

- `README.md` to reflect current state of development

## [0.1.4-alpha] - 2021-04-11

### Fixed

- Multiple tweaks and bug fixes by [Glen Sawyer](https://git.sr.ht/~snelg)

## [0.1.3-alpha] - 2021-04-04

### Added

- Support for `SMART_DEVICE_APP` devices, i.e. [KOReader's wireless connnection](https://github.com/koreader/koreader/wiki/Calibre-wireless-connection)

## [0.1.2-alpha] - 2020-11-21

### Added

- Support for `KOBO` and `KOBOTOUCH` devices

## [0.1.1-alpha] - 2020-11-18

### Added

- Support for all possible filetypes
- Variables to easily enable a dry-run when debugging and remote debugging

## [0.1.0-alpha] - 2020-11-18

### Added

- Everything needed for a first working version of the plugin
- `dummy_device` and `dummy_library` for easy debugging
- `Makefile` to build a plugin release as a ZIP file
- `TODO` to keep to-dos in one place
- `environment.yml`, in case anyone wants to recreate my Conda environment
- This `README.md`

[0.1.0-alpha]: https://git.sr.ht/~harmtemolder/koreader-calibre-plugin/tree/main/item/releases/KOReader%20Sync%20v0.1.0-alpha.zip
[0.1.1-alpha]: https://git.sr.ht/~harmtemolder/koreader-calibre-plugin/tree/main/item/releases/KOReader%20Sync%20v0.1.1-alpha.zip
[0.1.2-alpha]: https://git.sr.ht/~harmtemolder/koreader-calibre-plugin/tree/main/item/releases/KOReader%20Sync%20v0.1.2-alpha.zip
[0.1.3-alpha]: https://git.sr.ht/~harmtemolder/koreader-calibre-plugin/tree/main/item/releases/KOReader%20Sync%20v0.1.3-alpha.zip
[0.1.4-alpha]: https://git.sr.ht/~harmtemolder/koreader-calibre-plugin/tree/main/item/releases/KOReader%20Sync%20v0.1.4-alpha.zip
[0.2.0-alpha]: https://git.sr.ht/~harmtemolder/koreader-calibre-plugin/tree/main/item/releases/KOReader%20Sync%20v0.2.0-alpha.zip
[unreleased]: https://git.sr.ht/~harmtemolder/koreader-calibre-plugin/tree
