# Read the version from the version.txt file
version := $(shell head -n 1 version.txt)
zip_file = KOReader_Sync_v$(version).zip
zip_contents = about.txt LICENSE plugin-import-name-koreader.txt *.py *.md images/*.png
plugin_index_file_to_upd = pluginIndexKOReaderSync.txt
init_file_to_upd = __init__.py
release_dir = release

# Convert the version to tuple format
version_tuple := $(shell echo $(version) | awk -F. '{print "("$$1", "$$2", "$$3")"}')

# Flatpak support: set FLATPAK=1 to use Flatpak commands
# e.g., make release FLATPAK=1
ifdef FLATPAK
CALIBRE_CUSTOMIZE = flatpak run --command=calibre-customize com.calibre_ebook.calibre
CALIBRE_DEBUG = flatpak run --command=calibre-debug com.calibre_ebook.calibre
else
CALIBRE_CUSTOMIZE = calibre-customize
CALIBRE_DEBUG = calibre-debug
endif

# Main targets
release: update_version zip load

zip: $(release_dir)
	@echo "Creating new $(release_dir)/$(zip_file)"
	@mkdir -p "$(release_dir)" && zip "$(release_dir)/$(zip_file)" $(zip_contents)

# Loads current src content, use this if doing dev changes
# Use FLATPAK=1 for Flatpak installations
dev:
	@$(CALIBRE_CUSTOMIZE) -b .; $(CALIBRE_DEBUG) -g

# Loads zip from release dir if exists
# Use FLATPAK=1 for Flatpak installations
load:
	@$(CALIBRE_CUSTOMIZE) -a "$(release_dir)/$(zip_file)"; $(CALIBRE_DEBUG) -g

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
	@echo "Tagging version v$(version) and pushing to the repository"
	@if git rev-parse "v$(version)" >/dev/null 2>&1; then \
		echo "Tag v$(version) already exists. Deleting the old tag."; \
		git tag -d "v$(version)"; \
		git push origin ":refs/tags/v$(version)"; \
	fi
	@git tag -a "v$(version)" -m "Version $(version)"  # Create annotated tag for the version
	@git push origin "v$(version)"  # Push the tag to the remote repository

md_to_bb:
	@echo "Converting input.md to output.forumbb"
	@python .scripts/md-to-bb.py .scripts/input.md .scripts/output.forumbb
	@echo "Done:"
	@cat .scripts/output.forumbb
