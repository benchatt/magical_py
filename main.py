import random
from modules.cards import TarotDeck, ObliqueDeck
from modules.world import Day, Year
from modules.yarrow import Yijing

def tarot_pull(topics) -> dict:
    random.seed()
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
    print(f"  {deck.deal()}")

if __name__ == "__main__":
    date_and_season()
    print()
    tarot_pull(
        ["self", "love", "work", "kids", "hobbies"]
    )
    print()
    yijing_draw()
    oblique_draw()
