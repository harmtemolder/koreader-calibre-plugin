# KOReader calibre plugin

> **Hi,**
>
> **I'm looking for someone who wants to help me maintain this plugin, because I don't use it all that much anymore. Please contact me if you're up for this.**
>
> **Harm**

A calibre plugin to synchronize metadata from KOReader to calibre.

[KOReader](https://koreader.rocks/) creates sidecar files that hold read progress and annotations. This plugin reads the data from those sidecar files and updates calibre's metadata based on them. It is inspired by [the Kobo Utilities plugin](https://www.mobileread.com/forums/showthread.php?t=215339), that synchronizes reading progress between the original Kobo firmware ("Nickel") and custom columns in calibre.

Note that at the moment the sync is primarily one-way—from the KOReader device to calibre, and only works for USB and [wireless](https://github.com/koreader/koreader/wiki/Calibre-wireless-connection) devices. For the latter, you'll need [KOReader 2021.04 or newer](https://github.com/koreader/koreader/releases).

Pushing metadata from calibre to KOReader currently works only for books which do not have KOReader sidecar files, and of course requires the raw metadata column to be mapped. The use-case is for setting up a new device, or if a book was removed from your device and you've now added it back. This has been tested for calibre's Connect to Folder and Custom USB Device modes. It does not seem to work for the Kobo Touch device driver nor with wireless connections, but I (@charlesangus) find those don't communicate perfectly with Calibre/KOReader in any case... I haven't disabled it for other devices - it may be a quirk in my setup which is causing it to fail, and it may work fine for you.

Releases will also be uploaded to [this plugin thread on the MobileRead Forums](https://www.mobileread.com/forums/showthread.php?p=4060141). If you are on there as well, please let me know what you think of the plugin in that thread.

## Using this plugin

### Download and install

1. Go to your calibre's _Preferences_ > _Plugins_ > _Get new plugins_ and search for _KOReader Sync_
2. Click _Install_
3. Restart calibre

#### Alternatively

1. Download the latest release from [here](https://github.com/harmtemolder/koreader-calibre-plugin/tree/main/releases).
2. Go to your calibre's _Preferences_ > _Plugins_ > _Load plugin from file_ and point it to the downloaded ZIP file
3. Restart calibre

### Setup

1. Pick and choose the metadata you would like to sync and create the appropriate columns in calibre. These are your options:
   - A _Floating point numbers_ column to store the **current percent read**, with _Format for numbers_ set to `{:.0%}`.
   - An _Integers_ column to store the **current percent read**.
   - A regular _Text_ column to store the **location you last stopped reading at**.
   - A _Rating_ column to store your **rating** of the book, as entered on the book's status page.
   - A _Long text_ column to store your **review** of the book, as entered on the book's status page.
   - A regular _Text_ column to store the **reading status** of the book, as entered on the book status page (_Finished_, _Reading_, _On hold_).
   - A _Yes/No_ column to store the **reading status** of the book, as a boolean (_Yes_ = _Finished_, _No_ = everything else).
   - A _Date_ column to store **the date on which the first highlight or bookmark was made**. (This is probably around the time you started reading.)
   - A _Date_ column to store **the date on which the last highlight or bookmark was made**. (This is probably around the time you finished reading.)
   - A _Long text_ column to store your **bookmarks and highlights** of the book, with _Interpret this column as_ set to _Plain text formatted using markdown_. (Highlights are an unordered list with their metadata in an HTML comment.)
   - A regular _Text_ column to store the **MD5 hash** KOReader uses to sync progress to a [**KOReader Sync Server**](https://github.com/koreader/koreader-sync-server#koreader-sync-server). (_Progress sync_ in the KOReader app.) This might allow for syncing progress to calibre without having to connect your KOReader device, in the future.
   - A _Date_ column to store **when the last sync was performed**.
   - A _Date_ column to store **when the sidecar file was last modified**.',
   - A _Long text_ column to store the **contents of the metadata sidecar** as JSON, with _Interpret this column as_ set to _Plain text_. This is required to sync metadata back to KOReader sidecars.
10. Add _KOReader Sync_ to _main toolbar when a device is connected_, if it isn't there already.
11. Right-click the _KOReader Sync_ icon and _Configure_.
12. Map the metadata you want to sync to the newly created calibre columns.
13. Click _OK_ to save your mapping.
14. From now on just click the _KOReader Sync_ icon to sync all mapped metadata for all books on the connected device to calibre.

### Things to consider

- The plugin overwrites existing metadata in Calibre without asking. That usually isn’t a problem, because you will probably only add to KOReader’s metadata. But be aware that you might lose data in calibre if you’re not careful.
- Pushing sidecars back to KOReader currently only happens for sidecars which are missing. For now, manually delete the `<bookname>.sdr` folder from the device before attempting to push the sidecars back to KOReader for any books you would like to overwrite the current metadata with Calibre's metadata.
- When pushing missing sidecars to the device, no attempt is made to convert Calibre's metadata to account for changes in KOReader's sidecar format. Old metadata may work unpredictably if it's from a different version of KOReader.

### Supported devices

This plugin has been tested successfully with:

- Kobo Aura connected over USB, which means it will probably work for all comparable Kobo devices (`KOBO` and `KOBOTOUCH`)
- Kobo Aura H2O over USB (`KOBOTOUCHEXTENDED`, see [#6](https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin/6) for details)
- Kobo Aura connected wirelessly, which means it will probably work for all calibre connect devices (`SMART_DEVICE_APP`)
- A connected folder (`FOLDER_DEVICE`)
- Kindle Keyboard (`KINDLE2`, see [#1](https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin/1) for details)
- Tolino Vision 4 HD (`TOLINO`, see [this comment](https://www.mobileread.com/forums/showpost.php?p=4179705&postcount=28) for details)
- PocketBook Touch Lux 5 (which uses the `POCKETBOOK626` driver, so it will probably work for all comparable PocketBook devices, see [#8](https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin/8) for details)
- PocketBooks that use the `POCKETBOOK622` driver

This plugin is not compatible with:

- `MTP_DEVICE` (see [#2](https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin/2) for details)

### Issues

If you encounter any issues with the plugin, please submit them [here](https://github.com/harmtemolder/koreader-calibre-plugin/issues).

## Acknowledgements

- Multiple tweaks and bug fixes by [Glen Sawyer](https://git.sr.ht/~snelg)
- Additional functionality by [Charles Taylor](https://github.com/charlesangus/)
- Contains [SirAnthony's SLPP](https://github.com/SirAnthony/slpp) to parse Lua in Python.
- Some code borrowed from--and heavily inspired by--the great [Kobo Utilities](https://www.mobileread.com/forums/showthread.php?t=215339) calibre plugin.

## Contributing to this plugin

### Notes & Tips

- My first attempt was actually to sync calibre with KOReader's read progress through the progress sync plugin and a [sync server](https://github.com/koreader/koreader-sync-server). Read [here](https://github.com/koreader/koreader/issues/6399#issuecomment-721826362) why that did not work. This plugin might actually make that possible now by allowing you to store KOReader's MD5 hash in calibre...
- calibre allows you to auto-connect to a folder device on boot, which greatly speeds up your workflow when testing. You can find this under "Preferences" > "Tweaks", search for `auto_connect_to_folder`. Point that to the `dummy_device` folder in this repository. (I have included royalty free EPUBs for your and my convenience.)
- If you're testing and don't actually want to update any metadata, set `DRY_RUN` to `True` in `__init__.py`.
- I work in PyCharm, which offers a remote debugging server. To enable that in this plugin, set `PYDEVD` to `True` in `__init__.py`.You might need to change `sys.path.append` in `action.py`.
- The supported device drivers can be found in [the `SUPPORTED_DEVICES` list in `config.py`](https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/config.py#L30). Adding a new type here is the first step to adding support, but make sure all features are tested thoroughly before releasing a version with an added device

### Testing in calibre

Use make to load the plugin into calibre and launch it:

```shell
make dev
```

Alternatively, build a release and load that:

```shell
make zip load
```

### Building a release

Make sure you have the dependencies and have set the correct version number in `__init__.py`, `pluginIndexKOReaderSync.txt` and `Makefile`. Also update [Changelog](#changelog). Then:

```shell
make zip
```

### Debugging a release

1. Download the required release from [here](https://github.com/harmtemolder/koreader-calibre-plugin/tree/main/releases)
1. Add it to calibre by running this in your terminal: `calibre-customize -a "KOReader Sync vX.X.X-alpha.zip"`, where `X.X.X` refers to the version you downloaded
1. Start calibre in debug mode with `calibre-debug -g`
1. Configure the KOReader plugin as described [here](https://github.com/harmtemolder/koreader-calibre-plugin#setup)
1. Connect your device
1. Run the sync by clicking the KOReader icon in your toolbar
1. Check the details of the message when it's done if any/all books have been synced correctly
1. Check your (custom) columns for one of those books to see if their contents are what they should be
1. Check the output in your terminal for lines containing `koreader` to see what it did

## Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Removed sorting from `column_sidecar` transform because this caused an error in at least one of my books

## [0.5.2-beta] - 2023-05-22

- Many thanks to @elmodor and igorius for their help!

### Added

- Added config option to only sync if the metadata is newer than the data stored in calibre (will fallback to "Percent read column" if no "Date Modified column" exists or can not be obtained)
- Added config option to not sync if the book has already been marked as finished (via "Percent read column" or "Reading status column")
- Added a yes/no column for read status (based on [changes from igorius at MobileRead](https://www.mobileread.com/forums/showpost.php?p=4323088&postcount=90))

### Changed

- Pylint cleanup
- Update README to match new columns
- Update dummy device and library to match new columns

### Fixed

- Fixed crash for wireless connected devices while trying to get the "Date Modified column" value
- Fixed setting correct sync status for `column_status` if no status is sent from KOReader

## [0.5.1-beta] - 2022-12-27

### Added

- Add support for Date Synced column (stores date of last sync from KOReader to Calibre)
- Add support for Date Modified column (stores date modified of KOReader Sidecar)

### Changed

- Standardized results message format
- code cleanup to pass linting

### Fixed

- Error in results message
- Fix error in debug_print definition

## [0.5.0-beta] - 2022-12-27

### Added

- Add "Sync Missing Sidecars to KOReader" functionality

### Changed

- Vendor in slpp.py instead of adding it as a separate dependency to reduce fragility

## [0.4.1-beta] - 2022-11-08

### Changed

- Use calibre's built-in UTC timezone ([source](https://github.com/kovidgoyal/calibre/blob/0cecc77a22c2cc91bbb7a5b5b414804808f73976/src/calibre/utils/date.py#L14)), because `tzdata` isn't available on Windows (see [#13](https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin/13))

## [0.4.0-beta] - 2022-11-02

### Added

- Calculate first and last bookmark date columns

## [0.3.2-beta] - 2022-09-16

### Added

- Enable `POCKETBOOK632`

## [0.3.1-beta] - 2022-09-15

### Added

- Enable `USER_DEFINED`

## [0.3.0-beta] - 2022-09-13

### Changed

- Don't break for unknown device class, but try to sync anyway

## [0.2.7-alpha] - 2022-02-18

### Added

- Enable `TOLINO`, for real this time

## [0.2.6-alpha] - 2022-02-04

### Added

- Enable `POCKETBOOK622`

## [0.2.5-alpha] - 2021-12-20

### Added

- Enable `POCKETBOOK626`

## [0.2.4-alpha] - 2021-12-12

### Added

- Enable `TOLINO`

## [0.2.3-alpha] - 2021-11-23

### Added

- Enable `KOBOTOUCHEXTENDED`

## [0.2.2-alpha] - 2021-06-22

### Fixed

- Skip metadata sidecars that cannot be decoded (e.g. from a very old version of KOReader)

### Changed

- Use `path` instead of `lpath` for book paths to go around `MTP_DEVICE` lowercasing the latter
- Disable `MTP_DEVICE` because it cannot be supported (see [#2](https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin/2))

### Added

- Enable `KINDLE2`

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

[0.1.0-alpha]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.1.0-alpha.zip
[0.1.1-alpha]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.1.1-alpha.zip
[0.1.2-alpha]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.1.2-alpha.zip
[0.1.3-alpha]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.1.3-alpha.zip
[0.1.4-alpha]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.1.4-alpha.zip
[0.2.0-alpha]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.2.0-alpha.zip
[0.2.1-alpha]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.2.1-alpha.zip
[0.2.2-alpha]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.2.2-alpha.zip
[0.2.3-alpha]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.2.3-alpha.zip
[0.2.4-alpha]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.2.4-alpha.zip
[0.2.5-alpha]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.2.5-alpha.zip
[0.2.6-alpha]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.2.6-alpha.zip
[0.2.7-alpha]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.2.7-alpha.zip
[0.3.0-beta]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.3.0-beta.zip
[0.3.1-beta]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.3.1-beta.zip
[0.3.2-beta]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.3.2-beta.zip
[0.4.0-beta]: https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/releases/KOReader%20Sync%20v0.4.0-beta.zip
[0.4.1-beta]: https://github.com/harmtemolder/koreader-calibre-plugin/releases/tag/v0.4.1-beta
[0.5.0-beta]: https://github.com/harmtemolder/koreader-calibre-plugin/releases/tag/v0.5.0-beta
[0.5.1-beta]: https://github.com/harmtemolder/koreader-calibre-plugin/releases/tag/v0.5.1-beta
[0.5.2-beta]: https://github.com/harmtemolder/koreader-calibre-plugin/releases/tag/v0.5.2-beta
[unreleased]: https://github.com/harmtemolder/koreader-calibre-plugin
