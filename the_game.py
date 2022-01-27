import random
# from select import select

from numpy import NaN

#from enum import Enum

import sys

MAX_VALUE = 10
MIN_VALUE = 1

MINIMUM_NUMBER_OF_TURNS = 2

class Deck:
    
    def __init__(self):
        self.reset()
        
    def reset(self):
        """create a new shuffled deck with cards from 2 to 99 and set the draw index to zero."""
        self.deck = list(range(MIN_VALUE+1,MAX_VALUE))
        random.shuffle(self.deck)
        self.index = 0
        
    def draw(self, n):
        """draw the next n cards from the deck."""
        
        # Adjust the number of cards returned when not enough cards in the deck
        index_to = min([len(self.deck), self.index+n])       
        
        # get the values from the deck and adjust the index accordingly
        r = self.deck[ self.index:index_to ]
        self.index = index_to        
        return r
            
    def print(self):
        for i in range(len(self.deck)):
            if i != 0:
                print(", ", end="")
                
            if i == self.index:
                print("->", end="")
                
            print(self.deck[i], end="")
            
        print("")
        
    def len(self):
        return len(self.deck)
    
    def nCardsLeft(self):
        return self.len() - self.index
    
    def isEmpty(self):
        #print("index=" + str(self.index) + "  len=" + str(len(self.deck)))
        return self.index == len(self.deck)

            
   
class Player:
    
    def __init__( self, name, hand_size = 7 ):
        self.name = name
        self.hand_size = hand_size
        self.hand = []        
    
    def countMissing (self):
        """Determine how many cards are needed to refill the hand"""
        return self.hand_size - len(self.hand)
    
    def addCards( self, cards ):
        self.hand.extend(cards)
        self.hand.sort()
        
    def removeCard( self, card ):
        if card in self.hand:
            self.hand.remove(card)
            return True
        else:
            return False
        
    def canPlay(self, piles):
        if len(self.hand) == 0:
            return False
        for card in [min(self.hand), max(self.hand)]:
            for pile in piles:
                if pile.checkAllowed(card) == True:
                    return True
        return False
    
    def refillHand(self, deck):
        self.addCards(deck.draw(self.countMissing()))
    
        
    def print(self):
        print("Player " + self.name + ": ", end="")
        print(self.hand)
        
    def checkCard(self, card):
        if card in self.hand:
            return True
        else:
            return False
        
class HumanPlayer(Player):
    def __init__(self, name, hand_size = 7):
        Player.__init__(self, name, hand_size)
        
    def dispHand(self):
         print("Your Hand: " + str(self.hand))
    
        
    def takeTurn(self, piles, deck):
        
        self.addCards(deck.draw(self.countMissing()))
            
        keep_playing = True
        turn_counter = 0
        
        choose_card_message = "Choose a card: "
        
        while keep_playing:
            
            GameInterface.dispPiles(piles)
            self.dispHand()
            
            if turn_counter < MINIMUM_NUMBER_OF_TURNS:
                if self.canPlay(piles) == False:
                    print("No possible turns!")
                    return False
            
            selected_card = -1
            while self.checkCard(selected_card) == False:
                selected_card = input(choose_card_message)
                
                if turn_counter >= MINIMUM_NUMBER_OF_TURNS and selected_card == "":
                    keep_playing = False
                    break
                
                try:
                    selected_card = int(selected_card)
                except ValueError:
                    continue
                
                if self.checkCard(selected_card) == False:
                    print("You do not have this card!")
        
            if turn_counter >= MINIMUM_NUMBER_OF_TURNS and selected_card == "":
                keep_playing = False
                continue
        
            selected_pile = -1
            while True:
                try:
                    selected_pile = int(input("Choose a pile: ")) -1
                except ValueError:
                    continue
                if selected_pile not in range(len(piles)):
                    print("Invalid pile")
                else:
                    break
                    
                    
            if piles[selected_pile].playCard(selected_card) == False:
                print("Card cannot be played on this pile!")
                continue
            
            self.removeCard(selected_card)
            
            turn_counter += 1
            
            if turn_counter == 2:
                choose_card_message = "Choose a card or press ENTER to finish turn: "
        
        return True

class Pile:
    def __init__(self, increasing=True):
        self.increasing=increasing
        
        if self.increasing:
            self.pile=[MIN_VALUE]
            self.value=MIN_VALUE
        else:
            self.pile=[MAX_VALUE]
            self.value=MAX_VALUE
            
    def checkAllowed(self, card):
        allow = False
        if self.increasing:
            if card > self.value:
                allow = True
            elif card == self.value - 10:
                allow = True
                
        else:
            if card < self.value:
                allow = True
            elif card == self.value + 10:
                allow = True
                
        return allow
            
    def playCard( self, card ):
        allow = self.checkAllowed(card)
            
        if allow:
            self.pile.append(card)
            self.value = card
            
        return allow
            
    def print(self):
        print(self.value)


class GameInterface:
    
    def dispPiles(piles):
        for i in range(len(piles)):
            print(str(i+1) + ": " + str(piles[i].value))
        

class TheGame:
    
    def __init__(self, n_piles_increasing = 2, n_piles_decreasing = 2):
        self.piles = []
        for i in range(n_piles_increasing):
            self.piles.append(Pile(increasing=True))
        
        for i in range(n_piles_decreasing):
            self.piles.append( Pile(increasing=False))
            
        self.deck = Deck()
        
        self.players = []
        
        self.current_player = 0
        self.turn_counter = 0
        
        self.player_alive = []
        
    def addPlayer(self, player):
        if self.turn_counter != 0:
            print("Cannot add player, game already started")
            return
        player.refillHand(self.deck)
        self.players.append(player)
        self.player_alive.append(True)
        
        
    def nextTurn(self):       
        if len(self.players) < 1:
            print ("Not enough player!")
            
        print("~~~~~~~~~~~~~~~~~~~")
            
        self.turn_counter += 1            
        
        print("There are " + str(self.deck.nCardsLeft()) + " cards left on the deck." )
        print("It's " + self.players[self.current_player].name + "'s turn")
    
        self.players[self.current_player].takeTurn(self.piles, self.deck)
        
        self.current_player += 1
        if self.current_player >= len(self.players):
            self.current_player = 0
            
    def won(self):
        for p in self.players:
            if len(p.hand) != 0:
                return False
        if not self.deck.isEmpty():
            return False
        
        return True
    
    def continues(self):
        for p in self.players:
            if p.canPlay(self.piles):
                return True
            
        return False
         
            
                    
            
def main ():
    game = TheGame()
    
    print(game.deck.deck)
    
    game.addPlayer(HumanPlayer("Julia"))
    game.addPlayer(HumanPlayer("Christian"))
    
    while game.continues():
        game.nextTurn()
        
    
    if game.won() == True:
        print("   YAY You won :)")
        
    else:
        print ("  GAME OVER :(")
        
        cards_left = []
        for p in game.players:
            cards_left.extend(p.hand)
        
        cards_left.extend(game.deck.deck[game.deck.index:])
        print ("Cards left: " + str(cards_left))
        
        
if __name__ == "__main__":
    main()
        
                
    