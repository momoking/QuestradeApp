import requests
import json
from terminaltables import AsciiTable

class App(object):

	def __init__(self):
		self.URL_AUTH = "https://login.questrade.com/oauth2/token?grant_type=refresh_token&refresh_token="
		self.HOST = 'will-be-determined'
		self.REFRESH_TOKEN = 'put-it-in-file'
		self.ACCESS_TOKEN = 'will-be-determined'

	def read_refresh_token_file (self):
		with open('refresh_token', 'r') as f:
			first_line = f.readline().strip()
			f.close()
			print 'token from file:' + first_line
		self.REFRESH_TOKEN = first_line		
		
	def write_refresh_token_file (self):
		with open('refresh_token', 'w') as f:
			f.write(self.REFRESH_TOKEN)
			f.close()

	def refresh_token (self):
		# get refresh token
		self.read_refresh_token_file()
		url = self.URL_AUTH + self.REFRESH_TOKEN
		print 'refresh_token: ' + url
		response = requests.post(url).json()
		# print json.dumps(response, indent=4)
		# update values
		self.HOST = response.get('api_server')
		self.REFRESH_TOKEN = response.get('refresh_token')
		self.ACCESS_TOKEN = response.get('access_token')
		# write the new refresh back to file
		self.write_refresh_token_file()

	def get_headers (self):
		return {"Authorization":"Bearer " + self.ACCESS_TOKEN}

	def get_accounts (self):
		url = self.HOST + 'v1/accounts/'
		print 'get_accounts: ' + url
		response = requests.get(url, headers=self.get_headers())
		return response

	def get_account_balance (self, account_number):
		url = self.HOST + 'v1/accounts/' + account_number + "/balances/"
		print 'get_account_balance: ' + url
		response = requests.get(url, headers=self.get_headers())
		return response

	def print_account_summary(self):
		table_data = [
			['Account Number', 'Type', 'Currency', 'Cash', 'Market Value', 'Total Equity']    
		]
		accounts_response=self.get_accounts().json()
		accounts=accounts_response.get('accounts')
		for account in accounts:
			account_number = account.get('number')
			account_type = account.get('type')			
			account_balance_response=self.get_account_balance(account_number).json()
			account_currency_balances = account_balance_response.get('perCurrencyBalances')
			for account_currency_balance in account_currency_balances:
				cash = account_currency_balance.get('cash')
				marketValue = account_currency_balance.get('marketValue')
				totalEquity = account_currency_balance.get('totalEquity')
				account_currency = account_currency_balance.get('currency')
				row = [account_number, account_type, account_currency, str(cash), str(marketValue), str(totalEquity)]
				table_data.append(row)
		asciiTable = AsciiTable(table_data)
		print asciiTable.table

app = App()
app.refresh_token()
app.print_account_summary()
