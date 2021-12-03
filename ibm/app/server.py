from flask import Flask, request, jsonify
from agents import *
import os
port = int(os.getenv('PORT', 8000))

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
        agentModel = ArrangementModel(city, number_agents, width, height)
        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getCars', methods=['GET'])
def getAgents():
    global agentModel

    if request.method == 'GET':
        carPositions = []
        carData=[]
        for (a,x,z) in agentModel.grid.coord_iter():
            for agents in a:
                if isinstance(agents, Car):
                    carPositions.append({"x": z, "y":0, "z":x, "id":int(agents.unique_id[4:])})
                    dir=0
                    if agents.direction=="North":
                        dir=1
                    elif agents.direction=="West":
                        dir=2
                    elif agents.direction=="South":
                        dir =3
                    elif agents.direction=="East":
                        dir=4
                    carData.append({"x": int(agents.unique_id[4:]), "y":dir, "z":0})
        carPositions=sorted(carPositions, key=lambda d: d['id'])
        for car in carPositions:
            car.pop("id")
        return jsonify({'positions':carPositions, 'data':carData})

@app.route('/getTrafficLights', methods=['GET'])
def getTrafficLights():
    global agentModel
    if request.method == 'GET':
        tlPositions = []
        for (a,x,z) in agentModel.grid.coord_iter():
            for agents in a:
                if isinstance(agents, Stoplight):
                    tlPositions.append({"x": z, "y":agents.color, "z":x})
        return jsonify({'positions':tlPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, agentModel
    if request.method == 'GET':
        agentModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=port, debug=True)