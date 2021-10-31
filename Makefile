
build : install-dependencies run

run :
	python3 prepare.py

install-dependencies :
	for dep in pandas seaborn beautifulsoup4 colorama ; do \
		pip3 install $$dep ; \
	done
