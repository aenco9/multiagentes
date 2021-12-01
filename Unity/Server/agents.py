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
    def __init__(self, unique_id, model, destinyCords):
        super().__init__(unique_id, model)
        self.color = 1
        self.moves = 0
        self.direction = None
        self.destiny = destinyCords

    def move(self):
        
        
        self.update_direction()
        nc = self.get_neighborhood_content()
        
        if(type(self.get_far_neighborhood_content()) == list):
            nc = nc + self.get_far_neighborhood_content()
        y, x  = self.pos
        yd, xd = self.destiny
        if((y,x+1) == (yd, xd) or (y,x-1) == (yd, xd) or (y+1,x) == (yd, xd) or (y-1,x) == (yd, xd)):
            self.model.grid.move_agent(self, (yd,xd))
        elif(self.direction == "South" and (y,x+2) == (yd,xd)):
            self.model.grid.move_agent(self, (y,x+1))
        
        
        elif(self.direction == "East" and  len(nc) > 6 and nc[6] == "v"  and self.check_proximity(4)):
            self.check_turn(1)
        elif(self.direction == "East" and  len(nc) > 7 and ( nc[-2] == "v")  and self.check_proximity(4)):
            self.check_turn(1)
        elif(self.direction == "East" and  len(nc) > 7 and ( nc[-1] == "^")  and self.check_proximity(1)):
            self.check_turn(4)
        elif(self.direction == "East"):
            self.model.grid.move_agent(self, (y,x+1))
        elif(self.direction == "North" and  len(nc) > 6 and nc[4] == ">"  and (13,15) == (yd,xd)):
            self.check_turn(2)
        elif(self.direction == "North" and  len(nc) > 6 and nc[4] == ">"  and self.check_proximity(3)):
            self.check_turn(2)
        elif(self.direction == "North" and  len(nc) > 7 and (nc[-2] == ">" )  and self.check_proximity(3)):
            self.check_turn(2)
        elif(self.direction == "North" and  len(nc) > 7 and (nc[-1] == "<" )  and self.check_proximity(2)):
            self.check_turn(3)
        elif(self.direction == "North"):
            self.model.grid.move_agent(self, (y-1,x))
        elif(self.direction == "South" and  len(nc) > 6 and nc[3] == "<"  and self.check_proximity(2)):
            self.check_turn(3)
        elif(self.direction == "South" and  len(nc) > 7 and (nc[-1] == "<" )  and self.check_proximity(2)):
            self.check_turn(3)
        elif(self.direction == "South" and  len(nc) > 7 and (nc[-2] == ">")  and self.check_proximity(3)):
            self.check_turn(2)
        elif(self.direction == "South"):
            self.model.grid.move_agent(self, (y+1,x))
        elif(self.direction == "West" and  len(nc) > 6 and nc[1] == "^"  and self.check_proximity(1)):
            self.check_turn(4)
        elif(self.direction == "West" and  len(nc) > 7 and (nc[-1] == "^" )  and self.check_proximity(1)):
            self.check_turn(4)
        elif(self.direction == "West" and  len(nc) > 7 and (nc[-2] == "v" )  and self.check_proximity(3)):
            self.check_turn(1)
        elif(self.direction == "West"):
            self.model.grid.move_agent(self, (y,x-1))
            
        elif(self.direction == "Destiny"):
            pass
        else:
            self.model.grid.move_agent(self, (y-1,x))
            
        
        
        self.moves += 1
        
    def check_turn(self, case):
        nc = self.get_neighborhood_content()
        y, x  = self.pos
        # if vuelta en el carril interior
        
        
        if(case == 1):
            self.model.grid.move_agent(self, (y+1,x))
        elif(case == 2):
            self.model.grid.move_agent(self, (y,x+1))
        elif(case == 3):
            self.model.grid.move_agent(self, (y,x-1))
        elif(case == 4):
            self.model.grid.move_agent(self, (y-1,x))
        else:
            pass
        
        
    def check_proximity(self, case):
        y, x  = self.pos
        
        yd, xd = self.destiny
        #North
        if(case == 1):
            if(xd >= x-1):
                return True
        #East
        elif(case == 2):
            if(yd <= y-1):
                return True
        #West
        elif(case == 3):
            if(yd >= y+1):
                return True
        #South
        elif(case == 4):
            if(xd <= x+1):
                return True
        else:
            return False
        
        
    def update_direction(self):
        nc = self.get_neighborhood_content()
        
        center = self.model.grid.get_cell_list_contents(self.pos)
        center = [x for x in self.model.grid.get_cell_list_contents(self.pos) if isinstance(x,Tile)][0].symbol
        
            
        if (center == "^"):
            self.direction = "North"
        elif (center == "v"):
            self.direction = "South"
        elif (center == '<'):
            self.direction = "West"
        elif (center == '>'):
            self.direction = "East"
        elif (center in 'Ss'):
            pass
            #self.direction = "Stop"
        elif(center == 'D'):
            self.direction = "Destiny"
        else:
            self.direction = "se rompió este pedo"
            
        
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
    
    def get_far_neighborhood_content(self):
        #para cada caso
        
        #North: x+2, x-2 a menos que esté en borde
        #South  x+2, x-2 a menos que esté en borde
        y,x = self.pos
        a = []
        if(self.direction == "North" or self.direction == "South"):
            
            if(x < 2):
                coordenada = (y, x+2)
                possible_step = self.model.grid.get_neighborhood(coordenada,moore=True,include_center=True)
                a.append(self.model.grid.get_cell_list_contents([possible_step[4]])[0].symbol)
                a.append(0)
                return(a)
            elif (x > self.model.width - 3):
                coordenada = (y, x-2)
                possible_step = self.model.grid.get_neighborhood(coordenada,moore=True,include_center=True)
                a.append(0)
                a.append(self.model.grid.get_cell_list_contents([possible_step[4]])[0].symbol)
                return(a)
            
            else:
                coordenada1 = (y, x-2)
                coordenada2 = (y, x+2)
                possible_step2 = self.model.grid.get_neighborhood(coordenada2,moore=True,include_center=True) 
                possible_step1 = self.model.grid.get_neighborhood(coordenada1,moore=True,include_center=True)
                

                a.append(self.model.grid.get_cell_list_contents([possible_step1[4]])[0].symbol)
                a.append(self.model.grid.get_cell_list_contents([possible_step2[4]])[0].symbol)
                return(a)
        #East y+2, y-2 a menos que esté en borde
        #West y+2, y-2 a menos que esté en borde
        elif (self.direction == "East" or self.direction == "West"):
            if(y < 2):
                coordenada = (y+2,x)
                possible_step = self.model.grid.get_neighborhood(coordenada,moore=True,include_center=True)
                a.append(self.model.grid.get_cell_list_contents([possible_step[4]])[0].symbol)
                a.append(0)
                return(a)
            elif (y > self.model.height - 3):
                coordenada = (y-2, x)
                possible_step = self.model.grid.get_neighborhood(coordenada,moore=True,include_center=True)
                a.append(0)
                a.append(self.model.grid.get_cell_list_contents([possible_step[4]])[0].symbol)
                return(a)
            else:
                coordenada1 = (y-2, x)
                coordenada2 = (y+2, x)
                possible_step1 = self.model.grid.get_neighborhood(coordenada1,moore=True,include_center=True)
                possible_step2 = self.model.grid.get_neighborhood(coordenada2,moore=True,include_center=True)
                a.append(self.model.grid.get_cell_list_contents([possible_step2[4]])[0].symbol)
                a.append(self.model.grid.get_cell_list_contents([possible_step1[4]])[0].symbol)
                
                return(a)
                
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
        self.destinies = []
        self.street_tiles = []
        # Set up model objects
        self.grid = MultiGrid(width, height, False)
        self.schedule = SimultaneousActivation(self)
        
        # Create the city
        for (content, x, y) in self.grid.coord_iter():
            if (self.city[x][y] == 'D'):
                self.destinies.append((x,y))
            elif (self.city[x][y] == ('^' or '>' or '<' or 'v')):
                self.street_tiles.append((x,y))
            tmp = self.city[x][y]
            a = Tile(str((x,y)), tmp, self)
            self.schedule.add(a)
            self.grid.place_agent(a, (x, y))
        
        # Create cars
        for j in range(self.num_agents):
            a = Car('Car-'+str(j), self, random.choice(self.destinies))
            self.schedule.add(a)
            self.grid.place_agent(a, random.choice(self.street_tiles))
        #a = Car('Car-'+str(1), self, (2,4))
        #b = Car('Car-'+str(2), self, (13,15))
        
        
        #self.schedule.add(b)
        


        
        #self.grid.place_agent(a, (5,0))
        #self.grid.place_agent(b,(22,1))
        
              
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
