from tile import Tile


class TileSet:
    def __init__(self):
        self.tiles = []

    def from_decompressed_bytes(self, data, index):
        self.tiles.clear()
        tile_set_size = data[4]

        for i in range(0, 64):
            tile = Tile()

            if tile_set_size > i:
                for j in range(0, 4):
                    tile.characters[j] = data[5 + i + (j * tile_set_size)] + 0x40 * index
                type_pos = 6 + i + (tile_set_size * 5)
                if len(data) > type_pos:
                    tile.tile_type = data[type_pos]

            self.tiles.append(tile)
