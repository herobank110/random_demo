"""Blackjack simulator
"""
import itertools
from collections import defaultdict
import random
import time


def simulate(cards, players, results):
    hands = [[] for _ in range(players)]
    dealer = []

    def draw():
        card = cards.pop(0)
        cards.append(card)  # TODO: change to collect cards at end by adding players cards then dealer cards
        return card

    def sum_a11(hand):
        total = sum(hand)
        if 1 in hand and total + 10 <= 21:
            return total + 10
        return total

    for _ in range(2):
        for player in range(players):
            hands[player].append(draw())

    dealer.append(draw())
    for player in range(players):
        player_sum = sum_a11(hands[player])
        if player_sum >= 17 or player_sum >= 12 and sum_a11(dealer) >= 7:
            break
        hands[player].append(draw())

    while sum_a11(dealer) < 17:
        dealer.append(draw())
    
    dealer_sum = sum_a11(dealer)
    for player in range(players):
        player_sum = sum_a11(hands[player])
        if player_sum > 21:
            results['bust'] += 1
        elif dealer_sum > 21 or player_sum > dealer_sum:
            results['win'] += 1
        elif player_sum == dealer_sum:
            results['push'] += 1
        else:
            results['lose'] += 1


def get_cards(decks):
    return list(range(2, 14)) * 4 * decks


def main():
    start = time.time_ns()
    results = defaultdict(int)
    cards = get_cards(decks=8)
    games = 100_000
    for i in range(games):
        simulate(cards, players=1, results=results)
        if i % 4 == 0:
            random.shuffle(cards)

    print(f"Games: {games}")
    print(f"Time: {(time.time_ns() - start) / 1_000_000} ms")
    print("")
    print(f"Win:  {results['win']: 6d}")
    print(f"Lose: {results['lose']: 6d}")
    print(f"Push: {results['push']: 6d}")
    print(f"Bust: {results['bust']: 6d}")
    print("")
    bet_per_game = 1
    invested = bet_per_game * games
    left_with = bet_per_game * results['win'] * 2 + bet_per_game * results['push'] - bet_per_game * results['bust'] - bet_per_game * results['lose']
    print(f"Invested:  {invested: 6d}")
    print(f"Left with: {left_with: 6d}")
    print(f"Profit:    {left_with - invested: 6d} ({(left_with - invested) / invested * 100:.2f}%)")


if __name__ == '__main__':  
    main()
