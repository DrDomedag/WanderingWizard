
class FloorTile:
    def __init__(self):
        self.layer = "floor"
        self.name = "Floor"
        self.walkable = True
        self.flyable = True
        self.swimmable = False
        self.flammable = False
        self.onEnterEffects = []
        self.onTurnStartEffects = []
        self.onTurnEndEffects = []
        self.asset = "unknown"

class DirtFloorTile(FloorTile):
    def __init__(self):
        super().__init__()
        self.name = "Floor"
        self.type = "solid"
        self.asset = "dirt_tile"

class DryGrassFloorTile(FloorTile):
    def __init__(self):
        super().__init__()
        self.name = "Floor"
        self.type = "solid"
        self.asset = "dry_grass_tile"

class LavaFloorTile(FloorTile):
    def __init__(self):
        super().__init__()
        self.name = "Lava"
        self.type = "liquid"
        self.walkable = False
        self.swimmable = True
        #self.onEnterEffects.append() Deal fire damage

class WaterFloorTile(FloorTile):
    def __init__(self):
        super().__init__()
        self.name = "Water"
        self.type = "liquid"
        self.asset = "water_tile"
        self.walkable = False
        self.swimmable = True
        # Make this turn into ice when hit by cold damage, which thaws when hit by fire damage

class ChasmFloorTile(FloorTile):
    def __init__(self):
        super().__init__()
        self.name = "Chasm"
        self.type = "void"
        self.walkable = False
        self.swimmable = False
