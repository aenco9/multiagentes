from flask import Flask, request, jsonify
from agents import *

# Size of the board:
number_agents = 5
width = 10
height = 10
agentModel = None
currentStep = 0
value=1

app = Flask("Robots")

@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, agentModel, number_agents, width, height, value

    if request.method == 'POST':
        number_agents = int(request.form.get('NAgents'))
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        density = float(request.form.get('density'))
        currentStep = 0

        print(request.form)
        print(number_agents, width, height)
        agentModel = ArrangementModel(number_agents, width, height, density)
        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getRobots', methods=['GET'])
def getAgents():
    global agentModel

    if request.method == 'GET':
        robotPositions = []
        for (a,x,z) in agentModel.grid.coord_iter():
            for agents in a:
                if isinstance(agents, BoxMover):
                    robotPositions.append({"x": x, "y":0, "z":z})
        return jsonify({'positions':robotPositions})

@app.route('/getBoxes', methods=['GET'])
def getObstacles():
    global agentModel
    if request.method == 'GET':
        boxPositions=[]
        for (a,x,z) in agentModel.grid.coord_iter():
            for agents in a:
                if isinstance(agents, Box) and agents.color==1:
                    boxPositions.append({"x": x, "y":0.5, "z":z})
        return jsonify({'positions':boxPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, agentModel
    if request.method == 'GET':
        agentModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

@app.route('/finish', methods=['GET'])
def finish():
    global agentModel
    if request.method == 'GET':
        return str(agentModel.count_left())

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)