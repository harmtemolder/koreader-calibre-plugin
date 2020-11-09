zip_file = KOReader Sync.zip
zip_contents = *.py LICENSE *.md *.txt

all: clean zip

clean:
	@ rm -f "$(zip_file)"  && echo "removed old $(zip_file)"

zip:
	@ zip "$(zip_file)" $(zip_contents) && echo "built new $(zip_file)"
