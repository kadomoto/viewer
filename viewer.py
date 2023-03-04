import pyxel

import json
import argparse
import random

DISPLAY_AREA = 320
CHIP_AREA = 256  # chip area
SIZE = 6  # chip size
CENTER = CHIP_AREA // SIZE * SIZE / 2

COORD_NUM = 1
ROUT_NUM = 0


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Chip:
    def __init__(self, x, y):
        self.pos = Vec2(x, y)


class App:
    def __init__(self, json_path):
        pyxel.init(DISPLAY_AREA, DISPLAY_AREA, title="viewer", quit_key=pyxel.KEY_Q)
        pyxel.load("assets/CHIP.pyxres")
        pyxel.mouse(True)
        # sound effect
        pyxel.sound(0).set("a3a2c1a1", "t", "7", "s", 5)
        pyxel.sound(1).set("a3e2a1", "p", "7", "s", 5)

        if json_path is None:
            print("no json file")
            chip_data = None
            # chip list
            self.chips = []
            # coordinator
            new_coord = Chip(CENTER, CENTER)
            self.chips.append(new_coord)
        else:
            print("Read json file")
            with open(json_path, 'r') as f:
                chip_data = json.load(f)
            print(chip_data)
            # chip list
            self.chips = []  # [Chip()]
            self.chipDict = {}  # {'node_id': (x, y)}
            self.chipPositions = {}  # {(x, y): 'node_id'}

            # coordinator
            new_coord = Chip(CENTER, CENTER)
            self.chips.append(new_coord)
            self.chipDict.update([('0', (0, 0))])
            self.chipPositions.update([((0, 0), '0')])

            # routers
            for node in chip_data['adjacencies'].items():
                dict, pos = self.nodePos(node)
                self.chipDict.update(dict)
                self.chipPositions.update(pos)

            for position in self.chipPositions:
                if (position[0] == 0 and position[1] == 0):
                    pass
                else:
                    new_rout = Chip(CENTER + position[0]*SIZE, CENTER + position[1]*SIZE)
                    self.chips.append(new_rout)

        pyxel.run(self.update, self.draw)

    def nodePos(self, node):
        adjacent_node_num = len(node[1])
        for adjacent_node in node[1]:
            if adjacent_node in self.chipDict: adjacent_node_num = adjacent_node_num - 1
        random_positions = self.randomPos(self.chipDict[node[0]], adjacent_node_num)
        node_list = []
        position_list = []
        i = 0
        for adjacent_node in node[1]:
            if adjacent_node in self.chipDict:
                pass
            else:
                node_list.append((adjacent_node, tuple(random_positions[i])))
                position_list.append((tuple(random_positions[i]), adjacent_node))
                i = i + 1
        
        return node_list, position_list  # list of ('node_id', (x, y)), list of ((x, y), 'node_id')
    
    def randomPos(self, position, num):
        x = position[0]
        y = position[1]
        pos = []
        if (x+1, y) not in self.chipPositions: pos.append([x+1, y])
        if (x, y-1) not in self.chipPositions: pos.append([x, y-1])
        if (x-1, y) not in self.chipPositions: pos.append([x-1, y])
        if (x, y+1) not in self.chipPositions: pos.append([x, y+1])

        return random.sample(pos, num)
    
    def jsonGen(self):
        outputDic = {}
        num = len(self.chips)
        outputDic.update([("num", num)])
        nodes = {}
        i = 1
        for chip in self.chips:
            if (chip.pos.x == CENTER and chip.pos.y == CENTER):
                nodes.update([("0", "Coordinator")])
            else:
                nodes.update([(str(i), "Router")])
                i = i + 1
        outputDic.update([("nodes", nodes)])
        adjacencies = {}
        for i, chip_a in enumerate(self.chips):
            adjacency = []
            for j, chip_b in enumerate(self.chips):
                if ((chip_a.pos.x == chip_b.pos.x - SIZE and chip_a.pos.y == chip_b.pos.y) or
                    (chip_a.pos.x == chip_b.pos.x and chip_a.pos.y == chip_b.pos.y - SIZE) or
                    (chip_a.pos.x == chip_b.pos.x + SIZE and chip_a.pos.y == chip_b.pos.y) or
                    (chip_a.pos.x == chip_b.pos.x and chip_a.pos.y == chip_b.pos.y + SIZE)):
                    adjacency.append(str(j))
            adjacencies.update([(str(i), adjacency)])
        outputDic.update([("adjacencies", adjacencies)])
        cycles = 10
        outputDic.update([("cycles", cycles)])
        with open("output.json", "w") as f:
            json.dump(outputDic, f, indent=4)

    def update(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):    
            if (pyxel.mouse_x < 256 and pyxel.mouse_y < 256):
                # router
                new_chip = Chip(pyxel.mouse_x // SIZE * SIZE, pyxel.mouse_y // SIZE * SIZE)
                # search
                #for chip in self.chips:
                    #if (chip.x == new_chip.x and chip.y == new_chip.y):
                        #pass
                    #else:
                        #self.chips.append(new_chip)
                self.chips.append(new_chip)
                pyxel.play(0, 0)
            elif (15 < pyxel.mouse_x < 71 and 295 < pyxel.mouse_y < 311):
                self.jsonGen()
                pyxel.play(0, 1)
            else:
                pass

    def draw(self):
        # init
        pyxel.cls(7)
        for i in range(0, CHIP_AREA, SIZE*2):
            for j in range(0, CHIP_AREA, 12):
                pyxel.rect(i, j, SIZE, SIZE, 13)
        for i in range(SIZE, CHIP_AREA, SIZE*2):
            for j in range(SIZE, CHIP_AREA, SIZE*2):
                pyxel.rect(i, j, SIZE, SIZE, 13)
        
        pyxel.rect(15, 295, 56, 16, 5)
        pyxel.text(20, 300, "output json", 13)

        for chip in self.chips:
            # place a chip
            # blt(x, y, img, u, v, w, h, [colkey])
            if (chip.pos.x == CENTER and chip.pos.y == CENTER):
                pyxel.blt(chip.pos.x, chip.pos.y, 1, 5, 5, SIZE, SIZE)
            else:
                pyxel.blt(chip.pos.x, chip.pos.y, 0, 5, 5, SIZE, SIZE)


def main(json_path):
    App(json_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default=None, help='json file path')
    args = parser.parse_args()

    main(args.path)
