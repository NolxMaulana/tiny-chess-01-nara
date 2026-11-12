import json
import os
import sys
import urllib.error
import urllib.request

ENV_URL = os.environ.get("MAKEFUN_ENV_URL") or sys.exit("MAKEFUN_ENV_URL is not set")
VALUE = {"p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 100}


def post(path, body):
    req = urllib.request.Request(
        ENV_URL + path,
        data=json.dumps(body).encode(),
        headers={"content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as res:
            return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"{path}: HTTP {e.code} {e.read().decode(errors='replace')}")


def board_of(fen):
    board = {}
    for i, row in enumerate(fen.split()[0].split("/")):
        file = 0
        for c in row:
            if c.isdigit():
                file += int(c)
            else:
                board["abcdefgh"[file] + str(8 - i)] = c
                file += 1
    return board


def centre(square):
    return abs("abcdefgh".index(square[0]) - 3.5) + abs(int(square[1]) - 4.5)


def choose(fen, legal):
    board = board_of(fen)

    def rank(move):
        mover = board[move[:2]].lower()
        victim = board.get(move[2:4])
        if victim is None and mover == "p" and move[0] != move[2]:
            victim = "p"
        taken = VALUE[victim.lower()] if victim else 0
        promo = VALUE[move[4]] if len(move) == 5 else 0
        return (-taken, -promo, centre(move[2:4]) - 0.1 * centre(move[:2]), VALUE[mover], move)

    return min(legal, key=rank)


while True:
    g = post("/game", {})
    if g["status"] == "done":
        break
    while g["status"] == "your_move":
        g = post("/move", {"game": g["game"], "move": choose(g["fen"], g["legal_moves"])})
    print(f"game {g['game']}: {g['outcome']} by {g['reason']}", file=sys.stderr)
print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost", file=sys.stderr)
