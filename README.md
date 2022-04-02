# Kraken-Scanner
#
# Idea is to have this running on a RPI with a dedicated screen to have as a picture frame with the current price and balance information
#
# You will need to create a file called kraken.key containing a key to access your account
#
# Execute the run.sh file in a terminal window. Page will refresh every 60 seconds
#
# Commands available:
#
# r - force a refresh
# c - clear the page and refresh
# q - quit
# p - pause the pulling of information/refresh. Any key to resume
#
# Things to do -
# 
# 1. add the reading of a text file containing ledger entries to be able to show all balances (not just the ones on kraken).
# 2. ability to define the currency for reporting (currently hard coded to EUR)
