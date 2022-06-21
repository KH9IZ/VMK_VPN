PROJECT_NAME = vmk_vpn
PROJECT_VERSION = v0.0.1

deploy:
	# Add deadsnake repo if ubuntu lower then 22
	sudo apt install python3.10 python3.10-venv python3.10-dev

lint:
	pylint *.py --disable=unspecified-encoding,too-few-public-methods,unspecified-encoding \
				--max-line-length=110
	pydocstyle *.py

test:
	python -m unittest discover

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

i18n-compile: $(I18N_DIR)/*/LC_MESSAGES/$(I18N_DOMAIN).po
	pybabel compile --domain=$(I18N_DOMAIN) --directory=$(I18N_DIR) --use-fuzzy --statistics $(extra_args) 

i18n-clean:
	rm $(I18N_POTNAME) $(I18N_DIR)/*/LC_MESSAGES/$(I18N_DOMAIN).mo

doc:
	sphinx-build -M html docs/source docs/build
