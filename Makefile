# Read the version from the version.txt file
version := $(shell head -n 1 version.txt)
zip_file = KOReader_Sync_v$(version).zip
zip_contents = about.txt LICENSE plugin-import-name-koreader.txt *.py *.md images/*.png
plugin_index_file_to_upd = pluginIndexKOReaderSync.txt
init_file_to_upd = __init__.py
release_dir = release

# Convert the version to tuple format
version_tuple := $(shell echo $(version) | awk -F. '{print "("$$1", "$$2", "$$3")"}')

all: update_version zip

zip: $(release_dir)
	@echo "Creating new $(release_dir)/$(zip_file)" && zip "$(release_dir)/$(zip_file)" $(zip_contents) && echo "Created new $(release_dir)/$(zip_file)"

dev:
	@calibre-customize -b .; calibre-debug -g

load:
	@calibre-customize -a "$(release_dir)/$(zip_file)"; calibre-debug -g

update_version: update_version_plugin_index update_version_init
	@echo "Versions updated in all files."

update_version_plugin_index:
	@echo "Updating version in $(plugin_index_file_to_upd) to $(version)"
	@sed -i 's/Version: [^;]*;/Version: $(version);/' $(plugin_index_file_to_upd)
	@echo "Version updated in $(plugin_index_file_to_upd)"

update_version_init:
	@echo "Updating version in $(init_file_to_upd) to $(version_tuple)"
	@sed -i '/^[[:space:]]*version = /s/version = ([0-9, ]*)/version = $(version_tuple)/' $(init_file_to_upd)
	@echo "Version updated in $(init_file_to_upd)"

$(release_dir):
	@mkdir -p $(release_dir)
	@echo "Created $(release_dir) directory"

debug_version:
	@echo "Read version: $(version)"
	@echo "Version tuple: $(version_tuple)"

tag:
	@echo "Tagging version $(version) and pushing to the repository"
	@git tag -a v$(version) -m "Version $(version)"  # Create annotated tag for the version
	@git push origin v$(version)  # Push the tag to the remote repository
