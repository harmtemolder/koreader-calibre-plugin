# KOReader calibre plugin

[KOReader](https://koreader.rocks/) creates sidecar files that hold read progress and annotations. This plugin reads the data from those sidecar files and updates calibre’s metadata based on them. It is inspired by [the Kobo Utilities plugin](https://www.mobileread.com/forums/showthread.php?t=215339), that synchronizes reading progress between the original Kobo firmware (“Nickel”) and custom columns in calibre.

Note that at the moment the sync is one-way: from the KOReader device to calibre.

## Using this plugin

### Setup

- Pick and choose the metadata you would like to sync and create the appropriate columns in calibre:
  - A “Floating point numbers” column for **percentage read**, with “Format for numbers” set to `{:.0%}`
  - A “Long text” column for the **raw contents of the metadata sidecar**, with “Interpret this column as” set to “Plain text”
  - A regular “Text” column for the MD5 hash KOReader uses to sync progress to a [**KOReader Sync Server**](https://github.com/koreader/koreader-sync-server#koreader-sync-server). (“Progress sync” in the KOReader app.) This might allow for syncing progress to calibre without having to connect your KOReader device, in the future.
  -

### Issues

If you encounter any issues with the plugin, please submit them <a href="https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin">here</a>.

## Contributing to this plugin

### Notes & Tips

- My first attempt was actually to sync calibre with KOReader’s read progress through the progress sync plugin and a [sync server](https://github.com/koreader/koreader-sync-server). Read [here](https://github.com/koreader/koreader/issues/6399#issuecomment-721826362) why that did not work.
- A device may be connected with USB or wirelessly using [the calibre plugin](https://github.com/koreader/koreader/tree/master/plugins/calibre.koplugin). (See [calibre’s repository](https://github.com/kovidgoyal/calibre/tree/master/src/calibre/devices/smart_device_app) for their end of the latter.)
- calibre allows you to auto-connect to a folder device on boot, which greatly speeds up your workflow when testing. You can find this under “Preferences” > “Tweaks”, search for `auto_connect_to_folder`.
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

## Acknowledgements

- Contains (SirAnthony’s SLPP)[https://github.com/SirAnthony/slpp].
- Some code borrowed from—and heavily inspired by—the great [Kobo Utilities](https://www.mobileread.com/forums/showthread.php?t=215339) calibre plugin.
-
