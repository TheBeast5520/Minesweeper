# Please run this program in IDLE

from tkinter import *
import random
from tkinter import messagebox
from math import floor
import sys

# The time program runs on a recursive loop, where it is call itself twice
# every second. In order to let the program run for as long as possible, I am
# setting the recursion depth higher. The new limit is 5000, which should
# theoretically let one game run for well over 20 minutes, by which time
# the minesweeper game should have been played.

sys.setrecursionlimit(5000)

class mineSweeperCell(Label):
    # colormap for numbers
    colormap = ['','blue','darkgreen','red','purple','maroon','cyan','black','dim gray']
    def __init__(self,master,coord):
        # initialize
        Label.__init__(self,master,height=1,width=2,text='',\
                       bg='white',font=('Arial',12),relief='raised')
        # set up attributes
        self.coord = coord
        self.number = 0
        self.bomb = False
        self.flagged = False
        self.state = 'undet' # 'undet', 'det'
        # listeners
        self.bind('<Button-1>',self.detonate)
        self.bind('<Button-2>',self.toggleFlag)
        self.bind('<Button-3>',self.toggleFlag)

    def toggleBomb(self):
        '''toggles the attribute for whether the cell has a bomb or not'''
        if self.bomb:
            self.bomb=False
        else:
            self.bomb=True

    def toggleFlag(self,a=[0,0],dowin=True):
        # toggles the attribute for whether the cell is flagged or not. Note here, that it also changes the 
        # label which shows how many flags are left.
        if self.state=='undet':
            if self.flagged:
                self.flagged=False
                self['text']=''
                self.master.flagsLeft+=1
                self.master.flagsLeftLabel = Label(text="Flags left: "+str(self.master.flagsLeft),font=("Arial",12))
                self.master.flagsLeftLabel.grid(row=self.master.height,column=0,columnspan=self.master.width)
            else:
                if self.master.flagsLeft > 0:
                    self.flagged=True
                    self['text']='*'
                    self.master.flagsLeft -= 1
                    self.master.flagsLeftLabel = Label(text="Flags left: "+str(self.master.flagsLeft),font=("Arial",12))
                    self.master.flagsLeftLabel.grid(row=self.master.height,column=0,columnspan=self.master.width)
        # an extra parameter defaulted to True which checks if the player has won or not after this is flagged
        # currently this feature is not being put to use, but at one point I wrote some code that made it so that 
        # if the player used all the flags and all of the flags were in the correct place, the program would
        # auto-detonate the rest of the cells. 
        if dowin:
            self.master.win()

    def setText(self,num):
        # sets the color of the number in the cell based on the number
        color = self.colormap[num]
        if num==0:
            self['text']=""
        else:
            self['fg']=color
            self['text']=str(num)

    def detonate(self,a = [0,0],dowin=True):
        # detonates the cell. If a bomb, ends game, else, updates a few attributes and calls the autoclear function
        if not (self.flagged or self.state=='det'):
            if self.bomb:
                self.master.outcome='loss'
                self.master.end_game()
            else:
                self['relief']='sunken'
                self['bg']='lightgray'
                self.state='det'
                self.master.nobombs -= 1
                self.setText(self.number)
                self.master.startcoord=self.coord
                self.master.autoClear()
        # extra parameter defaulted to True to call the win function.
        if dowin:
            self.master.win()
        

class mineSweeper(Frame):
    
    def __init__(self, master, width, height, numBombs):
        print("Welcome to Minesweeper! Right-click to detonate "+\
              "and left-click to flag.\n")
        print("If you detonate"+\
              " all the non-bomb cells, the rest of the board will automatica"+\
              "lly be flagged for you correctly, and you win! Good luck!")
        # set up Frame
        Frame.__init__(self, master)
        self.grid()
        # set up grid of minesweeper
        self.cells = []
        self.bombs = []
        for i in range(height):
            for j in range(width):
                self.cells.append(mineSweeperCell(self,(i,j)))
                self.cells[i*width+j].grid(row=i,column=j)
        # setting up attributes
        self.oneDet = False
        self.width = width
        self.height = height
        self.numBombs = numBombs
        self.outcome='notDone'
        self.startcoord=0
        self.flagsLeft = numBombs
        self.nobombs = width*height-self.flagsLeft
        self.flagsLeftLabel = Label(text="Flags left: "+str(self.flagsLeft),font=("Arial",12))
        self.flagsLeftLabel.grid(row=height,column=0,columnspan=width)
        self.timeLabel=Label(text="Time: 0")
        self.timeLabel.grid(row=height+1,column=0,columnspan=width)
        self.time=0
        self.done=False
        self.end_gameDone=False

    def end_game(self):
        # Ends game. If it is a loss, it also shows which bombs were not flagged, and if the player flagged any cells that were not
        # bombs, it also shows that by, 'nb'
        if self.end_gameDone==True:
            return 0
        self.end_gameDone=True
        if self.outcome=='win':

            messagebox.showinfo('Minesweeper','Congratulations -- you won!',parent=self)

            self.fullUnbind()
        else:
            messagebox.showerror('Minesweeper','KABOOM! You lose.',parent=self)
            self.fullUnbind()
            for i in self.cells:
                if i.bomb and i.state=='undet' and not i.flagged:
                    i['bg']='red'
                    i['text']='*'
                elif (not i.bomb) and i.flagged:
                    i['text']='nb'

        self.flagsLeftLabel['text']="GAME OVER"
        # creates a button to end game and continue the program. 
        self.endButton=Button(text='Click to continue',command=self.closeWindow)
        
        self.endButton.grid(row=self.height+2,column=0,columnspan=self.width)

    def autoClear(self):
        # goal of this function is to autoclear any cells if it can/should
        if not self.oneDet:
            # I added a feature that I found was missing in several other minesweeper renditions I have played: the player hits a bomb
            # on the first try. The player can't do anything about this, so I made it so that the program generates the bombs AFTER
            # the player cleared the first cell. It also starts the time after the first cell is cleared.
            self.start_time()
            self.oneDet = True
            counter = 0
            while (counter != self.numBombs):
                # while loop to generate the bombs. counter is increased every time a bomb is actually added.
                # code to randomize bombs below
                i = random.randrange(self.height)
                j = random.randrange(self.width)
                # if bomb is in one of the 8 cells surrounding the only detonated cell or the detonated cell itself, continue. These ones
                # can't be a bomb.
                if (i in [self.startcoord[0]-1, self.startcoord[0], self.startcoord[0]+1]) and\
                   (j in [self.startcoord[1]-1, self.startcoord[1],self.startcoord[1]+1]):
                    continue
                if not (self.cells[i*self.width+j].bomb or \
                        self.cells[i*self.width+j].state=='det'):
                    # otherwise, add the bomb if that cell does not already contain a bomb
                    self.cells[i*self.width+j].toggleBomb()
                    counter += 1
            for a in range(len(self.cells)):
                # sets the numbers for all the cells, we won't have to set the number for any cell after this.
                i = self.cells[a].coord[0]
                j = self.cells[a].coord[1]
                self.cells[a].number=self.findNum((i,j))
        changes = False
        for i in self.cells:
            # for all cells
            cellCoord=i.coord
            if i.number==0 and i.state=='det':
                # if it has 0 bombs surrounding it AND it is detonated
                for a in [cellCoord[0]-1, cellCoord[0], cellCoord[0]+1]:
                    for b in [cellCoord[1]-1, cellCoord[1], cellCoord[1]+1]:
                        # go through the cells around it
                        if not (a < 0 or a >= self.height or b < 0 or b >= self.width\
                                or (a==cellCoord[0] and b==cellCoord[1])):
                            # also check if it is off the grid or not
                            if self.cells[a*self.width+b].state=='undet':
                                # if it is undetonated, detonate it (but don't call autoClear, that would create infinite loops)
                                self.cells[a*self.width+b].detonate(False)
                                changes = True
        # if any new cells were detonated, we call the autoClear function again, just in case we cleared another '0' cell.
        if changes:
            self.autoClear()
        # see if the player has won
        self.win()
                
    def findNum(self,cellCoord):
        # finds the number of bombs for each cell
        num = 0
        for a in [cellCoord[0]-1, cellCoord[0], cellCoord[0]+1]:
            for b in [cellCoord[1]-1, cellCoord[1], cellCoord[1]+1]:
                # check in all surrounding cells
                if not (a < 0 or a >= self.height or b < 0 or b >= self.width\
                        or (a==cellCoord[0] and b==cellCoord[1])):
                        # check if it is the cell itself, or if the cell it is trying to access is off the board or not
                        if self.cells[a*self.width+b].bomb:
                            # if it has a bomb, add one to the number
                            num+=1
        # return the number of bombs!
        return num

    def win(self):
        # the below code that is commented out was to autodetonate all the cells if all the flags are placed correctly, but since 
        # that scenario leaves some space for guessing, I took it out.
##        if self.flagsLeft==0:
##            gameover=True
##            for i in self.cells:
##                if i.bomb and (not i.flagged):
##                    gameover=False
##            if gameover:
##                for i in self.cells:
##                    if i.state=='undet':
##                        i.detonate(False)
##                self.outcome='win'
##                self.end_game()
        # check if all cells have been detonated correctly. Player cannot guess with this, if the player guesses and is incorrect, he/she
        # loses. So, if there are no bombs left, we go into tihs function
        if self.nobombs==0:
            for i in self.cells:
                # for all cells
                if i.state=='undet' and not i.flagged:
                    # if undetonated and not flagged, flag it.
                    i.toggleFlag(dowin=False)
            # set the outcome to win and call the end_game function
            self.outcome='win'
            self.end_game()
        else:
            # else
            gameover=True
            for i in self.cells:
                if not (i.state=='det' or i.flagged):
                    # if any of the cells are not detonated or not flagged, game is not over
                    gameover=False
                   
            if gameover:
                # However, if game is over, outcome = win and call the end_game function
                self.outcome='win'
                self.end_game()

    def fullUnbind(self):
        # unbinds the cells, so player cannot continue to detonate/flag cells.
        for i in self.cells:
            i.unbind("<Button-1>")
            i.unbind("<Button-3>")

    def start_time(self):
        # function keeps time accurate to a half of a second. 
        if self.outcome=='win' or self.outcome=='loss':
            # if the game has ended, stop the timer.
            return 0
        self.time += 0.5
        self.timeLabel['text']="Time: " + str(floor(self.time))
        self.after(500,self.start_time)

    def closeWindow(self):
        # closes tkinter window
        self.master.destroy()

def play_minesweeper(width, height, numBombs):
    # sets up a minesweeper game
    root = Tk()
    root.title('Minesweeper')
    game = mineSweeper(root, width, height, numBombs)
    root.mainloop()

def play_again():
    # asks for inputs and plays the game accordingly
    a = int(input("What do you want the width to be? "))
    b = int(input("What do you want the height to be? "))
    c = int(input("How many bombs do you want there to be? "))
    play_minesweeper(a,b,c)
    while True:
        if input("Do you want to play again? (y/n) ").lower().strip()=='y':
            if input("Do you want to use the same inputs as last time? (y/n) ").lower().strip()\
               =='y':
                play_minesweeper(a,b,c)
            else:
                a = int(input("What do you want the width to be? "))
                b = int(input("What do you want the height to be? "))
                c = int(input("How many bombs do you want there to be? "))
                play_minesweeper(a,b,c)
        else:
            print("Thank you for playing Minesweeper!")
            break
play_again()
