from flask import Flask, request, jsonify
from agents import *

# Size of the board:
number_agents = 5
width = 10
height = 10
agentModel = None
currentStep = 0
cajas=10

app = Flask("Robots")

# @app.route('/', methods=['POST', 'GET'])

@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, agentModel, number_agents, width, height, cajas

    if request.method == 'POST':
        number_agents = int(request.form.get('NAgents'))
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        density = float(request.form.get('density'))
        currentStep = 0

        print(request.form)
        print(number_agents, width, height)
        agentModel = ArrangamentModel(number_agents, width, height, density)

        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getRobots', methods=['GET'])
def getAgents():
    global agentModel

    if request.method == 'GET':
        robotPositions = []
        for (a,x,z) in agentModel.grid.coord_iter():
            for agents in a:
                if isinstance(agents, BoxMover):
                    robotPositions.append({"x": x, "y":1, "z":z})
        return jsonify({'positions':robotPositions})

@app.route('/getBoxes', methods=['GET'])
def getObstacles():
    global agentModel
    if request.method == 'GET':
        boxPositions=[]
        for (a,x,z) in agentModel.grid.coord_iter():
            for agents in a:
                if isinstance(agents, Box) and agents.color==1:
                    boxPositions.append({"x": x, "y":1, "z":z})
        return jsonify({'positions':boxPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, agentModel
    if request.method == 'GET':
        agentModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)