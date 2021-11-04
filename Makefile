
build : install-dependencies run

run :
	python3 prepare.py

steam-spy :
	@python3 steam_spy.py

install-dependencies :
	for dep in pandas seaborn beautifulsoup4 steamreviews colorama ; do \
		pip3 install $$dep ; \
	done
