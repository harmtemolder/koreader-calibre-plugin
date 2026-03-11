# Read the version from the .version file
version := $(shell head -n 1 .version 2>/dev/null || echo 0.0.1)

# Dev version components
DATE := $(shell date -u +%Y%m%d)
SHA := $(shell git rev-parse --short HEAD 2>/dev/null || echo local)
DEV_VERSION := $(DATE)-$(SHA)-dev
DEV_TUPLE := (0, 0, 0)

# Check for a dev version file in dist, otherwise use the release version
ifeq ($(wildcard dist/.version-dev),)
    effective_version := $(version)
else
    effective_version := $(shell head -n 1 dist/.version-dev)
endif

zip_file = KOReader_Sync_v$(effective_version).zip
zip_contents = about.txt LICENSE plugin-import-name-koreader.txt *.py *.md images/
plugin_index_file_to_upd = pluginIndexKOReaderSync.txt
init_file_to_upd = __init__.py
dist_dir = dist

# Convert the version to tuple format
version_tuple := $(shell echo $(version) | awk -F. '{print "("$$1", "$$2", "$$3")"}')

# Flatpak support: set FLATPAK=1 to use Flatpak commands
# e.g., make release FLATPAK=1
ifdef FLATPAK
    ifneq ($(shell uname -s 2>/dev/null),Linux)
        $(error FLATPAK=1 is only supported on Linux. For other platforms, please install Calibre natively and run make without FLATPAK=1)
    endif
    ifeq ($(shell command -v flatpak 2>/dev/null),)
        $(error The 'flatpak' command was not found. Please install flatpak or run make without FLATPAK=1)
    endif
    ifeq ($(shell flatpak info com.calibre_ebook.calibre >/dev/null 2>&1; echo $$?),1)
        $(error Calibre Flatpak (com.calibre_ebook.calibre) is not installed. Please install it or run make without FLATPAK=1)
    endif
    CALIBRE_CUSTOMIZE = flatpak run --command=calibre-customize com.calibre_ebook.calibre
    CALIBRE_DEBUG = flatpak run --command=calibre-debug com.calibre_ebook.calibre
else
    CALIBRE_CUSTOMIZE = calibre-customize
    CALIBRE_DEBUG = calibre-debug
endif

# Main targets
# Always clean dev metadata before a formal release
release: clean_dev
	@$(MAKE) update_version
	@$(MAKE) zip
	@$(MAKE) load

zip: $(dist_dir)
	@echo "Creating new $(dist_dir)/$(zip_file)"
	@mkdir -p "$(dist_dir)" && zip -r "$(dist_dir)/$(zip_file)" $(zip_contents)

# Loads current src content, use this if doing dev changes
dev: dev_version
	@$(MAKE) zip
	@$(MAKE) load

dev_version:
	@mkdir -p "$(dist_dir)"
	@echo "$(DEV_VERSION)" > "$(dist_dir)/.version-dev"
	@sed -i 's/^\([[:space:]]*\)version = ([0-9, ]*)/\1version = $(DEV_TUPLE)/' $(init_file_to_upd)
	@if grep -q "^[[:space:]]*version_string =" $(init_file_to_upd); then \
		sed -i "s/^\([[:space:]]*\)version_string = .*/\1version_string = '$(DEV_VERSION)'/" $(init_file_to_upd); \
	else \
		sed -i "/^[[:space:]]*version = /a \    version_string = '$(DEV_VERSION)'" $(init_file_to_upd); \
	fi
	@sed -i 's/Version: [^;]*;/Version: $(DEV_VERSION);/' $(plugin_index_file_to_upd)
	@echo "Dev version set to $(DEV_VERSION)"

# Install the plugin into Calibre
install: zip
	@$(CALIBRE_CUSTOMIZE) -a "$(dist_dir)/$(zip_file)"

# Install and then launch Calibre in debug mode
load: install
	@$(CALIBRE_DEBUG) -g

update_version: update_version_plugin_index update_version_init
	@echo "Versions updated in all files."

update_version_plugin_index:
	@echo "Updating version in $(plugin_index_file_to_upd) to $(version)"
	@sed -i 's/Version: [^;]*;/Version: $(version);/' $(plugin_index_file_to_upd)
	@echo "Version updated in $(plugin_index_file_to_upd)"

update_version_init:
	@echo "Updating version in $(init_file_to_upd) to $(version_tuple)"
	@sed -i 's/^\([[:space:]]*\)version = ([0-9, ]*)/\1version = $(version_tuple)/' $(init_file_to_upd)
	@sed -i "s/^\([[:space:]]*\)version_string = .*/\1version_string = '$(version)'/" $(init_file_to_upd)
	@echo "Version updated in $(init_file_to_upd)"

clean_dev:
	@rm -f "$(dist_dir)/.version-dev"
	@echo "Dev version metadata removed from $(dist_dir)."

clean: clean_dev
	@rm -rf "$(dist_dir)"
	@echo "Cleaned $(dist_dir) directory"

$(dist_dir):
	@mkdir -p $(dist_dir)
	@echo "Created $(dist_dir) directory"

debug_version:
	@echo "Read version: $(version)"
	@echo "Effective version: $(effective_version)"
	@echo "Version tuple: $(version_tuple)"
	@echo "Zip file: $(zip_file)"

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

.PHONY: release zip dev install load update_version update_version_plugin_index update_version_init debug_version tag md_to_bb dev_version clean_dev clean
