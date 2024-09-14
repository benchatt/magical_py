import random
import json

HEXAGRAM_FILE = "hexagrams.json"
YIJING_FILE = "yijing.json"

def roll_with_zero(n: int) -> int:
    return random.randint(0,n)

def yarrow_split(pile: int) -> int:
    prep_total = pile - 1
    split_total = 1
    while prep_total:
        step_size = 10 if prep_total > 10 else prep_total
        split_total += roll_with_zero(step_size)
        prep_total -= step_size
    return (split_total, pile - split_total)

class HexagramLine:
    def __init__(self):
        # Yarrow-stalk randomization method
        draw = 49
        observer = 1
        counts = []
        for _ in range(3):
            points = 0
            (left, right) = yarrow_split(draw)
            right -= 1
            points += 1
            drawn = left % 4
            if drawn == 0:
                drawn = 4
            discard = left - drawn
            points += drawn
            drawn = right % 4
            if drawn == 0:
                drawn = 4
            discard += (right - drawn)
            points += drawn
            counts.append(points)
            draw = discard
        tally = sum([3 if n < 6 else 2 for n in counts])
        self.yang = tally % 2 # yang is 1, yin is 0
        print(f"self.yang {self.yang}")


class Hexagram:
    def __init__(self):
        self.lines = [
            HexagramLine(),
            HexagramLine(),
            HexagramLine(),
            HexagramLine(),
            HexagramLine(),
            HexagramLine()
        ]
        self.number = int("".join([str(line.yang) for line in self.lines]), 2) + 1
        if HEXAGRAM_FILE.endswith(".json"):
            hexagrams = json.load(open(HEXAGRAM_FILE))
        idx = next(h for h in hexagrams if hexagrams[h][0] == self.number)
        (_, self.character) = hexagrams[idx]

class Yijing:
    def __init__(self):
        self.hexagram = Hexagram()
        if YIJING_FILE.endswith(".json"):
            yijing = json.load(open(YIJING_FILE))
        self.info = yijing[str(self.hexagram.number)]

    def __repr__(self):
        val = f"{self.info.get('hex')} ({self.hexagram.number})\n"
        val = val + f"{self.info.get('simp')} / {self.info.get('trad')} ({self.info.get('pinyin')})\n"
        val = val + "\nDECISION:\n" + self.info.get("decision")
        val = val + "\n\nINTERPRETATION:\n" + self.info.get("interpretation")
        return val
