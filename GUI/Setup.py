import pygame as pg
from pygame.locals import *
from Logic.Board import Board
from AI.minimax import AIController
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
        
        # New attributes for game mode
        self.game_mode = None  # "human_vs_human" or "human_vs_computer"
        self.player_role = None  # BLACK or WHITE (only relevant for human vs computer)
        self.in_menu = True
        self.menu_state = "main"  # "main", "role_selection", or "depth_selection"
        
        # AI attributes
        self.ai_controller = None
        self.ai_depth = 2  # Default depth
        self.ai_thinking = False
        self.ai_move_delay = 500  # Delay in ms before AI makes move (for better UX)
        self.ai_move_time = 0
    
    # Drawing the initial empty board
    def drawBoard(self):
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                rect = pg.Rect(self.BOARD_TOPLEFT[0] + col*self.CELL_SIZE,
                               self.BOARD_TOPLEFT[1] + row*self.CELL_SIZE,
                               self.CELL_SIZE, self.CELL_SIZE)
                pg.draw.rect(self.screen, (0, 100, 80), rect)
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
        # Don't show hover when AI is thinking or it's AI's turn
        if self.game_mode == "human_vs_computer" and self.turn != self.player_role:
            return
            
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
        
        # Check if it's human's turn (for human vs computer mode)
        if self.game_mode == "human_vs_computer" and self.turn != self.player_role:
            return  # Ignore clicks when it's computer's turn
        
        if square:
            row, col = square
            if self.board.board[row, col] ==0 and (row, col) in moves:
                self.board.board[row, col] = self.turn
                self.board.setDiscs(row, col, self.turn)
                self.turn = -1 * self.turn
                self.last_move =(col, row)
    
    def handleAIMove(self):
        """Handle AI move logic"""
        if self.game_mode != "human_vs_computer":
            return
        
        # Check if it's AI's turn
        if self.turn != self.player_role and not self.board.isGameOver():
            current_time = pg.time.get_ticks()
            
            # Start computing move if not already thinking
            if not self.ai_thinking:
                self.ai_thinking = True
                self.ai_move_time = current_time
                self.ai_controller.compute_move(self.board, self.turn)
            
            # Make the move after delay
            if self.ai_controller.has_move_ready() and (current_time - self.ai_move_time) >= self.ai_move_delay:
                move = self.ai_controller.get_move()
                if move:
                    row, col = move
                    self.board.board[row, col] = self.turn
                    self.board.setDiscs(row, col, self.turn)
                    self.last_move = (col, row)
                    self.turn = -1 * self.turn
                self.ai_thinking = False
               
    def announceWinner(self):
        if self.board.isGameOver() is True:
                my_font = pg.font.SysFont('Arial', 30) 
                text_surface = my_font.render('Game ended', True, (255, 255, 255)) 
                self.screen.blit(text_surface, (700, 500))

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
        
        # Show AI indicator
        if self.game_mode == "human_vs_computer" and self.turn != self.player_role:
            current += " (AI)"
            if self.ai_thinking:
                current += " thinking..."
        
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
    
    def showAIDepth(self):
        """Display current AI depth setting"""
        if self.game_mode == "human_vs_computer":
            my_font = pg.font.SysFont('Arial', 20)
            text_surface = my_font.render(f"AI Depth: {self.ai_depth}", True, (255, 255, 255))
            self.screen.blit(text_surface, (700, 250))

    def chooseMatchType(self):
        """Display menu for choosing game mode: Human vs Human or Human vs Computer"""
        self.screen.fill((50, 50, 50))
        
        # Title
        title_font = pg.font.SysFont('Arial', 50, bold=True)
        title = title_font.render('OTHELLO', True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Menu options
        menu_font = pg.font.SysFont('Arial', 36)
        
        # Human vs Human button
        hvh_text = menu_font.render('Human vs Human', True, (255, 255, 255))
        hvh_rect = pg.Rect(400, 300, 400, 70)
        
        # Human vs Computer button
        hvc_text = menu_font.render('Human vs Computer', True, (255, 255, 255))
        hvc_rect = pg.Rect(400, 400, 400, 70)
        
        # Hover effect
        mx, my = pg.mouse.get_pos()
        
        # Draw buttons
        if hvh_rect.collidepoint(mx, my):
            pg.draw.rect(self.screen, (0, 150, 0), hvh_rect)
        else:
            pg.draw.rect(self.screen, (0, 100, 0), hvh_rect)
        pg.draw.rect(self.screen, (255, 255, 255), hvh_rect, 3)
        hvh_text_rect = hvh_text.get_rect(center=hvh_rect.center)
        self.screen.blit(hvh_text, hvh_text_rect)
        
        if hvc_rect.collidepoint(mx, my):
            pg.draw.rect(self.screen, (0, 150, 0), hvc_rect)
        else:
            pg.draw.rect(self.screen, (0, 100, 0), hvc_rect)
        pg.draw.rect(self.screen, (255, 255, 255), hvc_rect, 3)
        hvc_text_rect = hvc_text.get_rect(center=hvc_rect.center)
        self.screen.blit(hvc_text, hvc_text_rect)
        
        # Handle clicks
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if hvh_rect.collidepoint(mx, my):
                    self.game_mode = "human_vs_human"
                    self.in_menu = False
                    self.startTime = pg.time.get_ticks()  # Reset timer when game starts
                    return True
                elif hvc_rect.collidepoint(mx, my):
                    self.game_mode = "human_vs_computer"
                    self.menu_state = "depth_selection"
                    return False
        
        return False
    
    def chooseDepth(self):
        """Display menu for choosing AI depth (np parameter)"""
        self.screen.fill((50, 50, 50))
        
        # Title
        title_font = pg.font.SysFont('Arial', 40, bold=True)
        title = title_font.render('Choose AI Difficulty', True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle_font = pg.font.SysFont('Arial', 24)
        subtitle = subtitle_font.render('(Search Depth - np parameter)', True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(self.SCREEN_WIDTH // 2, 150))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        menu_font = pg.font.SysFont('Arial', 32)
        
        # Depth options
        depth1_text = menu_font.render('Easy ', True, (255, 255, 255))
        depth1_rect = pg.Rect(400, 230, 400, 60)
        
        depth2_text = menu_font.render('Medium ', True, (255, 255, 255))
        depth2_rect = pg.Rect(400, 310, 400, 60)

        depth3_text = menu_font.render('Hard ', True, (255, 255, 255))
        depth3_rect = pg.Rect(400, 390, 400, 60)
        
        
        
        # Hover effect
        mx, my = pg.mouse.get_pos()
        
        # Draw buttons
        buttons = [
            (depth1_rect, depth1_text, 1),
            (depth2_rect, depth2_text, 2),
            (depth3_rect, depth3_text, 3),
            
        ]
        
        for rect, text, depth in buttons:
            if rect.collidepoint(mx, my):
                pg.draw.rect(self.screen, (0, 120, 150), rect)
            else:
                pg.draw.rect(self.screen, (0, 80, 100), rect)
            pg.draw.rect(self.screen, (255, 255, 255), rect, 3)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        # Handle clicks
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                for rect, text, depth in buttons:
                    if rect.collidepoint(mx, my):
                        self.ai_depth = depth
                        self.menu_state = "role_selection"
                        return False
        
        return False

    def chooseRole(self):
        """Display menu for choosing player color in Human vs Computer mode"""
        self.screen.fill((50, 50, 50))
        
        # Title
        title_font = pg.font.SysFont('Arial', 40, bold=True)
        title = title_font.render('Choose Your Color', True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Show selected depth
        depth_font = pg.font.SysFont('Arial', 24)
        depth_text = depth_font.render(f'AI Depth: {self.ai_depth}', True, (200, 200, 200))
        depth_rect = depth_text.get_rect(center=(self.SCREEN_WIDTH // 2, 200))
        self.screen.blit(depth_text, depth_rect)
        
        # Menu options
        menu_font = pg.font.SysFont('Arial', 36)
        
        # Black button
        black_text = menu_font.render('Play as Black', True, (255, 255, 255))
        black_rect = pg.Rect(400, 300, 400, 70)
        
        # White button
        white_text = menu_font.render('Play as White', True, (255, 255, 255))
        white_rect = pg.Rect(400, 400, 400, 70)
        
        # Hover effect
        mx, my = pg.mouse.get_pos()
        
        # Draw buttons
        if black_rect.collidepoint(mx, my):
            pg.draw.rect(self.screen, (50, 50, 50), black_rect)
        else:
            pg.draw.rect(self.screen, (30, 30, 30), black_rect)
        pg.draw.rect(self.screen, (255, 255, 255), black_rect, 3)
        black_text_rect = black_text.get_rect(center=black_rect.center)
        self.screen.blit(black_text, black_text_rect)
        
        if white_rect.collidepoint(mx, my):
            pg.draw.rect(self.screen, (200, 200, 200), white_rect)
        else:
            pg.draw.rect(self.screen, (150, 150, 150), white_rect)
        pg.draw.rect(self.screen, (0, 0, 0), white_rect, 3)
        white_text_rect = white_text.get_rect(center=white_rect.center)
        self.screen.blit(white_text, white_text_rect)
        
        # Handle clicks
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if black_rect.collidepoint(mx, my):
                    self.player_role = self.board.BLACK
                    self.ai_controller = AIController(self.ai_depth)
                    self.in_menu = False
                    self.startTime = pg.time.get_ticks()  # Reset timer when game starts
                    return True
                elif white_rect.collidepoint(mx, my):
                    self.player_role = self.board.WHITE
                    self.ai_controller = AIController(self.ai_depth)
                    self.in_menu = False
                    self.startTime = pg.time.get_ticks()  # Reset timer when game starts
                    return True
        
        return False

    
    
    def start(self) -> None:        
        while self.running:
            # Handle menu
            if self.in_menu:
                if self.menu_state == "main":
                    self.chooseMatchType()
                elif self.menu_state == "depth_selection":
                    self.chooseDepth()
                elif self.menu_state == "role_selection":
                    self.chooseRole()
                pg.display.flip()
                continue
            
            # Handle game
            for event in pg.event.get():
                if event.type == QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.handleMouseClick()
            
            # Handle AI move if in human vs computer mode
            self.handleAIMove()
            
            self.screen.fill((50, 50, 50))      # background color
            self.drawBoard()
            self.redrawBoard()
            self.currentTurn()
            self.hover()
            self.timeLapse()
            self.lastMove()
            self.showAIDepth()
            pg.display.flip()