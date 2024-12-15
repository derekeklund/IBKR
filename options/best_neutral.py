


'''
Select an optimal straddle/strangle

TODO to have this integrated strategy
1. create an instance of the ChainReader class
2. call read_option_chain() [chain_reader.py] to get current option chain (1st ARGUMENT to best_neutral())
3. call compute_probabilities() [best_spread.py] to populate the beliefs dictionary which associates stockprices with their estimated probabilities (2nd ARGUMENT)
4. populate a list called spreads with the straddle and strangles that can be purchased from the options chain. Each element of the list is a tuple of strike prices (3rd ARGUMENT)
5. call best_neutral()
'''

def best_neutral(probs, chain, spreads):

    profits = []
    max_profit = -1000.0
    max_index = -1
    for i, spread in enumerate(spreads):

        # Strike prices and premiums
        K1 = spread[0]
        K2 = spread[1]
        P1 = chain[K1]['P']['ask_price']
        P2 = chain[K2]['C']['ask_price']

        # Iterate through probabilities
        profit = 0.0
        for belief in probs:

            if belief < K1:
                profit += ((K1 - belief) - (P1 + P2)) * probs[belief]/(P1 + P2)
            elif belief > K2:
                profit += ((belief - K2) - (P1 + P2)) * probs[belief](P1 + P2)
            else:
                profit += -(P1 + P2) * probs[belief]/(P1 + P2)

        # Check for spread with maximum profit
        profits.append(profit)
        if profit > max_profit:
            max_profit = profit
            max_index = i

    return max_profit, max_index
