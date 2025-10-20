import pygame as pg
from pygame.locals import *
from Logic.Board import Board
import sys
import time

pg.init()

class Game:
    # General variables of the game
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 700 
    CELL_SIZE = 60
    BOARD_SIZE = 8
    BOARD_TOPLEFT = (100,100)
    board = Board()
    

    def __init__(self):
        self.screen = pg.display.set_mode((Game.SCREEN_WIDTH, 
                                           Game.SCREEN_HEIGHT))
        pg.display.set_caption("myOthello")
    
        self.running = True
        self.startTime = pg.time.get_ticks()

        self.turn = self.board.BLACK

        self.last_move = -1, -1
    
    # Drawing the initial empty board
    def drawBoard(self):
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                rect = pg.Rect(self.BOARD_TOPLEFT[0] + col*self.CELL_SIZE,
                               self.BOARD_TOPLEFT[1] + row*self.CELL_SIZE,
                               self.CELL_SIZE, self.CELL_SIZE)
                pg.draw.rect(self.screen, (0, 100, 0), rect)
                pg.draw.rect(self.screen, (0, 0, 0), rect, 1)
    # redrawing board with the correct discs           
    def redrawBoard(self):
        self.announceWinner()
        self.piecesTracking()
        self.highlightPossibleMoves()
        for row in range(self.BOARD_SIZE):
                for col in range(self.BOARD_SIZE):
                    if self.board.board[row, col] == self.board.BLACK:
                        self.drawDisc(self.board.BLACK, self.findSquareTopleftCoordsByIndex((row, col)))
                    elif self.board.board[row, col] == self.board.WHITE:
                        self.drawDisc(self.board.WHITE, self.findSquareTopleftCoordsByIndex((row,col)))
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
        square = self.findSquareTopleftCoords((mx, my))
        index = self.getSquareIndex((mx, my))

        if square and index:
            x, y = square
            row, col = index   # unpack the grid coordinates
            if self.board.board[row, col] == 0:  # empty cell
                rect = pg.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE)
                pg.draw.rect(self.screen, (0, 170, 0), rect, 4)
    # finding top left coords of a square in the board using any coords in the square
    def findSquareTopleftCoords(self, coords: tuple[int, int]) -> tuple[int, int] | None:
        square = self.getSquareIndex(coords)
        if square is None:
            return None  # mouse outside board

        col, row = square
        c = self.BOARD_TOPLEFT[0] + col * self.CELL_SIZE
        r = self.BOARD_TOPLEFT[1] + row * self.CELL_SIZE
        return (c, r)
    # finding top left coords using the index of the square
    def findSquareTopleftCoordsByIndex(self, index: tuple[int, int]) -> tuple[int, int] | None:
        row, col= index
        x, y = self.BOARD_TOPLEFT

        c = self.BOARD_TOPLEFT[0] + col*self.CELL_SIZE
        r = self.BOARD_TOPLEFT[1] + row*self.CELL_SIZE

        return (r, c)  
    # getting the index of a square using coords inside it
    def getSquareIndex(self, coords: tuple[int, int]):
        mx, my = coords
        x, y = self.BOARD_TOPLEFT

        if (mx< x or mx>=x+8*self.CELL_SIZE) or (my<y or my>=y+8*self.CELL_SIZE):
            return 
        
        col = (mx - self.BOARD_TOPLEFT[0]) // self.CELL_SIZE
        row = (my - self.BOARD_TOPLEFT[1]) // self.CELL_SIZE

        return(col, row)
    # handling clicking events 
    def handleMouseClick(self) -> None:
        mx, my = pg.mouse.get_pos()
        square = self.getSquareIndex((mx, my))
        moves = self.board.findAllPossibleMoves(self.turn)
        if square:
            row, col = square
            if self.board.board[row, col] ==0 and (row, col) in moves:
                self.board.board[row, col] = self.turn
                self.board.setDiscs(row, col, self.turn)
                self.turn = -1 * self.turn
                self.last_move =(col, row)
               
    def announceWinner(self):
        if self.board.isGameOver() is True:
                my_font = pg.font.SysFont('Arial', 30) 
                text_surface = my_font.render('Game ended', True, (255, 255, 255)) 
                # Text, Antialiasing, Color (RGB)
                self.screen.blit(text_surface, (700, 500)) # Text surface, Position (x, y)

                if self.board.white_disc_count > self.board.black_disc_count:
                    winner = my_font.render('White won!', True, (255, 255, 255))
                    self.screen.blit(winner, (700, 300))
                elif self.board.white_disc_count < self.board.black_disc_count:
                    winner = my_font.render('Black won!', True, (255, 255, 255))
                    self.screen.blit(winner, (700, 300))
                else:
                    winner = my_font.render('it is a tie!', True, (255, 255, 255))
                    self.screen.blit(winner, (700, 300))

    def highlightPossibleMoves(self):
        moves = self.board.findAllPossibleMoves(self.turn)

        overlay = pg.Surface(self.screen.get_size(), pg.SRCALPHA)

        for move in moves: 
            row, col = move
            x, y = self.findSquareTopleftCoordsByIndex((row, col))
            center = (x + self.CELL_SIZE // 2, y + self.CELL_SIZE // 2)

            if self.turn == 1:  # 1 for black 
                pg.draw.circle(overlay, (0, 0, 0, 60), center, 26)
            else:  # 0 for white 
                pg.draw.circle(overlay, (255, 255, 255, 100), center, 26)

        self.screen.blit(overlay, (0, 0))

    def piecesTracking(self):
        my_font = pg.font.SysFont('Arial', 30) 
        white_num = self.board.whiteDiscCount()
        black_num = self.board.blackDiscCount()
        white = my_font.render(f"White : {white_num}", True, (255, 255, 255)) 
        black = my_font.render(f"Black : {black_num}", True, (255, 255, 255))
        self.screen.blit(white, (700, 150))
        self.screen.blit(black, (700, 100))

    def timeLapse(self):
        elapsed_ms = pg.time.get_ticks() - self.startTime
        elapsed_sec = elapsed_ms // 1000
        minutes = elapsed_sec // 60 
        seconds = elapsed_sec % 60

        my_font = pg.font.SysFont('Arial', 24)
        text_surface = my_font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
        self.screen.blit(text_surface, (700, 50))

    def currentTurn(self):
        if self.turn == self.board.BLACK:
            current = "Black"
        else:
            current = "White"
        my_font = pg.font.SysFont('Arial', 24)
        text_surface = my_font.render(f"Current Turn: {current}", True, (255, 255, 255))
        self.screen.blit(text_surface, (700, 200))

    def lastMove(self):
        lastr, lastc = self.last_move
        if lastr == -1 and lastc == -1:
            return
        my_font = pg.font.SysFont('Arial', 24)
        text_surface = my_font.render(f"last Turn: ({lastr+1}, {lastc+1})", True, (255, 255, 255))
        self.screen.blit(text_surface, (700, 300))

    #def chooseRole(self):
        #to implement

    #def chooseMatchType(self):
        #to implement

    
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

            self.redrawBoard()
            self.currentTurn()
            self.hover()
            self.timeLapse()
            self.lastMove()
            pg.display.flip() 
    

