# Mesa
from mesa import Agent, Model 
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

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
                if isinstance(agent, BoxMover):
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

class BoxMover(Agent):
    """ An agent that moves boxes to certain locations. """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.color = 2
        self.moves = 0
        self.destination=(0,0)
        self.box = False # True if carrying box, false if empty

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, # Von Neumann neighborhood
            include_center=False)
        # A
        possible_steps_content = list()
        for i in range (len(possible_steps)):
            a = self.model.grid.get_cell_list_contents([possible_steps[i]])
            possible_steps_content.append(a)
        # Random list of choices        
        random_list = random.sample(range(0,len(possible_steps)),len(possible_steps))
        for n in random_list:
            if len(possible_steps_content[n])==1 and possible_steps_content[n][0].color==0:
                new_position = possible_steps[n]
                self.model.grid.move_agent(self, new_position)         
        self.moves += 1

    def searchForBox(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, # Von Neumann neighborhood
            include_center=False)
        # A
        possible_steps_content = list()
        for i in range (len(possible_steps)):
            a = self.model.grid.get_cell_list_contents([possible_steps[i]])[0]
            if (a.color == 1):
                possible_steps_content.append(a)
            else:
                possible_steps_content.append('')
        # if box in any of possible steps
        random_list = random.sample(range(0,len(possible_steps)),len(possible_steps))
        for n in random_list:
            if (isinstance(possible_steps_content[n],Box) and possible_steps_content[n].pos!=self.destination):
                # Get box from that position
                box = possible_steps_content[n]
                # Agarrar la caja
                self.color = 3
                self.box = True
                box.color = 0
        
    def moveBox(self):
        # Con caja y sin obstáculo mover a menor de x o y, para el punto de delivery
        xf, yf = self.destination
        x,  y  = self.pos
        minx, miny = xf-x, yf-y
        if (self.pos==(0,1) or self.pos==(1,0)):
            self.pileBox()
        else:
            if (abs(minx) <= abs(miny)):
                if minx!=0 :
                    agentsinX=self.model.grid.get_cell_list_contents((x-1,y))
                    obsinX=False
                    for agent in agentsinX:
                        if agent.color!=0:
                            obsinX=True
                    if not obsinX:
                        self.model.grid.move_agent(self, (x-1,y))
                    else:
                        self.move()
                        
                else:
                    agentsinY=self.model.grid.get_cell_list_contents((x,y-1))
                    obsinY=False
                    for agent in agentsinY:
                        if agent.color!=0:
                            obsinY=True
                    if not obsinY:
                        self.model.grid.move_agent(self, (x,y-1))
                    else:
                        self.move()
                        
            else:
                if miny!=0:
                    agentsinY=self.model.grid.get_cell_list_contents((x,y-1))
                    obsinY=False
                    for agent in agentsinY:
                        if agent.color!=0:
                            obsinY=True
                    if not obsinY:
                        self.model.grid.move_agent(self, (x,y-1))
                    else:
                        self.move()
                        
                else:
                    agentsinX=self.model.grid.get_cell_list_contents((x-1,y))
                    obsinX=False
                    for agent in agentsinX:
                        if agent.color!=0:
                            obsinX=True
                    if not obsinX:
                        self.model.grid.move_agent(self, (x-1,y))
                    else:
                        self.move()
                        
    
    def pileBox(self):
        self.color=2
        self.box=False
        destination=self.model.grid.get_cell_list_contents(self.destination)[0]
        destination.color=1
        destination.onTop+=1
        destination.piled=True    

    def step(self):
        if (self.box):
            self.moveBox()
        else:
            self.move()
            self.searchForBox()

class Box(Agent):
    '''
    Represents if a tile has a box or not ("1 is box, 0 is empty")
    '''
    def __init__(self, unique_id, color, model):
        super().__init__(unique_id, model)
        self.color = color
        self.piled = False
        self.onTop=0

    def step(self):
        pass

class ArrangamentModel(Model):
    """A model with some number of agents."""
    
    def __init__(self, N, width, height, density, coords=(0,0)):
        # Initialize model parameters
        self.num_agents = N
        self.height = height
        self.width = width
        self.density= density
        self.destination = coords

        
        # Set up model objects
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        
        # Create box movers at random positions
        for j in range(self.num_agents):
            a = BoxMover('BxMver-'+str(j), self)
            self.schedule.add(a)
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            self.grid.place_agent(a, (x, y))
              
        # Create boxes based on density
        for (content, x, y) in self.grid.coord_iter():
            a = Box('Bx-'+str((x,y)), 0, self)
            if random.random() < self.density and (x,y)!=coords:
                a = Box((x, y), 1, self)
            self.grid.place_agent(a, (x, y))
            self.schedule.add(a)

        # Define collector for the entire grid 
        self.datacollector = DataCollector(
            model_reporters={"Grid": get_grid})
        
        # Run the model until it is halted
        self.running = True
        
    def step(self):
        self.datacollector.collect(self)
        # Halt if no more boxes left to pile
        if self.count_left(self) == 0:
            self.running = False
        self.schedule.step()
        
        
    @staticmethod
    def count_left(self):
        '''
        Helper method to count boxes that are piled
        '''
        count = 0
        for agent in self.schedule.agents:
            if isinstance(agent, Box):
                if (agent.piled == False and agent.color==1 and agent.pos!=self.destination):
                    count += 1
        return count



