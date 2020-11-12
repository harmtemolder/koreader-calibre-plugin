# KOReader calibre plugin

[KOReader](https://koreader.rocks/) creates sidecar files that hold read progress and annotations. This plugin reads the data from those sidecar files and updates calibre’s metadata based on them. It is inspired by [the Kobo Utilities plugin](https://www.mobileread.com/forums/showthread.php?t=215339), that synchronizes reading progress between Nickel and custom columns in calibre.

## Notes

- A device may be connected with USB or wirelessly using [the calibre plugin](https://github.com/koreader/koreader/tree/master/plugins/calibre.koplugin). (See [calibre’s repository](https://github.com/kovidgoyal/calibre/tree/master/src/calibre/devices/smart_device_app) for their end of the latter.)
- My first attempt was actually to sync calibre with KOReader’s read progress through the progress sync plugin and a [sync server](https://github.com/koreader/koreader-sync-server). Read [here](https://github.com/koreader/koreader/issues/6399#issuecomment-721826362) why that did not work.

## Building a release

If you do not have `slpp.py` yet, run:

```shell
make dependencies all
```

Otherwise this is enough:

```shell
make
```

## Acknowledgements

- Contains (SirAnthony’s SLPP)[https://github.com/SirAnthony/slpp]

## Contributing

Contributing patches on sourcehut works through `git send-email`. You can find this repository’s mailing list [here](https://lists.sr.ht/~harmtemolder/koreader-calibre-plugin).

### Relevant documentation when contributing

- [calibre’s documentation on setting up a development environment](https://manual.calibre-ebook.com/develop.html)
- [calibre’s documentation on writing an interface plugin](https://manual.calibre-ebook.com/creating_plugins.html#a-user-interface-plugin)

## Issues

If you encounter any issues with the plugin, please submit an issue <a href="https://todo.sr.ht/~harmtemolder/koreader-calibre-plugin">here</a>.
