# Mesa
from mesa import Agent, Model 
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

# Matplotlib
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128

# Libraries
import numpy as np
import pandas as pd
import time
import datetime
import random
from contextlib import contextmanager
import threading
import _thread

def get_grid(model):
    '''
    Stores the grid content in an array.
    '''
    grid = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, x, y = cell
        grid[x][y] = cell_content[0].color
        if len(cell_content)>1:
            for agent in cell_content:
                if isinstance(agent, Car):
                    grid[x][y] = agent.color
        
    return grid

@contextmanager
def time_limit(seconds):
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise Exception("Timed out for operation")
        timer.cancel()

class Car(Agent):
    """ An agent that moves boxes to certain locations. """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.color = 1
        self.moves = 0
        self.direction = None

    def move(self):
        self.check_turn()
        self.update_direction()
        nc = self.get_neighborhood_content()
        y, x  = self.pos
        print(nc)
        print(self.direction)
        
        self.model.grid.move_agent(self, (y-1,x))
        
        self.moves += 1
        
    def check_turn(self):
        nc = self.get_neighborhood_content()
        y, x  = self.pos
        # if vuelta en el carril interior
        if (self.direction == "East" and  nc[-1] == "v"):
            self.model.grid.move_agent(self, (y,x+1))
            self.model.grid.move_agent(self, (y+1,x))
        elif (self.direction == "South" and  nc[5] == "<"):
            self.model.grid.move_agent(self, (y+1,x))
            self.model.grid.move_agent(self, (y,x-1))
        elif (self.direction == "West" and  nc[1] == "^"):
            self.model.grid.move_agent(self, (y,x-1))
            self.model.grid.move_agent(self, (y-1,x))
        else:
            pass
        
    def update_direction(self):
        nc = self.get_neighborhood_content()
        
        center = self.model.grid.get_cell_list_contents(self.pos)
        center = [x for x in self.model.grid.get_cell_list_contents(self.pos) if isinstance(x,Tile)][0].symbol
        print(center)
            
        if (center == "^"):
            self.direction = "North"
        elif (center == "v"):
            self.direction = "South"
        elif (center == '<'):
            self.direction = "West"
        elif (center == '>'):
            self.direction = "East"
        elif (center in 'Ss'):
            self.direction = "Stop"
        else:
            self.direction = "se rompió este pedo"
            print(center)
        
    def get_neighborhood_content(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos,
        moore=True,
        include_center=False)
        # Check content of possible steps
        possible_steps_content = list()
        for i in range (len(possible_steps)):
            a = self.model.grid.get_cell_list_contents([possible_steps[i]])[0]
            possible_steps_content.append(a.symbol)

        return possible_steps_content
        
    def step(self):
        self.move()

class Tile(Agent):
    '''
    Represents a piece of city (road, building, stop, etc.)
    '''
    def __init__(self, unique_id, symbol, model):
        super().__init__(unique_id, model)
        self.symbol = symbol
        self.color = model.color_dic[self.symbol]       
        
    def step(self):
        pass

class ArrangementModel(Model):
    """A model with some number of agents."""
    
    def __init__(self, city, N, width, height):
        # Initialize model parameters
        self.city = city
        self.num_agents = N
        self.height = height
        self.width = width
        self.color_dic = {
            "D": 2,
            "S": 3,
            "s": 3,
            "^": 4,
            ">": 5,
            "v": 6,
            "<": 7,
            "#": 8
        }

        # Set up model objects
        self.grid = MultiGrid(width, height, False)
        self.schedule = SimultaneousActivation(self)
        
        # Create the city
        for (content, x, y) in self.grid.coord_iter():
            tmp = self.city[x][y]
            a = Tile(str((x,y)), tmp, self)
            self.schedule.add(a)
            self.grid.place_agent(a, (x, y))
            
        # Create cars
        for j in range(self.num_agents):
            a = Car('Car-'+str(j), self)
            self.schedule.add(a)
            #x = random.randrange(self.width)
            #y = random.randrange(self.height)
            x = 17
            y = 6
            self.grid.place_agent(a, (y, x))
              
        # Define collector for the entire grid 
        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid})
        
        # Run the model until it is halted
        #self.running = True
        
    def step(self):
        self.datacollector.collect(self)
        # Halt if no cars in the map
        #if self.count_left() == 0:
            #self.running = False
        self.schedule.step()
