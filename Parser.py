from Game import *
from Abstraction import *
import CFR

#Read the input text file and split it into single lines

text = open("Leduc_C.txt", "r").read()
lines = text.split('\n')

#Separate the lines by object type (node or infoset) and store them into appropriate data lists 

nodes_list = []
infosets_list = []

for line in lines:
    if(line.startswith('node')):
        nodes_list.append(line)
    elif(line.startswith('infoset')):
        infosets_list.append(line)

nodes = {}
infosets = {}

for node in nodes_list:
    
    slices = node.split(' ')
    history = slices[1]
    node_type = slices[2]

    if(node_type == 'leaf'):
        payoffs = [int(float(slices[4][2:])), int(float(slices[5][2:]))]
        new_node = LeafNode(history, payoffs)
        nodes[new_node.history] = new_node
    
    elif(node_type == 'chance'):
        actions = []
        chances = {}
        for i in range(4, len(slices)):
            slc = slices[i].split('=')
            chances[slc[0]] = int(float(slc[1]))
            actions.append(slc[0])
        new_node = ChanceNode(history, 'C', actions, chances)
        nodes[new_node.history] = new_node

    elif(node_type == 'player'):
        actions = []
        for i in range(5, len(slices)):
            actions.append(slices[i])
        player = 'P' + slices[3]
        new_node = DecisionNode(history, player, actions)
        nodes[new_node.history] = new_node

for infoset in infosets_list:
    slices = infoset.split(' ')
    history = slices[1]
    nodes_of_set = []

    for i in range(3, len(slices)):
        nodes_of_set.append(nodes[slices[i]])
    
    new_set = InfoSet(history, nodes_of_set)
    infosets[new_set.history] = new_set

game = GameTree(nodes, infosets)

new_game = abstract(game, 7, 7)
CFR.initialize(new_game)

#CFR.initialize(game)