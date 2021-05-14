from sprites import *

#class used to keep track of zombies
class ListMobs:
    def __init__(self, game):
        self.game = game
        self.list = dict()
        self.data = dict()
        for id in range(game.nb_zombies):
            self.list[id] = None
            self.data[id] = None

    def create_mob_list(self):
        # print(self.game.network.is_master)
        id = 0
        if self.game.network.is_master:
            for row, tiles in enumerate(self.game.map.data):
                for col, tile in enumerate(tiles):
                    if tile == 'M':
                        mob = Mob(self.game, int(col*TILESIZE+TILESIZE/2), int(row*TILESIZE+TILESIZE/2))
                        self.list[id] = mob
                        self.data[id] = {"Pos": mob.pos, "Rot": mob.rot, "Hp": mob.health}
                        id += 1
        print(self.data)

    def update(self):
        for id in self.data.keys():
            if self.data[id] and self.list[id]:
                self.data[id]["Pos"] = self.list[id].pos
                self.data[id]["Rot"] = self.list[id].rot
                self.data[id]["Hp"] = self.list[id].health
