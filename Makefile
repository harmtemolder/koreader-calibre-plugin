version = 0.2.0-alpha
zip_file = releases/KOReader Sync v$(version).zip
zip_contents = *.py LICENSE *.md plugin-import-name-koreader.txt images/*.png

all: zip

dependencies:
	@ wget -N https://github.com/SirAnthony/slpp/raw/master/slpp.py

zip:
	@ echo "creating new $(zip_file)" && zip "$(zip_file)" $(zip_contents) && echo "created new $(zip_file)"

dev:
	@ calibre-customize -b .; calibre-debug -g