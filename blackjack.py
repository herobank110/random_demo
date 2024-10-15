"""Blackjack simulator
"""
import itertools
from collections import defaultdict
import random
import time


def simulate(cards, bets, players, results):
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
    dealer_sum = sum_a11(dealer)

    # payout for blackjack
    for player in range(players):
        # 3:2 payout for blackjack
        if sum_a11(hands[player]) == 21:
            results['win'] += 1
            results['invested'] += bets[player]
            results['winnings'] += bets[player] * 1.5
            results['pot'] += bets[player] * 2.5
            hands[player] = None

    for player in range(players):
        if hands[player] is None:
            continue
        player_sum = sum_a11(hands[player])
        # double bet
        if 10 <= player_sum <= 11 and dealer_sum < 11:
            bets[player] *= 2
        if player_sum >= 17 or player_sum >= 12 and dealer_sum >= 7:
            break
        hands[player].append(draw())

    while sum_a11(dealer) < 17:
        dealer.append(draw())
    
    dealer_sum = sum_a11(dealer)
    for player in range(players):
        if hands[player] is None:
            continue
        player_sum = sum_a11(hands[player])
        bet = bets[player]
        results['invested'] += bet
        if player_sum > 21:
            results['bust'] += 1
            # results['pot'] -= bet
        elif dealer_sum > 21 or player_sum > dealer_sum:
            results['win'] += 1
            results['winnings'] += bet
            results['pot'] += bet * 2
        elif player_sum == dealer_sum:
            results['push'] += 1
            results['pot'] += bet
        else:
            results['lose'] += 1


def get_cards(decks):
    return list(range(2, 14)) * 4 * decks


def main():
    start = time.time_ns()
    results = defaultdict(int)
    cards = get_cards(decks=8)
    games = 100_000
    bet_per_game = 1
    players = 1
    for i in range(games):
        simulate(cards, bets=[bet_per_game] * players, players=players, results=results)
        if i % 4 == 0:
            random.shuffle(cards)

    print(f"Games: {games}")
    print(f"Time: {(time.time_ns() - start) / 1_000_000} ms")
    print("")
    print(f"Win:  {results['win']: 6d}")
    print(f"Lose: {results['lose']: 6d}")
    print(f"Push: {results['push']: 6d}")
    print(f"Bust: {results['bust']: 6d}")
    print(f"  Invested: {results['invested']}")
    print(f"  Winnings: {results['winnings']}")
    print(f"       Pot: {results['pot']}")
    ratio = results['pot'] / results['invested']
    print(f"     Ratio: {ratio:.4f}")
    # print(f"House Edge: {1 - ratio:.4f}")


if __name__ == '__main__':  
    main()
