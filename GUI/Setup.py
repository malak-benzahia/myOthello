import pygame as pg
from pygame.locals import *
import time
import sys

pg.init()

class Game:
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 700 
    CELL_SIZE = 60
    BOARD_SIZE = 8
    BOARD_TOPLEFT = (100,100)

    def drawBoard(self):
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                rect = pg.Rect(self.BOARD_TOPLEFT[0] + col*self.CELL_SIZE,
                               self.BOARD_TOPLEFT[1] + row*self.CELL_SIZE,
                               self.CELL_SIZE, self.CELL_SIZE)
                pg.draw.rect(self.screen, (0, 100, 0), rect)
                pg.draw.rect(self.screen, (0, 0, 0), rect, 1)

    # drawing the discs 
    def drawDisc(self, color: int, coords: tuple[int, int]) -> None:
        center = (coords[0] + self.CELL_SIZE // 2, coords[1] + self.CELL_SIZE // 2)
        if color == 1: # 1 for black disc
            pg.draw.circle(self.screen, (0, 0, 0), center, 26)
        else: # 0 for white disc
            pg.draw.circle(self.screen, (255, 255, 255), center, 26)


    # hover effect 
    def hover(self) -> None:
        mx, my = pg.mouse.get_pos()
        square = self.findSquare((mx, my))

        if square:
            x, y = square
            if (1, square) not in self.discs and (0, square) not in self.discs:
                rect = pg.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE)
                pg.draw.rect(self.screen, (0, 170, 0), rect, 60, 10)

        


    def findSquare(self, coords: tuple[int, int]) -> tuple[int, int] | None:
        mx, my = coords
        x, y = self.BOARD_TOPLEFT

        if (mx< x or mx>x+8*self.CELL_SIZE) or (my<y or my>y+8*self.CELL_SIZE):
            return 
        
        col = (mx - self.BOARD_TOPLEFT[0]) // self.CELL_SIZE
        row = (my - self.BOARD_TOPLEFT[1]) // self.CELL_SIZE

        c = self.BOARD_TOPLEFT[0] + col*self.CELL_SIZE
        r = self.BOARD_TOPLEFT[1] + row*self.CELL_SIZE

        return (c, r)
    


    def __init__(self):
        self.screen = pg.display.set_mode((Game.SCREEN_WIDTH, 
                                           Game.SCREEN_HEIGHT))
        pg.display.set_caption("myOthello")
    
        self.running = True
        
        self.turn = 1  # 1 = black, 0 = white
        # store discs as (color, x, y)
        self.discs = []



    def handleMouseClick(self) -> None:
        mx, my = pg.mouse.get_pos()
        square = self.findSquare((mx, my))

        if square:
            self.discs.append((self.turn, square))
            self.turn = 1 - self.turn 


    def start(self) -> None:
        
        while self.running :
            for event in pg.event.get():
                if event.type == QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.handleMouseClick()
            
            self.screen.fill((50, 50, 50))      # background color
            self.drawBoard()

             # draw all discs stored
            for color, pos in self.discs:
                self.drawDisc(color, pos)                  # draw grid
            self.hover()
            pg.display.flip() 
    

