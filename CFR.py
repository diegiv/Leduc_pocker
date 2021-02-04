from Game import *
from itertools import *
import random
random.seed(69)

def initialize(game):

    suits = 2
    #cards = ['9', 'T', 'J', 'Q', 'K']
    #cards = ['5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    cards = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    cards = [item for item in cards for i in range(suits)]

    expected_game_value = 0
    time = 5000000
    
    for t in range(time):
        if t % 1000 == 0:
            print(t)
        curr_cards = cards.copy()
        random.shuffle(curr_cards)
        sample1 = curr_cards.pop()
        sample2 = curr_cards.pop()
        sampling = [sample1 + sample2, curr_cards]

        expected_game_value += cfr(game, '/', sampling, t, 1, 1)

    expected_game_value /= time
    display_results(expected_game_value, game.infosets)


def cfr(game, history, sampling, time, reach_pr1, reach_pr2):
   
    curr_node = game.nodes[history]

    if type(curr_node) == LeafNode:
        parent_player = game.nodes[curr_node.parent].player
        payoff = curr_node.payoffs[int(parent_player[1])-1]
        return payoff
    elif type(curr_node) == ChanceNode:
        if curr_node.history == '/':
            action = sampling[0]
            next_node = game.next_node(game.nodes[history], action)
            return cfr(game, next_node.history, sampling, time, reach_pr1, reach_pr2)
        else:
            counter = 0
            for action in sampling[1]:
                next_node = game.next_node(game.nodes[history], action)
                counter += cfr(game, next_node.history, sampling, time, reach_pr1, reach_pr2)
            return counter/len(sampling[1])
        
    info_set = curr_node.infoset

    if curr_node.player == 'P1':
        strategy = info_set.get_strategy(reach_pr1)
    elif curr_node.player == 'P2':
        strategy = info_set.get_strategy(reach_pr2)
    value = 0

    # Counterfactual utility per action.
    action_value = np.zeros(info_set.num_actions)

    def compl(num, base=14):
        if num > base:
            return base-(num-base)
        elif num < base:
            return base+(base-num)

    for i, a in enumerate(curr_node.actions):
        next_node = game.next_node(curr_node, a)
        if curr_node.player == 'P1':
            action_value[i] = cfr(game, next_node.history, sampling, time, reach_pr1 * strategy[i], reach_pr2)
        elif curr_node.player == 'P2':
            action_value[i] = cfr(game, next_node.history, sampling, time, reach_pr1, reach_pr2 * strategy[i])
        
        if not(type(next_node) is LeafNode):
            #action_value[i] = compl(action_value[i])
            action_value[i] = action_value[i] * -1

        value += strategy[i] * action_value[i]

    if curr_node.player == 'P1':
        for i, a in enumerate(curr_node.actions):
            info_set.cum_regret[i] += reach_pr2 * (action_value[i] - value) 
            info_set.cum_strategy[i] += reach_pr1 * strategy[i]

    elif curr_node.player == 'P2':
        for i, a in enumerate(curr_node.actions):
            info_set.cum_regret[i] += reach_pr1 * (action_value[i] - value) 
            info_set.cum_strategy[i] += reach_pr2 * strategy[i]
    
    return value
    

def display_results(ev, infosets):

    text = open("output - Leduc_C.txt", "w")
    
    for i in infosets:
        print(infosets[i])
        for x in infosets[i].mapping:            
            text.write('infoset ')
            text.write(x.history)
            text.write(' strategies')
            for j, a in enumerate(infosets[i].nodes[0].actions):
                strat = str('{:03.5f}'.format(infosets[i].avg_strategy[j]))
                text.write(' ' + a + '=' + strat)
            text.write('\n')
    text.close()

    print('player 1 expected value: {}'.format(ev))
    print('player 2 expected value: {}'.format(-1 * ev))

    
    