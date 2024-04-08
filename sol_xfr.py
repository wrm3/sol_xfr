# Solana Transfers

#<=====>#
# Description
#<=====>#
# Demonstration of sending SOL and SPL Tokens on the Solana Blockchain


#<=====>#
# Known To Do List
#<=====>#



#<=====>#
# Imports - Common Modules
#<=====>#

from termcolor import cprint
from pprint import pprint

import base58
import json
import time


from solana.rpc.api                import Client
from solana.rpc.api                import Keypair
from solana.rpc.api                import RPCException
from solana.rpc.async_api          import AsyncClient
from solana.rpc.commitment         import Commitment
from solana.rpc.commitment         import Confirmed
from solana.rpc.commitment         import Processed
from solana.rpc.types              import TokenAccountOpts
from solana.rpc.types              import TxOpts
from solana.transaction            import AccountMeta
from solana.transaction            import Transaction
from solders                       import message
from solders.compute_budget        import set_compute_unit_limit
from solders.compute_budget        import set_compute_unit_price
from solders.instruction           import Instruction
from solders.keypair               import Keypair
from solders.message               import to_bytes_versioned
from solders.pubkey                import Pubkey
from solders.signature             import Signature
from solders.system_program        import create_account
from solders.system_program        import CreateAccountParams
from solders.system_program        import transfer
from solders.system_program        import TransferParams
from solders.transaction           import VersionedTransaction
from spl.token.client              import Token
from spl.token.constants           import TOKEN_PROGRAM_ID
from spl.token.core                import _TokenCore
from spl.token.instructions        import CloseAccountParams
from spl.token.instructions        import close_account
from spl.token.instructions        import create_associated_token_account
from spl.token.instructions        import get_associated_token_address
from spl.token.instructions        import initialize_account
from spl.token.instructions        import InitializeAccountParams
from spl.token.instructions        import transfer_checked
from spl.token.instructions        import TransferCheckedParams
import spl.token.instructions as spl_token
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
import base58



#<=====>#
# Imports - Download Modules
#<=====>#



#<=====>#
# Imports - Shared Library
#<=====>#



#<=====>#
# Imports - Local Library
#<=====>#



#<=====>#
# Variables
#<=====>#



#<=====>#
# AI Prompt
#<=====>#
'''
AI Prompt This is not the code you are looking for!
'''


#<=====>#
# Constant
#<=====>#

LAMPORTS            = 1_000_000_000
ACCOUNT_SIZE        = 165

#<=====>#
def B(in_str):
	cprint(in_str, 'blue')
def G(in_str):
	cprint(in_str, 'green')
def M(in_str):
	cprint(in_str, 'magenta')
def R(in_str):
	cprint(in_str, 'red')
#<=====>#
def WoB(in_str):
	cprint(in_str, 'white', 'on_blue')
def WoG(in_str):
	cprint(in_str, 'white', 'on_green')
def WoM(in_str):
	cprint(in_str, 'white', 'on_magenta')
def WoR(in_str):
	cprint(in_str, 'white', 'on_red')
#<=====>#


def send_sol(
	src_addr, 
	src_key, 
	dest_addr, 
	amt_sol, 
	cu_prc=400000, 
	cu_lmt=200000, 
	rpc_url='https://api.mainnet-beta.solana.com', 
	show_details_yn='N'
	):
	func_name = 'send_sol'
	func_str = '{}(src_addr={}, src_key=HIDDEN, dest_addr={}, amt_sol={}, rpc_url={})'.format(func_name, src_addr, dest_addr, amt_sol, rpc_url)

	if show_details_yn == 'Y':
		print('')
		WoM(func_str)

	client                    = Client(rpc_url, commitment=Commitment("confirmed"), timeout=30, blockhash_cache=True)
	src_keypair               = Keypair.from_base58_string(src_key)
	src_pubkey                = Pubkey(base58.b58decode(src_addr))
	src_bal                   = client.get_balance(src_pubkey).value / LAMPORTS
	dest_pubkey               = Pubkey(base58.b58decode(dest_addr))
	dest_bal                  = client.get_balance(dest_pubkey).value / LAMPORTS
	send_amt_lamps            = int(amt_sol * LAMPORTS)

	if show_details_yn == 'Y':
		WoG('Before Balances')
		# Show Before Balance in Source Account
		src_bal         = client.get_balance(src_pubkey).value / LAMPORTS
		G('{:<40} : {:>21.8f} SOL'.format('Source Wallet SOL balance', src_bal))
		# Show Before Balance in Destination Account
		dest_bal        = client.get_balance(dest_pubkey).value / LAMPORTS
		G('{:<40} : {:>21.8f} SOL'.format('Destination Wallet SOL balance', dest_bal))

	# fails and warnings check')
	if src_bal < amt_sol:
		msg = 'INSUFFICIENT SOL!!!'
		WoR('{:<40} : {:>21.8f} SOL {:<40}'.format('Source Wallet SOL balance', src_bal, msg))
		return 'FAIL'
	if src_bal - amt_sol < 0.01:
		msg = 'LOW SOL BALANCE WARNING'
		WoR('{:<40} : {:>21.8f} SOL {:<40}'.format('Source Wallet SOL balance', src_bal, msg))

	blockhash                 = client.get_latest_blockhash().value.blockhash

	txn                       = Transaction(fee_payer=src_pubkey, recent_blockhash=blockhash)
	txn.add(
		transfer(
			TransferParams(
				from_pubkey   = src_pubkey,
				to_pubkey     = dest_pubkey,
				lamports      = send_amt_lamps
			)
		)
	)

	# Priority Fees, remove when no network congestion
	# these were the seeings from 4/5/2024 for trades to do through 
	# adjust as needed
	txn.add(set_compute_unit_price(cu_prc))  # Compute Unit Price
	txn.add(set_compute_unit_limit(cu_lmt)) #Compute Unit Limit

	response = client.send_transaction(txn, src_keypair)
	resp     = response.to_json()
	r        = json.loads(resp)

	txn_hash = type(r['result'])
	txn_hash = r['result']

	if show_details_yn == 'Y':
		print('https://solscan.io/tx/{}'.format(txn_hash))

	return txn_hash


#<=====>#


def send_tkn(
	src_addr, 
	src_key, 
	dest_addr, 
	tkn_addr, 
	tkn_amt=None, 
	send_max=False, 
	cu_prc=400000, 
	cu_lmt=200000, 
	rpc_url='https://api.mainnet-beta.solana.com', 
	show_details_yn='N'
	):
	func_name = 'send_tkn'
	func_str = '{}(src_addr={}, src_key=HIDDEN, dest_addr={}, tkn_addr={}, tkn_amt={}, rpc_url={})'.format(func_name, src_addr, dest_addr, tkn_addr, tkn_amt, rpc_url)

	if show_details_yn == 'Y':
		print('')
		WoM(func_str)

	txn_hash = 'FAIL'

	try:
		if not send_max and not tkn_amt:
			WoR('when send_max is False, please populate tkn_amt...')
			return 'FAIL'

		# building client
		client                    = Client(rpc_url, commitment=Commitment("confirmed"), timeout=30, blockhash_cache=True)
		# token pubkey
		tkn_pubkey                = Pubkey(base58.b58decode(tkn_addr))
		# source wallet pubkey & keypair
		src_keypair               = Keypair.from_base58_string(src_key)
		src_pubkey                = Pubkey(base58.b58decode(src_addr))
		# desination wallet pubkey & keypair
		dest_pubkey               = Pubkey(base58.b58decode(dest_addr))
		# blockhash
		blockhash        = client.get_latest_blockhash().value.blockhash
		# building transaction...
		txn = Transaction(fee_payer=src_pubkey, recent_blockhash=blockhash)
		# building spl token client
		spl_client = Token(conn=client, pubkey=tkn_pubkey, program_id=TOKEN_PROGRAM_ID, payer=src_keypair)


		# source wallet sol balance
		src_bal                   = client.get_balance(src_pubkey).value / LAMPORTS
		# destination wallet sol balance
		dest_bal                  = client.get_balance(dest_pubkey).value / LAMPORTS


		# source wallet token acct & details
		src_tkn_data              = get_tkn_acct(src_addr, tkn_addr)
#		pprint(src_tkn_data)
		tkn_dec                   = src_tkn_data['tkn_dec']
		src_tkn_bal               = src_tkn_data['tkn_bal']
		src_tkn_acct_pubkey       = src_tkn_data['tkn_acct_pubkey']
		if send_max:
			tkn_amt = src_tkn_bal
		# fails and warnings check
		if not src_tkn_acct_pubkey:
			msg = 'Source Account Does Not Have That Token!!!'
			WoR('{:<40}'.format(msg))
			return 'FAIL'
		if tkn_amt > src_tkn_bal:
			msg = 'Source Account Does Not Have Enough That Token!!!'
			WoR('{:<40} : {:>21.8f} SOL {:<40}'.format('Source Wallet TKN balance', tkn_amt, msg))
			return 'FAIL'
		if src_bal < 0.01:
			msg = 'LOW SOL BALANCE WARNING'
			WoR('{:<40} : {:>21.8f} SOL {:<40}'.format('Source Wallet SOL balance', src_bal, msg))

		# Calculating Send Amount in Token Specific Lamports
		send_amt_lamps            = int(tkn_amt * 10**tkn_dec)

		# destination wallet token acct & details
		dest_tkn_data             = get_tkn_acct(dest_addr, tkn_addr)
#		pprint(dest_tkn_data)
		dest_tkn_bal              = dest_tkn_data['tkn_bal']


		# Before balances
		if show_details_yn == 'Y':
			print('')
			print('')
			WoG('Before Balances')
			# Show Before Balance in Source Account
			G('{:<40} : {:>21.8f} {:<8}'.format('Source Wallet {:<8} balance'.format('SOL'), src_bal, 'SOL'))
			G('{:<40} : {:>21.8f} {:<8}'.format('Source Wallet {:<8} balance'.format('TKN'), src_tkn_bal, 'TKN'))
			# Show Before Balance in Destination Account
			G('{:<40} : {:>21.8f} {:<8}'.format('Destination Wallet {:<8} balance'.format('SOL'), dest_bal, 'SOL'))
			G('{:<40} : {:>21.8f} {:<8}'.format('Destination Wallet {:<8} balance'.format('TKN'), dest_tkn_bal, 'TKN'))


		# destination wallet token acct build if not exists...
		if dest_tkn_data['tkn_acct_pubkey']:
			dest_tkn_acct_pubkey  = dest_tkn_data['tkn_acct_pubkey']
		else:
			print('==> creating destination wallet token account pubkey')
			dest_tkn_acct_pubkey = create_assoc_tkn_acct(payer = src_keypair, owner = dest_pubkey, mint = tkn_pubkey, cu_prc=cu_prc, cu_lmt=cu_lmt)


		# building transfer instructions..
		xfr_ins = transfer_checked(
			TransferCheckedParams(
				program_id              = TOKEN_PROGRAM_ID,
				source                  = src_tkn_acct_pubkey,
				mint                    = tkn_pubkey,
				dest                    = dest_tkn_acct_pubkey,
				owner                   = src_pubkey,
				amount                  = send_amt_lamps,
				decimals                = tkn_dec
#				signers                 = [src_keypair,src_keypair,src_keypair]
			)
		)
		# adding transfer instructions..
		txn.add(xfr_ins)

		# Priority Fees, remove when no network congestion
		# these were the seeings from 4/5/2024 for trades to do through 
		# adjust as needed
		# adding priority fees...
		txn.add(set_compute_unit_price(cu_prc))  # Compute Unit Price
		txn.add(set_compute_unit_limit(cu_lmt)) #Compute Unit Limit

		time.sleep(1)
		# sending transaction...
		resp = client.send_transaction(txn, src_keypair, opts=TxOpts(skip_preflight=True, preflight_commitment='confirmed'))

		# deriving txn_hash...
		resp = resp.to_json()
		r = json.loads(resp)
		txn_hash = r['result']

		if show_details_yn == 'Y':
			print('https://solscan.io/tx/{}'.format(txn_hash))

	except Exception as e:
		print(func_str)
		print(type(e))
		print(e)

	return txn_hash


#<=====>#


def create_assoc_tkn_acct(payer: Keypair, owner: Pubkey, mint: Pubkey, cu_prc=400000, cu_lmt=200000) -> Pubkey:
	client = Client("https://api.mainnet-beta.solana.com")
	txn = Transaction()
	create_txn = spl_token.create_associated_token_account(payer=payer.pubkey(), owner=owner, mint=mint)
	txn.add(create_txn)

	# Priority Fees, remove when no network congestion
	# these were the seeings from 4/5/2024 for trades to do through 
	# adjust as needed
	txn.add(set_compute_unit_price(cu_prc))  # Compute Unit Price
	txn.add(set_compute_unit_limit(cu_lmt)) #Compute Unit Limit
	client.send_transaction(txn, payer, opts=TxOpts(skip_confirmation=False, preflight_commitment=Confirmed))
#	print(type(create_txn))
#	print(create_txn)

	return create_txn.keys[1].pubkey


#<=====>#


def get_tkn_acct(wallet_addr, tkn_addr):
#	func_name = 'get_tkn_acct'
#	func_str = '{}(wallet_addr={}, tkn_addr={})'.format(func_name, wallet_addr, tkn_addr)
#	B(func_str)

	# Initialize Solana RPC client
	client = Client("https://api.mainnet-beta.solana.com")

	data = {}
	data['tkn_acct_pubkey']   = None
	data['tkn_bal']           = 0
	data['tkn_bal_raw']       = 0
	data['tkn_dec']           = 0

	# Wallet public key (replace with the actual wallet public key)
	wallet_pubkey   = Pubkey(base58.b58decode(wallet_addr))

	# Token mint address (replace with the actual token mint address)
	tkn_pubkey      = Pubkey(base58.b58decode(tkn_addr))

	try:
		time.sleep(1)
		tkn_acct_data    = client.get_token_accounts_by_owner(wallet_pubkey, TokenAccountOpts(tkn_pubkey))
		tkn_acct_pubkey  = tkn_acct_data.value[0].pubkey
		data['tkn_acct_pubkey'] = tkn_acct_pubkey
		# Initialize token client
		token = Token(
			conn         = client,
			pubkey       = tkn_pubkey,
			program_id   = TOKEN_PROGRAM_ID,
			payer        = client
		)
		# Get token balance for the wallet
		r = token.get_balance(tkn_acct_pubkey)
		data['tkn_bal']     = r.value.ui_amount
		data['tkn_bal_raw'] = r.value.amount
		data['tkn_dec']     = r.value.decimals
	except Exception as e:
		return data

	return data


#<=====>#


