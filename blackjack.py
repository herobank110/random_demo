"""Blackjack simulator
"""
import itertools
from collections import defaultdict
import random
import time
import statistics


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
        if sum_a11(hands[player]) == 21:
            if dealer_sum < 10:
                results['win'] += 1
                results['invested'] += bets[player]
                results['winnings'] += bets[player] * 1.5
                results['pot'] += bets[player] * 2.5
                hands[player] = None
            elif dealer_sum == 11:
                # even money
                results['win'] += 1
                results['invested'] += bets[player]
                results['winnings'] += bets[player]
                results['pot'] += bets[player] * 2
                hands[player] = None

    for player in range(players):
        if hands[player] is None:
            continue
        player_sum = sum_a11(hands[player])
        # double bet
        # if 10 <= player_sum <= 11 and dealer_sum < 11:
        #     bets[player] *= 2
        if player_sum >= 13 or player_sum >= 12 and dealer_sum >= 4:
        # if player_sum >= 16:
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
    games = 170_000
    batches = 10
    bet_per_game = 1
    players = 1
    ratio = lambda results: results['pot'] / results['invested']  # noqa
    ratio_samples = []
    batch_results = defaultdict(int)
    for i in range(games):
        simulate(cards, bets=[bet_per_game] * players, players=players, results=batch_results)
        if i % 8 == 0:
            random.shuffle(cards)
        if i % (games // batches) == ((games // batches) // 2):
            ratio_samples.append(ratio(batch_results))
            for key in batch_results:
                results[key] += batch_results[key]
            batch_results = defaultdict(int)

    print(f"     Games: {games}")
    print(f"      Time: {(time.time_ns() - start) / 1_000_000_000:.3f}s")
    print(f"      Wins: {results['win']}")
    print(f"    Losses: {results['lose']}")
    print(f"    Pushes: {results['push']}")
    print(f"     Busts: {results['bust']}")
    print(f"  Invested: {results['invested']}")
    print(f"  Winnings: {results['winnings']}")
    print(f"       Pot: {results['pot']}")
    print(f"House Edge: {1 - (results['win'] + results['push']) / (results['lose'] + results['bust']):.4f}")
    print(f"     Ratio: {ratio(results):.4f} (min: {min(ratio_samples):.4f}, max: {max(ratio_samples):.4f}, mean: {statistics.mean(ratio_samples):.4f}, σ: {statistics.stdev(ratio_samples):.4f})")


if __name__ == '__main__':  
    main()
