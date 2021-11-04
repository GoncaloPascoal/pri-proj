
build : install-dependencies run

run :
	python3 prepare.py

install-dependencies :
	for dep in pandas seaborn beautifulsoup4 lxml steamreviews colorama howlongtobeatpy ; do \
		pip3 install $$dep ; \
	done
