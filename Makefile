
run : install-dependencies reviews proton-db steam-spy prepare

# Installs necessary dependencies using pip, Python's package installer
install-dependencies :
	@for dep in pandas seaborn beautifulsoup4 steamreviews colorama requests requests_futures tqdm; do \
		echo "Installing $$dep..." ; \
		pip3 install $$dep > /dev/null ; \
	done

# Gathers game review data using the Steam Store API
reviews :
	@python3 reviews.py

# Updates the ratings and playtime information using the SteamSpy API
steam-spy :
	@python3 steam_spy.py

# Gets number of reports and game compatibility tier from ProtonDB
proton-db :
	@python3 proton_db.py

# Script for cleaning and processing the Kaggle dataset
prepare :
	@python3 prepare.py
