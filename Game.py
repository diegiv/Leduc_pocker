from functools import reduce
from copy import deepcopy
import numpy as np

class GameRules(object):
    def __init__(self, players, deck, suits, rounds, ante):
        self.players = players
        self.deck = deck
        self.suits = suits
        self.rounds = rounds
        self.ante = ante

class Node(object):
    def __init__(self, history):
        self.history = history
        self.parent = history.rsplit('/',1)[0]

class LeafNode(Node):
    def __init__(self, history, payoffs):
        Node.__init__(self, history)
        self.payoffs = payoffs     #List of payoffs (ex. [10,2])

class DecisionNode(Node):
    def __init__(self, history, player, actions):
        Node.__init__(self, history)
        self.player = player        #Number of player playing in this node (ex. player=1)
        self.actions = actions      #List [] of actions available in this node    
        self.infoset = None

class ChanceNode(DecisionNode):
    def __init__(self, history, player, actions, chances):
        DecisionNode.__init__(self, history, player, actions)
        #i=0
        #for x in chances:
        #    i+=chances[x]
        #for x in chances:
        #    chances[x]= float(chances[x]/i)
        self.chances = chances      #Dictionary of chances
        self.total_chances = sum(chances.values())

class InfoSet(object):
    def __init__(self, history, nodes):
        self.history = history
        self.nodes = nodes          #List [] of nodes belonging to the inf. set
        self.mapping = None
        self.num_actions = (len(nodes[0].actions))
        self.cum_regret = np.zeros(self.num_actions)
        self.cum_strategy = np.zeros(self.num_actions)
        self.strategy = np.repeat(1/self.num_actions, self.num_actions)
        self.strategy_sum = np.zeros(self.num_actions)
        self.avg_strategy = np.zeros(self.num_actions)

    def __str__(self):
        self.avg_strategy = self.get_average_strategy()
        strategies = ['{:03.5f}'.format(x)
                      for x in self.avg_strategy]
        return '{} {} {}'.format(self.history.ljust(6), self.nodes[0].actions, strategies)

    def get_strategy(self, realiz_weight):
        """
        Calculate current strategy from the sum of regret.
        """
        strategy = self.make_positive(self.cum_regret)
        #strategy = np.zeros(self.num_actions)
        #for i in range(self.num_actions):
        #    if self.cum_regret[i] > 0:
        #        strategy[i] = self.cum_regret[i]
        #    else:   
        #        strategy[i] = 0
        norm_sum = sum(strategy)

        if norm_sum > 0:
            strategy = strategy / norm_sum
        else:
            n = self.num_actions
            strategy = np.repeat(1/n, n)

        self.strategy_sum += strategy * realiz_weight
        return strategy

    def get_average_strategy(self):
        """
        Calculate average strategy over all iterations. This is the
        Nash equilibrium strategy.
        """
        
        avg_strategy = np.zeros(self.num_actions)
        norm_sum = sum(self.strategy_sum)

        for i, a in enumerate(avg_strategy):
            if norm_sum > 0:
                avg_strategy[i] = self.strategy_sum[i] / norm_sum
            else:
                avg_strategy[i] = 1.0 / self.num_actions

        return avg_strategy
        
    def make_positive(self, x):
        return np.where(x > 0, x, 0)
        
    def setMapping(self, mapping):
        self.mapping = mapping

class GameTree(object):

    def __init__(self, nodes, infosets):
        #self.rules = rules
        for s in infosets:
            if (type(infosets[s].nodes[0]) == str):
                for i, node in enumerate(infosets[s].nodes):
                    infosets[s].nodes[i] = nodes[node]
        for s in infosets:
            for n in infosets[s].nodes:
                n.infoset = infosets[s]
        self.nodes = nodes
        self.infosets = infosets
        self.deck = {'1':0, '2':1, '3':2, '4':3, '5':4, '6':5, '7':6, '8':7, '9':8, 'T':9, 'J':10, 'Q':11, 'K':12} #LEDUC13
        #self.deck = {'5':0, '6':1, '7':2, '8':3, '9':4, 'T':5, 'J':6, 'Q':7, 'K':8}                                #LEDUC9
        #self.deck = {'9':0, 'T':1, 'J':2, 'Q':3, 'K':4}                                                            #LEDUC5
        self.num_cards = len(self.deck)

    def next_node(self, node, action):
        if (action in node.actions):
            if (node.history != '/'):
                child_history = node.history + '/' + node.player + ':' + action 
            else:
                child_history = '/' + node.player + ':' + action
            return self.nodes[child_history]
        else:
            return None