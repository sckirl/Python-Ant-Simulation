import pygame
import random
import sys
pygame.init()

# display config for pygame
win = pygame.display.set_mode((960, 540))
pygame.display.set_caption('Ant Colony Simulation')

clock = pygame.time.Clock()

class antClass(object):
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        # making ant Class that works like linked list
        # to visualize, it looks like; parent.parent <- parent <- position

class pheromoneClass(object):
    def __init__(self, position, value):
        self.position = position
        self.value = value

class simulation(object):
    def __init__(self, antAmount, travelPower):
        # important variables to work with
        self.ants = []
        self.foods = []
        self.walls = set()

        self.track = set()
        self.follow = set()
        self.nest = (480, 270)
        self.antID = None

        self.start = self.get_Food = False
        self.get_Wall =  False
        self.travelPower = travelPower//3

        self.travel = [
            ((0, (self.travelPower))),
            (((self.travelPower)), 0),
            ((0, -(self.travelPower))),
            (-(self.travelPower), 0),
            ((self.travelPower), (self.travelPower)),
            ((self.travelPower), -(self.travelPower)),
            (-(self.travelPower), (self.travelPower)),
            (-(self.travelPower), -(self.travelPower)),
        ]

        for i in range(antAmount): # generating ant population in same nest
            self.ants.append(antClass(position=(self.nest[0], self.nest[1])))

        self.pheromones = [[None]]*len(self.ants)
        self.addFood()

    def explore(self): # the state of ant after leaving nest, will go to random places
        for antID in range(len(self.ants)):
            if antID in self.track and self.ants[antID].position == self.nest:
                # checks if the ant is in the nest, if yes then restart the process (from explore)
                self.track.remove(antID)
                self.pheromones[antID] = [None]

            elif antID not in self.track:
                x, y = random.choices(self.travel)[0] # gets random movement from all 4 above
                
                if (self.ants[antID].position[0] + x, self.ants[antID].position[1] + y) not in self.walls:
                    self.ants[antID] = antClass(self.ants[antID],
                                                (self.ants[antID].position[0] + x, self.ants[antID].position[1] + y))

                else:
                    self.ants[antID] = antClass(self.ants[antID],
                                                (self.ants[antID].position[0] - x, self.ants[antID].position[1] - y))
                # updates the state of the ant inside the list, and adding its parent in every step

                if self.ants[antID].position in self.foods: # checks if ant is on the food
                    self.foods.pop(self.foods.index(self.ants[antID].position))
                    if self.ants[antID] in self.follow: self.follow.remove(self.ants[antID])
                    self.track.add(antID)
                    
                self.pheromoneList = [node.position for i in self.pheromones for node in i if node is not None]
                if self.ants[antID].position in self.pheromoneList:
                    self.follow.add(antID)

    def leader(self, antID):
        self.ants[antID] = self.path[antID].pop()  

    def returner(self, antID): # state of ant after getting food; going to nest
        if self.ants[antID].parent is not None:
            self.pheromones[antID].append(pheromoneClass(self.ants[antID].position, 0))
            self.ants[antID] = self.ants[antID].parent

            # making the path from linked list made before, The self.ants are all of the ants that
            # bring foods to the nest. ants will go back to their parent position, meaning it will
            # go to its previous movements until its back to the nest (once again nest ... <- parent.parent <- parent <- position)

        self.makePheromones(antID)        

    def makePheromones(self, antID):
        PhemoroneLength = 10
        
        if len(self.pheromones[antID]) > PhemoroneLength:
            self.pheromones[antID].pop(0)
        temp = []
        
        for idx, node in enumerate(self.pheromones[antID]):
            if node is not None:
                temp.append(pheromoneClass(node.position, idx * (255//PhemoroneLength)))

        self.pheromones[antID] = temp

    def follower(self, antID):
        # getting all possible movements for 4 nodes
        if self.ants[antID] in self.pheromoneList and antID not in self.track:
            for path in self.travel:
                if (self.ants[antID].position[0] + path[0],\
                    self.ants[antID].position[1] + path[1]) in self.pheromoneList:

                    for _ in range(5):
                        self.ants[antID] = antClass(self.ants[antID],
                                            (self.ants[antID].position[0] + path[0], self.ants[antID].position[1] + path[1]))

        if self.ants[antID].position in self.foods: # checks if ant is on the food
            self.track.add(antID)

    def addFood(self):
        if self.get_Food:
            position = pygame.mouse.get_pos()
            for x, y in [(x, y) for x in range(position[0], position[0]+5)
                         for y in range(position[1], position[1]+5)]:
                self.foods.append((x, y))

    def addWall(self):
        if self.get_Wall:
            position = pygame.mouse.get_pos()
            for x, y in [(x, y) for x in range(position[0], position[0]+self.travelPower*5)
                         for y in range(position[1], position[1]+self.travelPower*5)]:
                self.walls.add((x, y))
        
    def draw(self):
        win.fill([255, 255, 255])

        for ID in self.track:
            self.returner(ID)
        
        for ID in self.follow:
            self.follower(ID)

        for wall in self.walls: # drawing all of the foods
            pygame.draw.circle(win, [0, 0, 0], (wall[0], wall[1]), 1)

        for ant in self.ants: # drawing all of the ants
            pygame.draw.circle(win, [191, 121, 96], (ant.position[0], ant.position[1]), 2)

        for arr in self.pheromones: # drawing all of the pheromones
            for node in arr:
                if node is not None:
                    pygame.draw.circle(win, [node.value, node.value//3, 59], (node.position[0], node.position[1]), 2)

        for food in self.foods:
            pygame.draw.rect(win, [217, 146, 59], (food[0], food[1], 1, 1))

        pygame.draw.circle(win, [89, 73, 71], (self.nest[0], self.nest[1]), 5) # drawing nest
        pygame.display.update()

antColony = simulation(200, 9)

while (True):
    clock.tick(20)
    # keypress, quit config
    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            sys.exit()

        if events.type == pygame.KEYDOWN:
            if events.key == pygame.K_SPACE:
                antColony.start = True
                
            if events.key == pygame.K_q and not antColony.get_Food:
                antColony.get_Food = True
            else: antColony.get_Food = False

            if events.key == pygame.K_w and not antColony.get_Wall:
                antColony.get_Wall = True
            else: antColony.get_Wall = False
            
            
    antColony.addWall()
    antColony.addFood()
    # will loop and changes every ant position
    if antColony.start:
        antColony.explore()

    # redrawing all of the stuff above
    antColony.draw()