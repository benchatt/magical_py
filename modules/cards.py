import random
import logging
import yaml

SPLIT_LAYER_SIZE = 4.0
WIKI_URL = "https://en.wikipedia.org/wiki/"
OBLIQUE_LOC = "data/obliques.yaml"

random.seed()

def digit_to_name(n: int) -> str:
    return [
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
        "eleven",
        "twelve",
        "thirteen"
    ][n]

class Card:
    def __init__(self, value, kind=None, note=None):
        self.value = value
        self.kind = kind
        self.orientation = 0
        self.note = note

    def __repr__(self):
        turned = "" if self.orientation == 0 else "†"
        if not self.kind:
            return self.value + turned
        else:
            name = f"{self.value} of {self.kind}"
            return name + turned

    def turn(self):
        self.orientation = 1 - self.orientation

    def french_card_value(self):
        suit = 0 if not self.kind else 0.1 * "♣♢♡♠".index(self.kind)
        try:
            rank = int(self.value)
        except ValueError:
            if "joker" in self.value.lower():
                rank = 0
            elif self.value.lower().startswith("a"):
                rank = 1
            else:
                rank = 10 + "xjqk".index(self.value[0].lower())
        return suit + rank


class Deck:
    def __init__(self):
        self.values = []
        self.discard = []

    def _chunk(self):
        return random.randint(0,1) + random.randint(0,2) + random.randint(1,2)

    def split_(self) -> tuple:
        # Find reasonable split point
        deck_size = len(self.values)
        roll_layers = int(round(deck_size / SPLIT_LAYER_SIZE, 0))
        split_point = sum(random.randint(1, int(round(SPLIT_LAYER_SIZE,0))) for _ in range(roll_layers))
        left_hand = self.values[:split_point]
        right_hand = self.values[split_point:]
        return (left_hand, right_hand)

    def shuffle(self):
        (left_hand, right_hand) = self.split_()
        self.values = []
        if random.randint(0,1):
            for card in left_hand:
                card.turn()
        else:
            for card in right_hand:
                card.turn()
        while left_hand or right_hand:
            for _ in range(self._chunk()):
                if left_hand:
                    self.values.append(left_hand.pop())
            for _ in range(self._chunk()):
                if right_hand:
                    self.values.append(right_hand.pop())
            logging.info(f"Left: {len(left_hand)}, Right: {len(right_hand)}, Main: {len(self.values)}")
        logging.info("-----")
        self.values.reverse()

    def cut(self):
        (left_hand, right_hand) = self.split_()
        self.values = right_hand
        self.values.extend(left_hand)

    def deal(self, n=1) -> Card:
        try:
            dealt = self.values.pop()
            self.discard.append(dealt)
        except IndexError:
            dealt = None
        return dealt

    def reset(self):
        self.values.extend(self.discard)
        self.discard = []
        self.shuffle()

class TarotDeck(Deck):
    def __init__(self):
        super().__init__()
        suits = ["Cups", "Coins", "Wands", "Swords"]
        values = range(1,15)
        specials = [
            (1, "Ace"),
            (11, "Page"),
            (12, "Knight"),
            (13, "Queen"),
            (14, "King")
        ]
        majors = [
            ("0", "The Fool"),
            ("I", "The Magician"),
            ("II", "The High Priestess"),
            ("III", "The Empress"),
            ("IV", "The Emperor"),
            ("V", "The Hierophant"),
            ("VI", "The Lovers"),
            ("VII", "The Chariot"),
            ("VIII", "Justice"),
            ("IX", "The Hermit"),
            ("X", "Wheel of Fortune"),
            ("XI", "Strength"),
            ("XII", "The Hanged Man"),
            ("XIII", "Death"),
            ("XIV", "Temperance"),
            ("XV", "The Devil"),
            ("XVI", "The Tower"),
            ("XVII", "The Star"),
            ("XVIII", "The Moon"),
            ("XIX", "The Sun"),
            ("XX", "Judgement"),
            ("XXI", "The World")
        ]
        do_not_annotate = ["The High Priestess", "The Hierophant"]
        special_vals = [s[0] for s in specials]
        for value in values:
            try:
                special_loc = special_vals.index(value)
            except ValueError:
                special_loc = None
            for suit in suits:
                v = value
                if special_loc is not None:
                    v = specials[special_loc][1]
                card = Card(v, suit)
                if special_loc is not None:
                    longname = repr(card)
                else:
                    longname = repr(card).replace(str(card.value), digit_to_name(card.value).title())
                card.note = WIKI_URL + longname.replace(" ", "_")
                card.orientation = random.randint(0,1)
                self.values.append(card)
        for major in majors:
            card = Card(f"{major[0]} - {major[1]}")
            if major[1] in do_not_annotate:
                card.note = WIKI_URL + major[1].replace(" ", "_")
            else:
                card.note = WIKI_URL + major[1].replace(" ", "_") + "_(tarot_card) "
            card.orientation = random.randint(0,1)
            self.values.append(card)
        random.shuffle(self.values)

class ObliqueDeck(Deck):
    def __init__(self):
        super().__init__()
        with open(OBLIQUE_LOC) as fh:
            prompts = yaml.safe_load(fh)
        for prompt in prompts:
            self.values.append(Card(prompt))

    def setup_shuffle(self):
        for _ in range(4):
            self.shuffle()
        self.cut()
        for _ in range(4):
            self.shuffle()
        self.cut()
        for card in self.values:
            card.orientation = 0
