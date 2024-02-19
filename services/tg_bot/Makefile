PROJECT_NAME = chauss_vpn
PROJECT_VERSION = v0.0.1

lint:
	pylint *.py --disable=fixme,unspecified-encoding,too-few-public-methods,unspecified-encoding \
				--max-line-length=110
	pydocstyle *.py

test:
	python -m unittest discover -s tests 

I18N_DOMAIN = $(PROJECT_NAME)
I18N_DIR = i18n
I18N_POTNAME = messages.pot

$(I18N_POTNAME): *.py
	pybabel extract --project=$(PROJECT_NAME) --version=$(PROJECT_VERSION) \
		--add-comments="May the 4th be with u! \(._.)/"	--output-file=$(I18N_POTNAME) $(extra_args) *.py

i18n-init: $(I18N_POTNAME)
	pybabel init --domain=$(I18N_DOMAIN) --input-file=$(I18N_POTNAME) --locale=$(locale) \
		--output-dir=$(I18N_DIR) $(extra_args)

i18n-update: $(I18N_POTNAME)
	pybabel update --input-file=$(I18N_POTNAME) --output-dir=$(I18N_DIR)\
		--domain=$(I18N_DOMAIN) --update-header-comment $(extra_args)  

i18n-compile: $(I18N_DIR)/*/LC_MESSAGES/$(I18N_DOMAIN).po i18n-update
	pybabel compile --domain=$(I18N_DOMAIN) --directory=$(I18N_DIR) --use-fuzzy --statistics $(extra_args) 

i18n-clean:
	rm -f $(I18N_POTNAME) $(I18N_DIR)/*/LC_MESSAGES/$(I18N_DOMAIN).mo

doc:
	sphinx-build -M html docs/source docs/build

doc-clean:
	make -C docs clean

build: i18n-compile doc

clean: i18n-clean doc-clean
	rm -rf __pycache__
