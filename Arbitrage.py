import requests
import os
from dotenv import load_dotenv
load_dotenv()

ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')
ALCHEMY_API_URL = f'https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}'

# Token addresses
TOKENS = {
    'WETH': '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
    'DAI': '0x6b175474e89094c44da98b954eedeac495271d0f'
}

# Exchange pool addresses
EXCHANGES = {
    'UniswapV2': '0xa478c2975ab1ea89e8196811f51a7b7ade33eb11',
    'Sushiswap': '0xc3d03e4f041fd4cd388c549ee2a29a9e5075882f',
    'Shebaswap': '0x8faf958e36c6970497386118030e6297fff8d275',
    'Croswap': '0x60a26d69263ef43e9a68964ba141263f19d71d51'
}

# Function to convert wei to ether
def wei_to_ether(wei_value):
    return wei_value / (10 ** 18)

# Function to check for arbitrage opportunities in both directions (WETH <-> DAI)
def check_for_arbitrage(prices, trade_amount):
    arbitrage_opportunities = []

    exchanges = list(prices.keys())
    
    for i in range(len(exchanges)):
        for j in range(len(exchanges)):
            if i != j:
                exchange_sell = exchanges[i]
                exchange_buy = exchanges[j]

                # 1. WETH -> DAI arbitrage
                weth_to_dai_sell = prices[exchange_sell]['WETH_to_DAI']
                dai_to_weth_buy = prices[exchange_buy]['DAI_to_WETH']

                dai_received = weth_to_dai_sell * trade_amount
                dai_used = (trade_amount/dai_to_weth_buy)

                potential_profit_weth = dai_received - dai_used


                if potential_profit_weth > 0:
                    arbitrage_opportunities.append({
                        'direction': 'WETH -> DAI',
                        'sell_exchange': exchange_sell,
                        'buy_exchange': exchange_buy,
                        'profit': potential_profit_weth,
                        'details': f"Sell WETH -> DAI on {exchange_sell} and buy DAI -> WETH on {exchange_buy}"
                    })

                # 2. DAI -> WETH arbitrage
                dai_to_weth_sell = prices[exchange_sell]['DAI_to_WETH']
                weth_to_dai_buy = prices[exchange_buy]['WETH_to_DAI']

                weth_received = dai_to_weth_sell*trade_amount 
                weth_used = (trade_amount/weth_to_dai_buy)

                potential_profit_dai = weth_received - weth_used

                if potential_profit_dai > 0:
                    arbitrage_opportunities.append({
                        'direction': 'DAI -> WETH',
                        'sell_exchange': exchange_sell,
                        'buy_exchange': exchange_buy,
                        'profit': potential_profit_dai,
                        'details': f"Sell DAI -> WETH on {exchange_sell} and buy WETH -> DAI on {exchange_buy}"
                    })

    return arbitrage_opportunities


# Function to generate the data payload for 'balanceOf' function
def generate_data_payload(token_address, exchange_address):
    function_selector = '0x70a08231'
    padded_address = exchange_address[2:].zfill(64)
    return function_selector + padded_address

# Function to get the token balance for a given token and exchange
def get_token_balance(token_address, exchange_address):
    data_payload = generate_data_payload(token_address, exchange_address)
    
    # Create the payload for the API call
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{"data": data_payload, "to": token_address}, "latest"],
        "id": 1
    }
    
    # Make the API request
    response = requests.post(ALCHEMY_API_URL, json=payload, headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        result = response.json()['result']
        # Convert hex result to integer
        return int(result, 16)
    else:
        raise Exception(f"Error: {response.status_code} - {response.text}")

# Function to gather and store token balances
def gather_token_balances():
    balances = {}
    
    for exchange_name, exchange_address in EXCHANGES.items():  
        balances[exchange_name] = {}
      
        for token_name, token_address in TOKENS.items():

            balance = get_token_balance(token_address, exchange_address)
            # Convert balance from wei to ether
            ether_balance = wei_to_ether(balance)
            balances[exchange_name][token_name] = ether_balance
    
    return balances

# Function to calculate the output amount based on reserves, input, and Uniswap fee
def get_amount_out(input_amount, reserve_in, reserve_out):
    fee_adjusted_input = input_amount * 0.997  # Applying the 0.3% fee
    return (fee_adjusted_input * reserve_out) / (reserve_in + fee_adjusted_input)

# Function to calculate the price
def calculate_trade_price(token_reserves):
    prices = {}

    for exchange, reserves in token_reserves.items():
        reserve_weth = reserves['WETH']  # In Ether
        reserve_dai = reserves['DAI']  # In DAI

        # Calculate the amount of DAI out
        dai_out = get_amount_out(1, reserve_weth, reserve_dai)
        
        # Calculate the amount of WETH out
        weth_out = get_amount_out(1, reserve_dai, reserve_weth)

        prices[exchange] = {
            'WETH_to_DAI': dai_out,
            'DAI_to_WETH': weth_out
        }

    return prices


if __name__ == "__main__":
     while(1):
        # Gather data and calculate prices
        balances = gather_token_balances()
        small_trade_size = 0.000001  # Small trade size 

        prices_with_fee = calculate_trade_price(balances)

        # Check for arbitrage opportunities in both directions
        arbitrage_opportunities = check_for_arbitrage(prices_with_fee, small_trade_size)

        with open("arbitrage_opportunities_output.txt", "a") as file:
            # Print the arbitrage results
            if arbitrage_opportunities:
                for arbitrage in arbitrage_opportunities:
                    file.write(f"Arbitrage Opportunity Found! Direction: {arbitrage['direction']}\n")
                    if(arbitrage['direction']=="DAI -> WETH"):
                                file.write(f"Profit: {arbitrage['profit']} WETH\n")
                    else:
                                file.write(f"Profit: {arbitrage['profit']} DAI\n")

                    file.write(f"Details: {arbitrage['details']}")  # Write to file

            else:
                file.write("No arbitrage found.\n")
