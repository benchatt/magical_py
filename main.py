import random
from modules.cards import TarotDeck, ObliqueDeck, EmojiDeck
from modules.world import Day, Year
from modules.yarrow import Yijing
from modules.numbers import Lotto

def tarot_pull(topics) -> dict:
    deck = TarotDeck()
    for _ in range(3):
        deck.shuffle()
    deck.cut()
    for _ in range(4):
        deck.shuffle()
    deck.cut()
    for topic in topics:
        print(f"{topic}:")
        this_card = deck.deal()
        print(f"  {this_card}")
        print(f"  {this_card.note}")

def date_and_season():
    print(Day())
    print(Year())

def yijing_draw():
    print(Yijing())

def oblique_draw():
    print("================\n")
    print("Oblique Strategy")
    deck = ObliqueDeck()
    deck.setup_shuffle()
    print(f"  {deck.deal()}\n")
    print("================\n")

def emoji_draw():
    deck = EmojiDeck()
    print("================\n")
    print(f"Your upcoming challenge : {deck.deal()} {deck.deal()}, {deck.deal()}")
    print(f"What you need to face it: {deck.deal()} {deck.deal()}, {deck.deal()}")
    print(f"A warning as you proceed: {deck.deal()} {deck.deal()}, {deck.deal()}")
    print("================\n")

def lotto_draw():
    lotto = Lotto()
    print("================\n")
    print("\n'Lucky numbers' do not imply any guarantee of winning.")
    print("Numbers are generated with Python's `random` library.")
    print(lotto)
    print("================\n")

if __name__ == "__main__":
    random.seed()
    date_and_season()
    print()
    tarot_pull(
        ["self", "love", "work", "kids", "hobbies"]
    )
    print()
    yijing_draw()
    oblique_draw()
    emoji_draw()
    lotto_draw()
