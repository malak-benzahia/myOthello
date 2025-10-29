import numpy as np
from Logic.Board import Board

class OthelloAI:
    """AI player using Minimax algorithm for Othello"""
    
    def __init__(self, depth=2):
       
        self.depth = depth
        self.nodes_evaluated = 0
    
    def evaluate_board(self, board: Board, player: int) -> float:
        
        opponent = -player
        
        # 1. Disc count difference (basic score)
        black_count = board.blackDiscCount()
        white_count = board.whiteDiscCount()
        disc_diff = (black_count - white_count) if player == Board.BLACK else (white_count - black_count)
        
        # 2. Mobility (number of possible moves)
        player_moves = len(board.findAllPossibleMoves(player))
        opponent_moves = len(board.findAllPossibleMoves(opponent))
        mobility = player_moves - opponent_moves
        
        # 3. Corner control (corners are crucial in Othello)
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        corner_score = 0
        for r, c in corners:
            if board.board[r, c] == player:
                corner_score += 25
            elif board.board[r, c] == opponent:
                corner_score -= 25
        
        # 4. Edge control
        edge_score = 0
        edges = []
        for i in range(8):
            edges.extend([(0, i), (7, i), (i, 0), (i, 7)])
        edges = list(set(edges))  # Remove duplicates
        
        for r, c in edges:
            if board.board[r, c] == player:
                edge_score += 5
            elif board.board[r, c] == opponent:
                edge_score -= 5
        
        # 5. Stability - penalize positions next to corners (X-squares and C-squares)
        stability_penalty = 0
        dangerous_positions = [
            (0, 1), (1, 0), (1, 1),  # Near top-left corner
            (0, 6), (1, 6), (1, 7),  # Near top-right corner
            (6, 0), (6, 1), (7, 1),  # Near bottom-left corner
            (6, 6), (6, 7), (7, 6)   # Near bottom-right corner
        ]
        
        for r, c in dangerous_positions:
            if board.board[r, c] == player:
                stability_penalty -= 10
            elif board.board[r, c] == opponent:
                stability_penalty += 10
        
        # Weighted combination of factors
        total_score = (
            disc_diff * 10 +           # Disc count
            mobility * 15 +             # Mobility is important
            corner_score +              # Corners are crucial
            edge_score +                # Edges are valuable
            stability_penalty           # Avoid dangerous positions
        )
        
        return total_score
    
    def minimax(self, board: Board, depth: int, maximizing_player: bool, 
                player: int) -> tuple[float, tuple]:
        
        self.nodes_evaluated += 1
        
        # Terminal conditions
        if depth == 0 or board.isGameOver():
            return self.evaluate_board(board, player if maximizing_player else -player), None
        
        possible_moves = list(board.findAllPossibleMoves(player))
        
        # No moves available - pass turn to opponent
        if not possible_moves:
            return self.minimax(board, depth - 1, not maximizing_player, -player)
        
        best_move = None
        
        if maximizing_player:
            max_eval = float('-inf')
            
            for move in possible_moves:
                # Create a copy of the board and simulate the move
                board_copy = self.copy_board(board)
                row, col = move
                board_copy.board[row, col] = player
                board_copy.setDiscs(row, col, player)
                
                # Recursive call
                eval_score, _ = self.minimax(board_copy, depth - 1, False, -player)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
            
            return max_eval, best_move
        
        else:  # Minimizing player
            min_eval = float('inf')
            
            for move in possible_moves:
                # Create a copy of the board and simulate the move
                board_copy = self.copy_board(board)
                row, col = move
                board_copy.board[row, col] = player
                board_copy.setDiscs(row, col, player)
                
                # Recursive call
                eval_score, _ = self.minimax(board_copy, depth - 1, True, -player)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
            
            return min_eval, best_move
    
    def copy_board(self, board: Board) -> Board:
        """Create a deep copy of the board"""
        new_board = Board()
        new_board.board = np.copy(board.board)
        new_board.black_disc_count = board.black_disc_count
        new_board.white_disc_count = board.white_disc_count
        return new_board
    
    def get_best_move(self, board: Board, player: int) -> tuple:
        
        self.nodes_evaluated = 0
        score, best_move = self.minimax(board, self.depth, True, player)
        print(f"AI evaluated {self.nodes_evaluated} nodes at depth {self.depth}")
        print(f"Best move: {best_move} with score: {score}")
        return best_move


class AIController:
    
    def __init__(self, depth):
        
        self.ai = MiniMax(depth)
        self.thinking = False
        self.move_ready = False
        self.next_move = None
    
    def compute_move(self, board: Board, player: int):
        
        self.thinking = True
        self.next_move = self.ai.minimaxDecision(board, player)
        self.move_ready = True
        self.thinking = False
    
    def has_move_ready(self) -> bool:
        return self.move_ready
    
    def get_move(self) -> tuple:
        move = self.next_move
        self.move_ready = False
        self.next_move = None
        return move
    
    def reset(self):
        self.thinking = False
        self.move_ready = False
        self.next_move = None



class MiniMax:
    def __init__(self, depth):
        self.depth = depth

    def heuristic(self, board: Board, player: int) -> float:
        opponent = -player
        
        # 1. Disc count difference (basic score)
        black_count = board.blackDiscCount()
        white_count = board.whiteDiscCount()
        disc_diff = (black_count - white_count) if player == Board.BLACK else (white_count - black_count)
        
        # 2. Mobility (number of possible moves)
        player_moves = len(board.findAllPossibleMoves(player))
        opponent_moves = len(board.findAllPossibleMoves(opponent))
        mobility = player_moves - opponent_moves
        
        # 3. Corner control (corners are crucial in Othello)
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        corner_score = 0
        for r, c in corners:
            if board.board[r, c] == player:
                corner_score += 25
            elif board.board[r, c] == opponent:
                corner_score -= 25
        
        # 4. Edge control
        edge_score = 0
        edges = []
        for i in range(8):
            edges.extend([(0, i), (7, i), (i, 0), (i, 7)])
        edges = list(set(edges))  # Remove duplicates
        
        for r, c in edges:
            if board.board[r, c] == player:
                edge_score += 5
            elif board.board[r, c] == opponent:
                edge_score -= 5
        
        # 5. Stability - penalize positions next to corners (X-squares and C-squares)
        stability_penalty = 0
        dangerous_positions = [
            (0, 1), (1, 0), (1, 1),  # Near top-left corner
            (0, 6), (1, 6), (1, 7),  # Near top-right corner
            (6, 0), (6, 1), (7, 1),  # Near bottom-left corner
            (6, 6), (6, 7), (7, 6)   # Near bottom-right corner
        ]
        
        for r, c in dangerous_positions:
            if board.board[r, c] == player:
                stability_penalty -= 10
            elif board.board[r, c] == opponent:
                stability_penalty += 10
        
        # Weighted combination of factors
        total_score = (
            disc_diff * 10 +           # Disc count
            mobility * 15 +             # Mobility is important
            corner_score +              # Corners are crucial
            edge_score +                # Edges are valuable
            stability_penalty           # Avoid dangerous positions
        )
        
        return total_score
        
    
    def copy_board(self, board: Board) -> Board:

        new_board = Board()
        new_board.board = np.copy(board.board)
        new_board.black_disc_count = board.black_disc_count
        new_board.white_disc_count = board.white_disc_count
        return new_board
    
    def minimaxDecision (self, board: Board, turn: int) -> tuple:
        moves = board.findAllPossibleMoves(turn)
        
        if(turn == board.BLACK):
            opp = board.WHITE
        else:
            opp = board.BLACK

        if (not moves):
            return 

        else:
            bestMoveVal = float('-inf')
            for move in moves: 
                temp = self.copy_board(board)
                row, col = move
                temp.board[row, col] = turn
                temp.setDiscs(row, col, turn)

                val = self.minimaxValue(temp, turn, opp, self.depth, float('-inf'), float('inf'))

                if (val > bestMoveVal):
                    bestMoveVal = val
                    bestMove = move

            return bestMove

    def minimaxValue(self, board:Board, originalTurn:int, currentTurn:int, depth:int, alpha:int, beta:int):
        if (depth == 0 or board.isGameOver()):
            return self.heuristic(board, originalTurn)

        if(currentTurn == board.BLACK):
            opp = board.WHITE
        else:
            opp = board.BLACK


        moves = board.findAllPossibleMoves(currentTurn)

        if(not moves):
            return self.minimaxValue(board, originalTurn, opp, depth -1, alpha, beta)
        
        if(originalTurn == currentTurn):
            bestMoveVal = float('-inf')
            
            for move in moves:
                temp = self.copy_board(board)
                row, col = move
                temp.board[row, col] = currentTurn
                temp.setDiscs(row, col, currentTurn)
                
                val = self.minimaxValue(temp, originalTurn, opp, depth -1, alpha, beta)

                bestMoveVal = max(bestMoveVal, val)
                alpha = max(alpha, bestMoveVal)
                if beta <= alpha:
                    break
            return bestMoveVal
        else:
            bestMoveVal = float('inf')
            
            for move in moves:
                temp = self.copy_board(board)
                row, col = move
                temp.board[row, col] = currentTurn
                temp.setDiscs(row, col, currentTurn)
                
                val = self.minimaxValue(temp, originalTurn, opp, depth -1, alpha, beta)

                bestMoveVal = min(bestMoveVal, val)
                beta = min(alpha, bestMoveVal)
                if beta <= alpha:
                    break
            return bestMoveVal
    
        

