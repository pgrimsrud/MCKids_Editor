from compression import compress, decompress
from spawnpoint import SpawnPoint
from rom import RomFile


class Level:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tile_map = []
        self.tile_set_indices = [0, 0, 0, 0]
        self.spawn_points = []

    def decompress(self, compressed_data):
        self.width = compressed_data[0]
        self.height = compressed_data[1]

        self.tile_set_indices = compressed_data[2:6]

        stage_data = decompress(compressed_data[7:], compressed_data[6] >> 4, compressed_data[6] & 0xF)

        spawn_count = stage_data[0]
        stage_spawn_info = stage_data[1:spawn_count * 4 + 1]
        self.tile_map = stage_data[spawn_count * 4 + 1:]

        for i in range(0, spawn_count):
            self.spawn_points.append(SpawnPoint(
                stage_spawn_info[i],
                stage_spawn_info[i + spawn_count],
                stage_spawn_info[i + spawn_count * 2],
                stage_spawn_info[i + spawn_count * 3]
            ))

    def compress(self):
        output = [self.width, self.height] + self.tile_set_indices

        stage_data = []
        for i in range(len(self.spawn_points)):
            stage_data.append(self.spawn_points[i].x)
        for i in range(len(self.spawn_points)):
            stage_data.append(self.spawn_points[i].y)
        for i in range(len(self.spawn_points)):
            stage_data.append(self.spawn_points[i].type)
        for i in range(len(self.spawn_points)):
            stage_data.append(self.spawn_points[i].index)

        stage_data += self.tile_map

        best_size = 100000
        best_offset = 0
        best_length = 0
        best_result = []
        for offset in range(8, 14):
            for length in range(4, 10):
                result = compress(stage_data, offset, length)
                if len(result) < best_size:
                    best_size = len(result)
                    best_offset = offset
                    best_length = length
                    best_result = result

        output.append(best_offset << 4 + (best_length & 0x0F))
        return output + best_result

    def get_tile_at(self, index):
        tile_index = self.tile_map[index]
        return RomFile.tile_sets[self.tile_set_indices[tile_index >> 6]].tiles[tile_index & 0x3F]

    def set_tile_map(self, tile_map):
        self.tile_map = tile_map

    def add_spawn_point(self, sprite):
        self.spawn_points.append(sprite)
