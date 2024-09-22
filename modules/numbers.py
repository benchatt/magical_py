import random

FORMATS = {
    "Powerball": [69, 69, 69, 69, 69, 26],
    "MegaMillions": [70, 70, 70, 70, 70, 25],
    "SuperEnalotto-IT": [90] * 6,
    "EuroMillions": [50, 50, 50, 50, 50, 12, 12],
    "EuroJackpot": [50, 50, 50, 50, 50, 12, 12],
    "National Lottery-UK": [59] * 6,
    "La Primitiva-ES": [49, 49, 49, 49, 49, 49, 10],
    "Mega-Sena-BR": [60] * 15,
    "Powerball-AU": [40, 40, 40, 40, 40, 40, 20],
    "Ultra Lotto-PH": [58] * 6,
    "Lotto 6/49-CA": [49] * 6,
    "Lotto Max-CA": [50] * 8,
    "Daily Grand/Grand vie-CA": [49, 49, 49, 49, 49, 7],
    "Vikinglotto": [48, 48, 48, 48, 48, 48, 5]
}

ZERO_INDEX = [("La Primitiva-ES", 1)]

class Lotto:
    def __init__(self, games=None):
        if not games:
            self.games = ["Powerball", "MegaMillions"]
        elif isinstance(games, str):
            countries = [key.rsplit("-")[1] for key in FORMATS if key[-3] == "-"]
            if games in countries:
                self.games = [key for key in FORMATS if key.endswith(games.upper())]
            else:
                raise ValueError(f"Country code {games} is not supported.")
        else:
            self.games = games
        self.draws = {}
        for game in self.games:
            self.draws[game] = [None] * len(FORMATS.get(game))
            if game not in FORMATS:
                raise ValueError(f"Lotto game {game} is not supported.")
            pool_layout = FORMATS.get(game)
            pool_sizes = set(pool_layout)
            pool_limits = [[1, size] for size in pool_sizes]
            zeroes = [rule for rule in ZERO_INDEX if rule[0] == game]
            for zero in zeroes:
                pool_limits[zero[1]][0] -= 1
                pool_limits[zero[1]][1] -= 1
            for pool_limit in pool_limits:
                pool = list(range(*pool_limit))
                pool_id = pool_limit[1]
                if pool_limit[0] == 0:
                    pool_id += 1
                random.shuffle(pool)
                draws_in_pool = FORMATS.get(game).count(pool_id)
                for _ in range(draws_in_pool):
                    index = pool_layout.index(pool_id)
                    self.draws[game][index] = pool.pop()
                    pool_layout[index] = None

    def __repr__(self):
        outstr = []
        for draw in self.draws:
            outstr.append(f"{draw}: {self.draws.get(draw)}")
        return '\n'.join(outstr)
