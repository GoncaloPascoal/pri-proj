
build : install-dependencies run

run :
	python3 prepare.py

install-dependencies :
	for dep in pandas seaborn ; do \
		pip3 install $$dep ; \
	done
