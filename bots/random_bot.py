import random

class RandomBot():
    def __init__(self, piece):
        self.piece = piece

    def get_move(self):
        # select either 0 or 6
        col = random.choice([0,6])
        return col