# KOReader calibre plugin

[KOReader](https://koreader.rocks/) allows for synchronizing of reading progress to a [sync server](https://github.com/koreader/koreader-sync-server) through [the progress sync plugin](https://github.com/koreader/koreader/wiki/Progress-sync). This [calibre](https://calibre-ebook.com/) plugin aims to synchronize reading progress from such a sync server to calibre (and maybe later also the other way around). It is inspired by [the Kobo Utilities plugin](https://www.mobileread.com/forums/showthread.php?t=215339), that synchronizes reading progress locally between Nickel and custom columns in calibre.

## Notes

- The EPUB stored in calibre’s library is not the same as the one received by KOReader when pushing: it seems `content.opf` is a merge of the original `content.opf` and calibre’s `metadata.opf`. This means that—after syncing progress from kosync to calibre—a subsequent push will result in a different EPUB with a different hash.
- 

## About the KOReader progress sync plugin

- The default server's address is `https://sync.koreader.rocks:443`. See [`api.json`](https://github.com/koreader/koreader/blob/5909a887655682f0e725e4e0403dbd3b288cc1f1/plugins/kosync.koplugin/api.json) for the outline of the API.
- The `Accept` header should be set to `application/vnd.koreader.v1+json` ([source](https://github.com/koreader/koreader/blob/85b498d76e0edbb3d429c3dfecfe267c5c266c48/plugins/kosync.koplugin/KOSyncClient.lua))
- See [this module](https://github.com/koreader/koreader-sync-server/blob/d7d1ebff54240cfbade96a81f2971b6ad0afa33f/app/controllers/1/syncs_controller.lua#L42) for the `x-auth-user` and `x-auth-key` headers. The latter should be an MD5 hash of the user’s password
- References to books are stored based on a partial MD5 hash of the file itself (calculated with [the `fastDigest` function](https://github.com/koreader/koreader/blob/8403154d4d36f4279828e0af90667a92685a4ebe/frontend/document/document.lua#L125))

## Development

- [Setting up a calibre development environment](https://manual.calibre-ebook.com/develop.html)
