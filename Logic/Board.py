import numpy as np

class Board:
    WHITE = -1
    BLACK = 1
    EMPTY = 0

    moves = [( 0,-1),    #top
             ( 0, 1),    #bottom
             ( 1, 0),    #right
             (-1, 0),    #left
             ( 1,-1),    #top right
             ( 1, 1),    #bottom right
             (-1, 1),    #bottom left
             (-1,-1),    #top left
    ]
    
    def __init__(self):
        
        self.board = np.array([0]*8, dtype=np.int64)
        self.board = self.board[np.newaxis, :]
        for _ in range(3):
            self.board = np.concatenate((self.board, self.board), axis = 0)
        
        self.board[3, 3] = self.board[4,4] = Board.WHITE
        self.board[3, 4] = self.board[4,3] = Board.BLACK

        self.black_disc_count = 2
        self.white_disc_count = 2

    def checkBounds(self, x: int, y: int) -> bool:
        return (x >= 0 and y >= 0) and (x < 8 and y < 8)
    
    def findPossibleMoves(self, r: int, c: int):
        moves = []

        player = self.board[r, c]
        opp = player * -1

        if player == 0:  # empty
            return moves
        
        for dir in self.moves:
            rowDir, colDir = dir
            row = r + rowDir
            col = c + colDir

            if self.checkBounds(row, col) and self.board[row, col] == opp:
                while(self.checkBounds(row, col) and self.board[row, col] == opp):
                    row += rowDir
                    col += colDir

                if (self.checkBounds(row, col) and self.board[row, col] == Board.EMPTY):
                    moves.append((row, col))

                else:
                    continue
            else: 
                continue
        return moves

    def score(self, turn: int):
        if turn == self.BLACK:
            return self.black_disc_count
        else:
            return self.white_disc_count
        
    
    def findAllPossibleMoves(self, player: int):
        allMoves = set()
        for r in range(self.board.shape[0]):      # iterate over row indices
            for c in range(self.board.shape[1]):  # iterate over column indices
                if self.board[r, c] == player:
                    moves = self.findPossibleMoves(r, c)
                    allMoves.update(moves)
        return allMoves
    
    def flipDiscs(self, start: tuple[int, int], end: tuple[int, int], player: int, dir: tuple[int, int]):
        row, col = start
        rowDir, colDir = dir

        row += rowDir
        col += colDir

        while (row, col) != end:
            self.board[row, col] = player
            if player == self.BLACK:
                self.black_disc_count += 1
            elif player == self.WHITE:
                self.white_disc_count += 1

            row += rowDir
            col += colDir

    def setDiscs(self, row: int, col: int, player: int):
        self.board[row, col] = player
        opp = player * -1

        for dir in Board.moves:
            rowDir, colDir = dir
            r = row + rowDir
            c = col + colDir

            if self.checkBounds(r, c) is False or self.board[r, c] != opp:
                continue

            r += rowDir 
            c += colDir
            while(self.checkBounds(r, c) is True and self.board[r, c] == opp):
                r += rowDir
                c += colDir
            if(self.checkBounds(r, c) is True and self.board[r, c] == player):
                self.flipDiscs((row, col), (r, c), player, dir)

        
    def isGameOver(self) -> bool:
        if not self.findAllPossibleMoves(self.BLACK) and not self.findAllPossibleMoves(self.WHITE):
            return True
        return False
    
    def blackDiscCount(self):
        count = 0
        for row in self.board:
            for cell in row:
                if cell == self.BLACK:
                    count += 1
        return count
    
    def whiteDiscCount(self):
        count = 0
        for row in self.board:
            for cell in row:
                if cell == self.WHITE:
                    count += 1
        return count
    
    def getWinner(self):
        if self.white_disc_count > self.black_disc_count:
            return self.WHITE
        elif self.black_disc_count > self.white_disc_count:
            return self.BLACK
        else :
            return 0

