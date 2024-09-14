import logging
from ..modules import cards

def test_tarot_visual():
    deck = cards.TarotDeck()
    for _ in range(4):
        deck.shuffle()
    deck.cut()
    for _ in range(3):
        deck.shuffle()
    deck.cut()
    for _ in range(20):
        logging.info(deck.deal())
