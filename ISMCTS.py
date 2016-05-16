# This is a very simple Python 2.7 implementation of the Information Set Monte Carlo Tree Search algorithm.
# The function ISMCTS(rootstate, itermax, verbose = False) is towards the bottom of the code.
# It aims to have the clearest and simplest possible code, and for the sake of clarity, the code
# is orders of magnitude less efficient than it could be made, particularly by using a 
# state.GetRandomMove() or state.DoRandomRollout() function.
# 
# An example GameState classes for Knockout Whist is included to give some idea of how you
# can write your own GameState to use ISMCTS in your hidden information game.
# 
# Written by Peter Cowling, Edward Powley, Daniel Whitehouse (University of York, UK) September 2012 - August 2013.
# 
# Licence is granted to freely use and distribute for any sensible/legal purpose so long as this comment
# remains in any distributed code.
# 
# For more information about Monte Carlo Tree Search check out our web site at www.mcts.ai
# Also read the article accompanying this code at ***URL HERE***

from math import *
import random, sys
from game import Game as UNOGame
from player import Player as UNOPlayer
from utils import list_subtract_unsorted
import card as c


class GameState:
    """ A state of the game, i.e. the game board. These are the only functions which are
        absolutely necessary to implement ISMCTS in any imperfect information game,
        although they could be enhanced and made quicker, for example by using a
        GetRandomMove() function to generate a random move during rollout.
        By convention the players are numbered 1, 2, ..., self.numberOfPlayers.
    """

    def __init__(self):
        pass

    def GetNextPlayer(self, p):
        """ Return the player to the left of the specified player
        """
        raise NotImplementedError()

    def Clone(self):
        """ Create a deep clone of this game state.
        """
        raise NotImplementedError()

    def CloneAndRandomize(self, observer):
        """ Create a deep clone of this game state, randomizing any information not visible to the specified observer player.
        """
        raise NotImplementedError()

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerToMove.
        """
        raise NotImplementedError()

    def GetMoves(self):
        """ Get all possible moves from this state.
        """
        raise NotImplementedError()

    def GetResult(self, player):
        """ Get the game result from the viewpoint of player.
        """
        raise NotImplementedError()

    def __repr__(self):
        """ Don't need this - but good style.
        """
        pass


class UNOState(GameState):
    """ A state of the game UNO.
    """

    def __init__(self, game):
        """ Initialise the game state. n is the number of players (from 2 to 7).
        """
        self.game = game

    @property
    def playerToMove(self):
        return self.game.current_player

    @property
    def numberOfPlayers(self):
        return len(self.game.players)

    def CloneAndRandomize(self, observer):
        """ Create a deep clone of this game state.
        """
        game = UNOGame(None)
        game.deck.cards.append(game.last_card)
        game.draw_counter = self.game.draw_counter

        game.last_card = self.game.last_card

        game.deck.cards = list_subtract_unsorted(game.deck.cards,
                                                 self.game.deck.graveyard)
        game.deck.graveyard = list(self.game.deck.graveyard)

        for player in self.game.players:
            p = UNOPlayer(game, None)
            if player is observer:
                p.cards = list(player.cards)
            else:
                for i in range(len(player.cards)):
                    p.cards.append(game.deck.draw())

        return UNOState(game)

    def DoMove(self, move):
        """ Update a state by carrying out the given move.
            Must update playerToMove.
        """
        if move == 'draw':
            for n in range(self.game.draw_counter or 1):
                self.game.current_player.cards.append(
                    self.game.deck.draw()
                )

            self.game.draw_counter = 0
            self.game.turn()
        else:
            self.game.current_player.cards.remove(move)

            self.game.play_card(move)
            if move.special:
                self.game.turn()
                self.game.choosing_color = False

    def GetMoves(self):
        """ Get all possible moves from this state.
        """
        if self.game.current_player.cards:
            playable = self.game.current_player.playable_cards()
            playable_converted = list()
            for card in playable:
                if not card.color:
                    for color in c.COLORS:
                        playable_converted.append(
                            c.Card(color, None, card.special)
                        )
                else:
                    playable_converted.append(card)

            # playable_converted.append('draw')
            return playable_converted or ['draw']
        else:
            return list()

    def GetResult(self, player):
        """ Get the game result from the viewpoint of player.
        """
        return 1 if not player.cards else 0

    def __repr__(self):
        """ Return a human-readable representation of the state
        """
        return '\n'.join(
            ['%s: %s' % (p.user, [str(c) for c in p.cards])
             for p in self.game.players]
        ) + "\nDeck: %s" % str([str(crd) for crd in self.game.deck.cards]) \
          + "\nGrav: %s" % str([str(crd) for crd in self.game.deck.graveyard])


class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
    """

    def __init__(self, move=None, parent=None, playerJustMoved=None):
        self.move = move  # the move that got us to this node - "None" for the root node
        self.parentNode = parent  # "None" for the root node
        self.childNodes = []
        self.wins = 0
        self.visits = 0
        self.avails = 1
        self.playerJustMoved = playerJustMoved  # the only part of the state that the Node needs later

    def GetUntriedMoves(self, legalMoves):
        """ Return the elements of legalMoves for which this node does not have children.
        """

        # Find all moves for which this node *does* have children
        triedMoves = [child.move for child in self.childNodes]

        # Return all moves that are legal but have not been tried yet
        return [move for move in legalMoves if move not in triedMoves]

    def UCBSelectChild(self, legalMoves, exploration=0.7):
        """ Use the UCB1 formula to select a child node, filtered by the given list of legal moves.
            exploration is a constant balancing between exploitation and exploration, with default value 0.7 (approximately sqrt(2) / 2)
        """

        # Filter the list of children by the list of legal moves
        legalChildren = [child for child in self.childNodes if
                         child.move in legalMoves]

        # Get the child with the highest UCB score
        s = max(legalChildren, key=lambda c: float(c.wins) / float(
            c.visits) + exploration * sqrt(log(c.avails) / float(c.visits)))

        # Update availability counts -- it is easier to do this now than during backpropagation
        for child in legalChildren:
            child.avails += 1

        # Return the child selected above
        return s

    def AddChild(self, m, p):
        """ Add a new child node for the move m.
            Return the added child node
        """
        n = Node(move=m, parent=self, playerJustMoved=p)
        self.childNodes.append(n)
        return n

    def Update(self, terminalState):
        """ Update this node - increment the visit count by one, and increase the win count by the result of terminalState for self.playerJustMoved.
        """
        self.visits += 1
        if self.playerJustMoved is not None:
            self.wins += terminalState.GetResult(self.playerJustMoved)

    def __repr__(self):
        return "[M:%s W/V/A: %4i/%4i/%4i]" % (
        self.move, self.wins, self.visits, self.avails)

    def TreeToString(self, indent):
        """ Represent the tree as a string, for debugging purposes.
        """
        s = self.IndentString(indent) + str(self)
        for c in self.childNodes:
            s += c.TreeToString(indent + 1)
        return s

    def IndentString(self, indent):
        s = "\n"
        for i in range(1, indent + 1):
            s += "| "
        return s

    def ChildrenToString(self):
        s = ""
        for c in self.childNodes:
            s += str(c) + "\n"
        return s


def ISMCTS(rootstate, itermax, verbose=False):
    """ Conduct an ISMCTS search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
    """

    rootnode = Node()

    for i in range(itermax):
        node = rootnode

        # Determinize
        state = rootstate.CloneAndRandomize(rootstate.playerToMove)

        # Select
        while state.GetMoves() != [] and node.GetUntriedMoves(
                state.GetMoves()) == []:  # node is fully expanded and non-terminal
            node = node.UCBSelectChild(state.GetMoves())
            state.DoMove(node.move)

        # Expand
        untriedMoves = node.GetUntriedMoves(state.GetMoves())
        if untriedMoves != []:  # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(untriedMoves)
            player = state.playerToMove
            state.DoMove(m)
            node = node.AddChild(m, player)  # add child and descend tree

        # Simulate
        while state.GetMoves() != []:  # while state is non-terminal
            state.DoMove(random.choice(state.GetMoves()))

        # Backpropagate
        while node != None:  # backpropagate from the expanded node and work back to the root node
            node.Update(state)
            node = node.parentNode

    # Output some information about the tree - can be omitted
    if (verbose):
        print(rootnode.TreeToString(0))
    else:
        print(rootnode.ChildrenToString())

    return max(rootnode.childNodes, key=lambda
        c: c.visits).move  # return the move that was most visited


def PlayGame():
    """ Play a sample game between two ISMCTS players.
        *** This is only a demo and not used by the actual bot ***
    """
    game = UNOGame(None)
    me = UNOPlayer(game, "Player 1")
    UNOPlayer(game, "Player 2")
    UNOPlayer(game, "Player 3")
    UNOPlayer(game, "Player 4")
    UNOPlayer(game, "Player 5")

    state = UNOState(game)

    while (state.GetMoves() != []):
        print(str(state))
        # Use different numbers of iterations (simulations, tree nodes) for different players
        m = ISMCTS(rootstate=state, itermax=10, verbose=False)
        # if state.playerToMove is me:
        #     m = ISMCTS(rootstate=state, itermax=1000, verbose=False)
        # else:
        #     m = ISMCTS(rootstate=state, itermax=100, verbose=False)
        print("Best Move: " + str(m) + "\n")
        state.DoMove(m)

    someoneWon = False
    for p in game.players:
        if state.GetResult(p) > 0:
            print("Player " + str(p) + " wins!")
            someoneWon = True
    if not someoneWon:
        print("Nobody wins!")


if __name__ == "__main__":
    PlayGame()
