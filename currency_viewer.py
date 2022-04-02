# -*- coding: utf-8 -*-
# Includes
import krakenex
import sys

# Class init


class CurrencyViewer:
    def __init__(self):
        self.k = krakenex.API()
        self.k.load_key('kraken.key')
        self.currencies = {'fiat': [], 'crypto': []}  # List of different currencies owned by user
        self.market = []  # List of markets concerned by currencies in user's wallet
        self.balance = {'fiat': [], 'crypto': []}
        self.price = {'fiat': [], 'crypto': []}
        self.value = {'fiat': [], 'crypto': []}
        self.eur_total = 0.0

    def process_cv(self) -> object:
        balance_result = self.request_balance()
        self.extract_balances(balance_result)
        self.get_crypto_price_in_eur(self.currencies['crypto'], self.price['crypto'])
        self.process_conversion(self.currencies['crypto'], self.price['crypto'], self.balance['crypto'], self.value['crypto'])
        self.process_conversion(self.currencies['fiat'], self.price['fiat'], self.balance['fiat'], self.value['fiat'])

    # %% Collecting data
    def request_balance(self):
        raw_balance_result = self.k.query_private('Balance')
        if raw_balance_result['error']:
            print("Error : ", raw_balance_result['error'])
            self._exit_error()
        return raw_balance_result['result']

    def extract_balances(self, balance_result):
        self.extract_fiat_balance(balance_result)
        self.extract_crypto_balance(balance_result)

    def extract_fiat_balance(self, balance_result):
        # Extract fiat currencies
        fiat_index = [c for c in balance_result if (c.startswith("Z"))]
        for i in fiat_index:
            self.currencies['fiat'].append(i[1:])       # removing the leading Z
            self.balance['fiat'].append(float(balance_result[i]))
            self.price['fiat'].append(1.0)
            self.value['fiat'].append(0.0)

    def extract_crypto_balance(self, balance_result):
        crypto_owned = [c for c in balance_result if (not c.startswith("Z"))]
        # We get every symbols except the ones which starts with "Z" (these are fiat currencies)
        # print (crypto_owned)
        if not crypto_owned:
            self._empty_wallet_error()

        for i in crypto_owned:
            if i.startswith("X"):
                self.currencies['crypto'].append(i[1:]+"EUR")   # Strip the leading X
            else:
                self.currencies['crypto'].append(i+"EUR")
            if float(balance_result[i]) < 0.000001:
                self.balance['crypto'].append(0.0)          # here we clip small amounts
            else:
                if "TRX" in i:                              # for the TRX in the ledger (must fix this some time to read a static file with ledger entries)
                    self.balance['crypto'].append(float(balance_result[i]) + 7999.0)
                else:
                    self.balance['crypto'].append(float(balance_result[i]))
            self.price['crypto'].append(0.0)                # Seed the price with 0 so that we can update it later
            self.value['crypto'].append(0.0)                # Seed the value with 0 so that we can update it later

# ********************************************************************************

    def get_crypto_price_in_eur(self, crypto_owned, crypto_price):
        market_index = 0
        while market_index < len(crypto_owned):
            # We use a while loop because the for loop doesn't allow us to modify market_index during iteration
            market_data = self.extract_market_data(crypto_owned[market_index])
            if market_data:
                crypto_price[market_index] = float(self.update_market_price(market_data))
            market_index += 1

    def extract_market_data(self, market):
        data = self.k.query_public('Ticker', {'pair': market, })
        if data['error']:
            print(data['error'][0])
            self._public_query_error(data)
            return False
        return data

    @staticmethod
    def update_market_price(market):
        index = list(market['result'].keys())[0]
        return market['result'][index]['c'][0]

# ********************************************************************************

    def process_conversion(self, crypto_owned, crypto_price, crypto_balance, crypto_value):

        for i in range(len(crypto_owned)):
            crypto_value[i] = float(crypto_price[i]) * float(crypto_balance[i])
            self.eur_total = self.eur_total + crypto_value[i]

# ********************************************************************************

# Exit error handling functions
    @staticmethod
    def _exit_error():
        sys.exit("Can't continue with error")

    def _public_query_error(self, response_with_error):
        print(response_with_error['error'][0])

        if response_with_error['error'][0] == "EQuery:Invalid asset pair" or "EQuery:Unknown asset pair":
            print("Check market list, this pair doesn't exist on Kraken exchange."
                  " This market won't be added in market data.")
        else:
            # We leave the program if this is not an Invalid asset pair error
            self._exit_error()

    @staticmethod
    def _empty_wallet_error():
        sys.exit("Your wallet seem empty, please check your API keys or your Kraken dashboard.")

    @staticmethod
    def _crypto_in_market_error():
        sys.exit("Error while getting a crypto ticker from market dict file")
