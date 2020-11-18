zip_file = KOReader Sync.zip
zip_contents = *.py LICENSE *.md *.txt images/*.png

all: clean zip

dependencies:
	@ wget -N https://github.com/SirAnthony/slpp/raw/master/slpp.py

clean:
	@ rm -f "$(zip_file)" && echo "removed old $(zip_file)"

zip:
	@ echo "creating new $(zip_file)" && zip "$(zip_file)" $(zip_contents) && echo "created new $(zip_file)"
