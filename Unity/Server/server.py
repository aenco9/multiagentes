from flask import Flask, request, jsonify
from agents import *

# Size of the board:
cars = 1
agentModel = None
currentStep = 0
value=1

def load_city(path):
    with open(path, encoding='utf8') as f:
        city = str()
        for line in f:
            city += line
    width = len(city.partition('\n')[0])
    city = [x for x in city.split('\n')]
    height = len(city)
    
    return height, width, city

import os
path = os.path.abspath(os.path.join(os.getcwd(),'city.txt'))
height, width, city = load_city(path)

app = Flask("Cars")

@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, agentModel, height, width, city

    if request.method == 'POST':
        number_agents = int(request.form.get('NAgents'))
        currentStep = 0

        print(request.form)
        print(number_agents, width, height)
        agentModel = ArrangementModel(city, number_agents, height, width)
        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getCars', methods=['GET'])
def getAgents():
    global agentModel

    if request.method == 'GET':
        carPositions = []
        for (a,x,z) in agentModel.grid.coord_iter():
            for agents in a:
                if isinstance(agents, Car):
                    carPositions.append({"x": x, "y":0, "z":z})
        return jsonify({'positions':carPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, agentModel
    if request.method == 'GET':
        agentModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)