version = 0.5.2-beta
zip_file = releases/KOReader Sync v$(version).zip
zip_contents = about.txt LICENSE plugin-import-name-koreader.txt *.py *.md  images/*.png

all: zip

zip:
	@ echo "creating new $(zip_file)" && zip "$(zip_file)" $(zip_contents) && echo "created new $(zip_file)"

dev:
	@ calibre-customize -b .; calibre-debug -g

load:
	@ calibre-customize -a "$(zip_file)"; calibre-debug -g
