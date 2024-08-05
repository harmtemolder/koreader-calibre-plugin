# KOReader calibre plugin

A calibre plugin to synchronize metadata from KOReader to calibre.

[KOReader](https://koreader.rocks/) creates sidecar files that hold read
progress and annotations.
This plugin reads the data from those sidecar files and updates calibre's
metadata based on them. It is inspired
by [the Kobo Utilities plugin](https://www.mobileread.com/forums/showthread.php?t=215339),
that synchronizes reading progress between the original Kobo firmware ("Nickel")
and custom columns in calibre.

Note that at the moment the sync is primarily one-way—from the KOReader device
to calibre, and only works for USB
and [wireless](https://github.com/koreader/koreader/wiki/Calibre-wireless-connection)
devices. For best experience please use the latest
KOReader [release](https://github.com/koreader/koreader/releases)

## Using this plugin

### Download and install

1. Go to your calibre's _Preferences_ > _Plugins_ > _Get new plugins_ and search
   for _KOReader Sync_
2. Click _Install_
3. Restart calibre

#### Alternatively

1. Download the latest release
   from [here](https://github.com/harmtemolder/koreader-calibre-plugin/releases).
2. Go to your calibre's _Preferences_ > _Plugins_ > _Load plugin from file_ and
   point it to the downloaded ZIP file
3. Restart calibre

### Setup

1. Pick and choose the metadata you would like to sync and create the
   appropriate columns in calibre. These are your options:

   - A _Floating point numbers_ column to store the **current percent read**,
     with _Format for numbers_ set to `{:.0%}`.
   - An _Integers_ column to store the **current percent read**.
   - A regular _Text_ column to store the **location you last stopped reading
     at **.
   - A _Rating_ column to store your **rating** of the book, as entered on the
     book's status page.
   - A _Long text_ column to store your **review** of the book, as entered on
     the book's status page.
   - A regular _Text_ column to store the **reading status** of the book, as
     entered on the book status page (_Finished_, _Reading_, _On hold_).
   - A _Yes/No_ column to store the **reading status** of the book, as a
     boolean (_Yes_ = _Finished_, _No_ = everything else).
   - A _Long text_ column to store your **bookmarks and highlights** of the
     book, with _Interpret this column as_ set to _Plain text formatted using
     markdown_. (Highlights are an unordered list with their metadata in an
     HTML comment.)
   - A regular _Text_ column to store the **MD5 hash** KOReader uses to sync
     progress to a [**KOReader Sync Server
     **](https://github.com/koreader/koreader-sync-server#koreader-sync-server)
     . (_Progress sync_ in the KOReader app.) This might allow for syncing
     progress to calibre without having to connect your KOReader device, in the
     future.
   - A _Date_ column to store **when the last sync was performed**.
   - A _Long text_ column to store the **contents of the metadata sidecar** as
     HTML, with _Interpret this column as_ set to _HTML_.

10. Add _KOReader Sync_ to _main toolbar when a device is connected_, if it
    isn't there already.
11. Right-click the _KOReader Sync_ icon and _Configure_.
12. Map the metadata you want to sync to the newly created calibre columns.
13. Click _OK_ to save your mapping.
14. From now on just click the _KOReader Sync_ icon to sync all mapped metadata
    for all books on the connected device to calibre.

**Note:** Some field are depreciated and removed from plugin since they are
changed/removed from `sidecar_contents` data structure:

- `first_bookmark` removed
- `last_bookmark` removed
- `bookmarks` renamed to `annotations`
- `rating` uses 5-point instead 10-point scale
- `date_sidecar_modified` removed from `calculated`

### Things to consider

- The plugin overwrites existing metadata in Calibre without asking. That
  usually isn’t a problem, because you will probably only add to KOReader’s
  metadata. But be aware that you might lose data in calibre if you’re not
  careful.
- Pushing sidecars back to KOReader currently only happens for sidecars which
  are missing. For now, manually delete the `<bookname>.sdr` folder from the
  device before attempting to push the sidecars back to KOReader for any books
  you would like to overwrite the current metadata with Calibre's metadata.
- When pushing missing sidecars to the device, no attempt is made to convert
  Calibre's metadata to account for changes in KOReader's sidecar format. Old
  metadata may work unpredictably if it's from a different version of KOReader.

### Supported devices

This plugin has been tested successfully with:

- Kobo Clara BW connected over USB or KOreader wireless driver (means should
  work with prev and latest color modes as well)
- Kobo Aura connected over USB, which means it will probably work for all
  comparable Kobo devices (`KOBO` and `KOBOTOUCH`)
- Kobo Aura H2O over USB (`KOBOTOUCHEXTENDED`,
  see [#6](https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin/6) for
  details)
- Kobo Aura connected wirelessly, which means it will probably work for all
  calibre connect devices (`SMART_DEVICE_APP`)
- A connected folder (`FOLDER_DEVICE`)
- Kindle Keyboard (`KINDLE2`,
  see [#1](https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin/1) for
  details)
- Tolino Vision 4 HD (`TOLINO`,
  see [this comment](https://www.mobileread.com/forums/showpost.php?p=4179705&postcount=28)
  for details)
- PocketBook Touch Lux 5 (which uses the `POCKETBOOK626` driver, so it will
  probably work for all comparable PocketBook devices,
  see [#8](https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin/8) for
  details)
- PocketBooks that use the `POCKETBOOK622` driver

This plugin is not compatible with (may work with latest plugin release):

- `MTP_DEVICE` (
  see [#2](https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin/2) for
  details)

### Issues

If you encounter any issues with the plugin, please submit
them [here](https://github.com/harmtemolder/koreader-calibre-plugin/issues).

## Acknowledgements

- Multiple tweaks and bug fixes by [Glen Sawyer](https://git.sr.ht/~snelg)
- Additional functionality by [Charles Taylor](https://github.com/charlesangus/)
- Contains [SirAnthony's SLPP](https://github.com/SirAnthony/slpp) to parse Lua
  in Python.
- Some code borrowed from--and heavily inspired by--the
  great [Kobo Utilities](https://www.mobileread.com/forums/showthread.php?t=215339)
  calibre plugin.

## Contributing to this plugin

### Notes & Tips

- My first attempt was actually to sync calibre with KOReader's read progress
  through the progress sync plugin and
  a [sync server](https://github.com/koreader/koreader-sync-server).
  Read [here](https://github.com/koreader/koreader/issues/6399#issuecomment-721826362)
  why that did not work. This plugin might actually make that possible now by
  allowing you to store KOReader's MD5 hash in calibre...
- calibre allows you to auto-connect to a folder device on boot, which greatly
  speeds up your workflow when testing. You can find this under "
  Preferences" > "Tweaks", search for `auto_connect_to_folder`. Point that to
  the `dummy_device` folder in this repository. (I have included royalty free
  EPUBs for your and my convenience.)
- If you're testing and don't actually want to update any metadata,
  set `DRY_RUN` to `True` in `__init__.py`.
- I work in PyCharm, which offers a remote debugging server. To enable that in
  this plugin, set `PYDEVD` to `True` in `__init__.py`.You might need to
  change `sys.path.append` in `action.py`.
- The supported device drivers can be found
  in [the `SUPPORTED_DEVICES` list in `config.py`](https://github.com/harmtemolder/koreader-calibre-plugin/blob/main/config.py#L32).
  Adding a new type here is the first step to adding support, but make sure all
  features are tested thoroughly before releasing a version with an added device

### Testing in calibre

Use make to load the plugin into calibre and launch it:

```shell
make dev
```

### Release

1. Update version in one file `version.txt`
1. Use `make release` and it will update version, create zip, upload zip to
   plugin directory
1. Push all changes
1. Use `make tag` to create and push tag
1. Create release in github, use pushed tag and upload created zip to the
   release

### Debugging a release

1. Download the required release
   from [here](https://github.com/harmtemolder/koreader-calibre-plugin/releases)
1. Add it to calibre by running this in your
   terminal: `calibre-customize -a "KOReader_Sync_vX.X.X.zip"`, where `X.X.X`
   refers to the version you downloaded
1. Start calibre in debug mode with `calibre-debug -g`
1. Configure the KOReader plugin as
   described [here](https://github.com/harmtemolder/koreader-calibre-plugin#setup)
1. Connect your device
1. Run the sync by clicking the KOReader icon in your toolbar
1. Check the details of the message when it's done if any/all books have been
   synced correctly
1. Check your (custom) columns for one of those books to see if their contents
   are what they should be
1. Check the output in your terminal for lines containing `koreader` to see what
   it did
