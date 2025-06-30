import copy
import math
import random
import tkinter as tk
from tkinter import CENTER
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from tkinter import font as tkfont

BOARD_SIZE = 15
WIN_CONDITION = 5
MAX_DEPTH = 2
EMPTY = '.'
BLACK = 'B'
WHITE = 'W'

class GomokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gomoku Game")
        self.board = create_board()
        self.cell_size = 40
        self.canvas = tk.Canvas(root, width=self.cell_size * BOARD_SIZE, height=self.cell_size * BOARD_SIZE, bg='burlywood')
        self.canvas.pack()
        self.game_mode = None
        self.human_player = None
        self.after_id = None
        self.current_player = BLACK
        self.game_over = False
        self.last_move = None
        self.winning_moves = None
        self.move_history = []
        self.load_stone_images()
        self.custom_font = tkfont.Font(family='Helvetica', size=12, weight='bold')
        self.title_font = tkfont.Font(family='Helvetica', size=14, weight='bold')
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(fill='x', padx=10, pady=5)
        self.status_label = tk.Label(self.control_frame, text="", font=self.custom_font, fg='black')
        self.status_label.pack(side='left', expand=True)
        self.draw_board()
        self.setup_game()

    def load_stone_images(self):
        self.stone_images = {
            BLACK: self.create_stone_image('black'),
            WHITE: self.create_stone_image('white')
        }

    def create_stone_image(self, color):
        size = self.cell_size
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        fill = (0, 0, 0) if color == 'black' else (255, 255, 255)
        outline = (50, 50, 50) if color == 'black' else (200, 200, 200)
        draw.ellipse((0, 0, size - 1, size - 1), fill=fill, outline=outline)
        return ImageTk.PhotoImage(img)

    def clear_board(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.board = create_board()
        self.game_over = False
        self.last_move = None
        self.winning_moves = None
        self.draw_board()
        self.update_status()
        if self.game_mode == 'human_vs_ai':
            self.canvas.bind("<Button-1>", self.on_cell_click)
            if self.current_player != self.human_player:
                self.root.after(500, self.ai_move)

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(BOARD_SIZE):
            self.canvas.create_line(i * self.cell_size, 0, i * self.cell_size, self.cell_size * BOARD_SIZE, width=2)
            self.canvas.create_line(0, i * self.cell_size, self.cell_size * BOARD_SIZE, i * self.cell_size, width=2)
        if self.winning_moves:
            for row, col in self.winning_moves:
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill='light blue', outline='')
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = col * self.cell_size + self.cell_size // 2
                y = row * self.cell_size + self.cell_size // 2
                if self.board[row][col] == BLACK:
                    self.canvas.create_image(x, y, image=self.stone_images[BLACK], anchor=CENTER)
                elif self.board[row][col] == WHITE:
                    self.canvas.create_image(x, y, image=self.stone_images[WHITE], anchor=CENTER)
        if self.last_move:
            row, col = self.last_move
            x1 = col * self.cell_size
            y1 = row * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline='blue', width=3)

    def setup_game(self):
        self.current_player = BLACK
        self.game_mode = None
        self.human_player = None
        self.ai_player = None
        self.game_over = False
        self.last_move = None
        self.winning_moves = None

        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.root.lift()
        while True:
            mode = simpledialog.askstring("Game Mode", "Choose game mode:\n1. Human vs AI\n2. AI vs AI\nEnter 1 or 2:")
            if mode in ('1', '2'):
                break
            if mode is None:
                self.root.quit()
                return
        self.clear_board()

        if mode == '1':
            self.game_mode = 'human_vs_ai'
            while True:
                human_player = simpledialog.askstring("Player Selection","Choose color (Black starts first):\nB or W").strip().upper()
                if human_player in (BLACK, WHITE):
                    break
                if human_player is None:
                    self.root.quit()
                    return
            self.human_player = human_player
            self.ai_player = WHITE if human_player == BLACK else BLACK
            self.current_player = BLACK
            if self.current_player != self.human_player:
                self.root.after(500, self.ai_move)
            self.canvas.bind("<Button-1>", self.on_cell_click)
        else:
            self.game_mode = 'ai_vs_ai'
            self.current_player = BLACK
            self.root.after(500, self.ai_move)
        self.update_status()

    def update_status(self):
        if self.game_mode == 'human_vs_ai':
            player_info = f"Human ({'Black' if self.human_player == BLACK else 'White'}) vs AI - Minimax ({'White' if self.human_player == BLACK else 'Black'})"
        else:
            player_info = "AI (Minimax - Black) vs AI (AlphaBeta - White)"

        turn_info = f"Current Turn: {'Black' if self.current_player == BLACK else 'White'}"
        self.status_label.config(text=f"{player_info}\n{turn_info}")
        if hasattr(self, 'turn_indicator'):
            self.turn_indicator.destroy()
        self.turn_indicator = tk.Frame(self.root, height=20, bg='black' if self.current_player == BLACK else 'white')
        self.turn_indicator.pack(fill='x', padx=10, pady=5)
        tk.Label(self.turn_indicator,
                 text=f"{'BLACK' if self.current_player == BLACK else 'WHITE'}'s TURN",
                 bg='black' if self.current_player == BLACK else 'white',
                 fg='white' if self.current_player == BLACK else 'black',
                 font=('Arial', 12, 'bold')).pack()
        self.draw_board()


    def ai_move(self):
        if self.game_over:
            return
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        use_alphabeta = (self.game_mode == 'ai_vs_ai' and self.current_player == WHITE)
        if use_alphabeta:
            _, move = alphabeta(self.board, MAX_DEPTH, -math.inf, math.inf, self.current_player == BLACK)
        else:
            _, move = minimax(self.board, MAX_DEPTH, self.current_player == BLACK)
        if move:
            row, col = move
            self.move_history.append((row, col, self.current_player))
            self.last_move = (row, col)
            self.board[row][col] = self.current_player
            self.draw_board()
            if check_win(self.board, self.current_player):
                self.winning_moves = self.get_winning_line(self.board, self.current_player)
                self.game_over = True
                self.draw_board()
                self.update_status()
                answer = messagebox.askyesno(
                    "Game Over",
                    f"{self.get_player_name(self.current_player)} wins!\nPlay again?"
                )
                if answer:
                    self.setup_game()
                    return
                else:
                    self.root.quit()
                return
            elif is_full(self.board):
                self.game_over = True
                self.update_status()
                answer = messagebox.askyesno(
                    "Game Over","The game is a draw!\nPlay again?"
                )
                if answer:
                    self.setup_game()
                else:
                    self.root.quit()
                return

            self.current_player = WHITE if self.current_player == BLACK else BLACK
            self.update_status()
            if self.game_mode == 'ai_vs_ai':
                self.after_id = self.root.after(100, self.ai_move)

    def on_cell_click(self, event):
        if self.game_over or self.game_mode != 'human_vs_ai' or self.current_player != self.human_player:
            return
        col = min(max(0, event.x // self.cell_size), BOARD_SIZE - 1)
        row = min(max(0, event.y // self.cell_size), BOARD_SIZE - 1)
        stone_x = col * self.cell_size + self.cell_size // 2
        stone_y = row * self.cell_size + self.cell_size // 2
        if (abs(event.x - stone_x) < self.cell_size // 3 and abs(event.y - stone_y) < self.cell_size // 3 and self.board[row][col] == EMPTY):
            self.move_history.append((row, col, self.current_player))
            self.last_move = (row, col)
            self.board[row][col] = self.human_player
            self.draw_board()
            if check_win(self.board, self.human_player):
                self.winning_moves = self.get_winning_line(self.board, self.human_player)
                self.game_over = True
                self.draw_board()
                self.update_status()
                answer = messagebox.askyesno(
                    "Game Over",
                    f"{self.get_player_name(self.current_player)} wins!\nPlay again?"
                )
                if answer:
                    self.setup_game()
                    return
                else:
                    self.root.quit()
                return
            elif is_full(self.board):
                self.game_over = True
                self.update_status()
                answer = messagebox.askyesno(
                    "Game Over", "The game is a draw!\nPlay again?"
                )
                if answer:
                    self.setup_game()
                else:
                    self.root.quit()
                return
            self.current_player = WHITE if self.current_player == BLACK else BLACK
            self.update_status()
            if not self.game_over and self.current_player == self.ai_player:
                self.root.after(500, self.ai_move)

    def get_player_name(self, player):
        return "Black" if player == BLACK else "White"

    def get_winning_line(self, board, player):
        directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                for dr, dc in directions:
                    winning_moves = []
                    for i in range(WIN_CONDITION):
                        nr, nc = r + dr * i, c + dc * i
                        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == player:
                            winning_moves.append((nr, nc))
                        else:
                            break
                    if len(winning_moves) == WIN_CONDITION:
                        self.winning_moves = winning_moves
                        return winning_moves
        self.winning_moves = None
        return None

    def play_ai_vs_ai(self):
        self.ai_move()


def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def is_full(board):
    return all(cell != EMPTY for row in board for cell in row)

def check_win(board, player):
    directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            for dr, dc in directions:
                count = 0
                for i in range(WIN_CONDITION):
                    nr, nc = r + dr * i, c + dc * i
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == player:
                        count += 1
                    else:
                        break
                if count == WIN_CONDITION:
                    return True
    return False

def get_valid_moves(board):
    directions = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]
    near_moves = set()
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] != EMPTY:
                for dr, dc in directions:
                    for dist in range(1, 3):
                        r, c = row + dr*dist, col + dc*dist
                        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == EMPTY:
                            near_moves.add((r, c))
    return list(near_moves) if near_moves else [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == EMPTY]

def evaluate(board):
    if check_win(board, BLACK):
        return 100000
    if check_win(board, WHITE):
        return -100000
    black_score = score_position(board, BLACK)
    white_score = score_position(board, WHITE)
    return black_score - white_score

def score_position(board, player):
    score = 0
    opponent = WHITE if player == BLACK else BLACK
    directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            for dr, dc in directions:
                own_count = 0
                opp_count = 0
                for i in range(WIN_CONDITION):
                    nr, nc = r + dr * i, c + dc * i
                    if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                        if board[nr][nc] == player:
                            own_count += 1
                        elif board[nr][nc] == opponent:
                            opp_count += 1
                if opp_count == 0:
                    score += 10 ** own_count
                elif own_count == 0:
                    score -= 10 ** opp_count
    return score

def minimax(board, depth, maximizing_player):
    if depth == 0 or is_full(board) or check_win(board, BLACK) or check_win(board, WHITE):
        return evaluate(board), None
    best_move = None
    moves = get_valid_moves(board)
    random.shuffle(moves)
    if maximizing_player:
        max_eval = -math.inf
        for move in moves:
            new_board = copy.deepcopy(board)
            new_board[move[0]][move[1]] = BLACK
            eval, _ = minimax(new_board, depth - 1, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in moves:
            new_board = copy.deepcopy(board)
            new_board[move[0]][move[1]] = WHITE
            eval, _ = minimax(new_board, depth - 1, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
        return min_eval, best_move

def alphabeta(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or is_full(board) or check_win(board, BLACK) or check_win(board, WHITE):
        return evaluate(board), None
    best_move = None
    moves = get_valid_moves(board)
    random.shuffle(moves)
    if maximizing_player:
        max_eval = -math.inf
        for move in moves:
            new_board = copy.deepcopy(board)
            new_board[move[0]][move[1]] = BLACK
            eval, _ = alphabeta(new_board, depth - 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        for move in moves:
            new_board = copy.deepcopy(board)
            new_board[move[0]][move[1]] = WHITE
            eval, _ = alphabeta(new_board, depth - 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

if __name__ == "__main__":
    root = tk.Tk()
    game = GomokuGUI(root)
    root.mainloop()
