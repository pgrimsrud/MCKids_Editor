class SpawnPoint:
    def __init__(self, x, y, sprite_index, index):
        self.x = x
        self.y = y
        self.sprite_index = sprite_index
        self.index = index

    @staticmethod
    def get_index(element):
        return element.index