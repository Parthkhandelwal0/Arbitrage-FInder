### OBJECTIVE

- this script finds arbitrage opportunites between multiple exchanges

## Files/Folders

- Arbitrage.py
  Main script file to run
- .env.example
  .env example file to replace the Alchemy API KEY

## RUNNING THE SCRIPT

- rename `.env.example` file with `.env` and add the Alchemy API key
- install `dotenv` and `requests` modules
- run `python Arbitrage.py`

## Script Overview

# Token and Exchange Definitions

    TOKENS: A dictionary storing the contract addresses for the tokens involved, specifically WETH and DAI.
    EXCHANGES: A dictionary holding the contract addresses of liquidity pools from various decentralized exchanges.

# Functions

- wei_to_ether(wei_value)
  This function converts value from wei (the smallest unit of Ethereum) to ether

- check_for_arbitrage(prices, trade_amount)
  This function checks for arbitrage opportunities between the provided exchanges. It compares the WETH-to-DAI and DAI-to-WETH prices for each exchange pair. It computes the potential profit based on trade sizes and lists any found arbitrage opportunities.
  Inputs:
  prices: A dictionary containing the current prices for WETH and DAI on each exchange.
  trade_amount: The trade size to check for arbitrage (e.g., 1 WETH).
  Output:
  A list of arbitrage opportunities found, including the direction of trade (WETH -> DAI or DAI -> WETH) and the profit.

- generate_data_payload(token_address, exchange_address)
  Generates the necessary payload for the Ethereum eth_call to fetch token balances from smart contracts.
  Inputs:
  token_address: The contract address of the token (WETH or DAI).
  exchange_address: The address of the exchange's liquidity pool.
  Output:
  A data payload formatted for the Ethereum eth_call method to retrieve balances.

- get_token_balance(token_address, exchange_address)
  This function retrieves the token balance for a specific exchange using the Ethereum blockchain's eth_call method via the Alchemy API.

  Inputs:
  token_address: The token (WETH or DAI) contract address.
  exchange_address: The exchange pool's contract address.
  Output:
  The balance of the token at the specified exchange, converted from hexadecimal format into an integer.

- gather_token_balances()
  Collects and stores the balances of WETH and DAI for all exchanges in the EXCHANGES dictionary. It loops over each exchange and token, calling get_token_balance() and converting the results from wei to ether.

  Output:
  A dictionary containing the token balances for WETH and DAI on each exchange.

- get_amount_out(input_amount, reserve_in, reserve_out)

  Calculates the output token amount for a trade based on Uniswap's constant product formula, taking into account a 0.3% trading fee.

  Inputs:
  input_amount: The amount of the input token to trade.
  reserve_in: The reserve amount of the input token in the liquidity pool.
  reserve_out: The reserve amount of the output token in the liquidity pool.
  Output:
  The amount of the output token received after trading fees.

- calculate_trade_price(token_reserves)

  This function calculates the price for small trades (e.g., 1 WETH) on each exchange using the token reserves obtained from the blockchain. It takes into account the Uniswap-style fee (0.3%).

  Inputs:
  token_reserves: The reserves of WETH and DAI for each exchange.
  Output:
  A dictionary containing the trade prices (WETH -> DAI and DAI -> WETH) for each exchange.

## Pricing Calculation

This script uses the Uniswap V2 pricing formula to calculate the trading price of tokens.

The formula for calculating the output amount when swapping token A for token B is:
`output amount=(input amount×(1−fee)×reserve B)/(reserve A+input amount×(1−fee))`

Where:

    Input amount: The amount of the input token you want to swap.
    Fee: Uniswap applies a 0.3% fee
    Reserve A: The amount of the input token in the liquidity pool.
    Reserve B: The amount of the output token in the liquidity pool.

This formula ensures that larger swaps have a diminishing return, maintaining a balance between token reserves according to the constant product formula:
`reserve A×reserve B=constant`
