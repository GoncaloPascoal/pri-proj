
all : install-dependencies reviews hltb proton-db steam-spy prepare

# Installs necessary dependencies using pip, Python's package installer
install-dependencies : /usr/bin/pip3
	@for dep in pandas seaborn beautifulsoup4 lxml steamreviews colorama howlongtobeatpy requests requests_futures tqdm; do \
		echo "Installing $$dep..." ; \
		pip3 install $$dep > /dev/null ; \
	done

# Gathers game review data using the Steam Store API
reviews : /usr/bin/python3
	@python3 reviews.py

# Updates the ratings and playtime information using the SteamSpy API
steam-spy : /usr/bin/python3 data/steam.csv
	@python3 steam_spy.py

# Fetches information from HowLongToBeat website (regarding the expected
# length of a game based on user reports)
hltb : /usr/bin/python3
	@python3 hltb.py

# Gets number of reports and game compatibility tier from ProtonDB
proton-db : /usr/bin/python3
	@python3 proton_db.py

# Script for cleaning and processing the Kaggle dataset
prepare : /usr/bin/python3 data/reviews.csv data/steam_updated.csv \
data/steam_description_data.csv data/proton_db.csv data/hltb.csv
	@python3 prepare.py

# Deletes all generated JSON files
clean-json : /usr/bin/rm
	rm -f data/steam.json data/descriptions.json \
	data/reviews.json data/hltb.json data/proton_db.json

# Deletes all files generated by the pipeline
clean : clean-json
	rm -f data/reviews.csv data/hltb.csv data/proton_db.csv data/steam_updated.csv

# Data analysis
analysis :
	@python3 analysis.py
