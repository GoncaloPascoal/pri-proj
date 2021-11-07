
build : install-dependencies get-reviews prepare

# Script for cleaning and processing the Kaggle dataset
prepare :
	python3 prepare.py

steam-spy :
	@python3 steam_spy.py

# Installs necessary dependencies using pip, Python's package installer
install-dependencies :
	@for dep in pandas seaborn beautifulsoup4 lxml steamreviews colorama howlongtobeatpy requests requests_futures tqdm; do \
		echo "Installing $$dep..." ; \
		pip3 install $$dep > /dev/null ; \
	done

get-reviews :
	python3 get_reviews.py