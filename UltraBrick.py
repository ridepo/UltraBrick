#!/usr/bin/env python3
# Copyright (C) <2024-2025>  <Riccardo De Ponti>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import copy
import time
import chess
import PeSTO


def format_eval(evaluation):
    if evaluation[0] == -2:
        return "inf -1"
    elif evaluation[0] == -1:
        return "mate " + str(-evaluation[1])
    elif evaluation[0] == 0:
        return "cp " + str(evaluation[1])
    elif evaluation[0] == 1:
        return "mate " + str(-evaluation[1])
    elif evaluation[0] == 2:
        return "inf 1"
    else:
        print(f"impossible evaluation {evaluation}")


def is_better_eval(eval_1, eval_2):  # Returns True is the first eval is better, False otherwise.
    if eval_1[0] > eval_2[0]:
        return True
    elif eval_1[0] == eval_2[0] and eval_1[1] > eval_2[1]:
        return True
    else:
        return False

def max_eval(eval_1, eval_2):
    if is_better_eval(eval_1, eval_2):
        return eval_1
    else:
        return eval_2

def min_eval(eval_1, eval_2):
    if is_better_eval(eval_1, eval_2):
        return eval_2
    else:
        return eval_1

def is_worse_or_equal_eval(eval_1, eval_2):
    return not is_better_eval(eval_1, eval_2)

def sort_moves(m_list):
    return sorted(m_list, reverse=True, key=lambda x: (x[1][0], x[1][1]))

class Engine:
    def __init__(self):
        self.name = "UltraBrick"
        self.author = "Riccardo De Ponti"
        self.board = chess.Board()
        self.player = chess.WHITE
        self.nodes = 0
        self.start_time = 0
        self.stop_time = 0
        self.middlegame_tables, self.endgame_tables = PeSTO.init_tables()

    def set_fen(self, fen_string):
        self.board.set_fen(fen_string)

    @staticmethod
    def position_eval(self):
        if self.board.is_stalemate():
            return [0, 0]
        if self.board.is_checkmate():
            if self.board.turn is self.player:
                return [-1, 1]
            else:
                return [1, -1]

        middlegame = [0, 0]
        endgame = [0, 0]
        game_phase = 0
        game_phase_values = (0, 0, 1, 1, 1, 1, 2, 2, 4, 4, 0, 0)

        for piece_type in chess.PIECE_TYPES:
            for color in chess.COLORS:
                for square in self.board.pieces(piece_type, color):
                    piece_index = (2 * (piece_type - 1) + color)
                    middlegame[color] += self.middlegame_tables[piece_index][square]
                    endgame[color] += self.endgame_tables[piece_index][square]
                    game_phase += game_phase_values[piece_index]

        middlegame_score = middlegame[chess.WHITE] - middlegame[chess.BLACK]
        endgame_score = endgame[chess.WHITE] - endgame[chess.BLACK]
        middlegame_phase = game_phase
        middlegame_phase = min(middlegame_phase, 24)
        endgame_phase = 24 - middlegame_phase
        value = (middlegame_score * middlegame_phase + endgame_score * endgame_phase) / 24

        if self.player == chess.BLACK:
            value = - value

        return [0, int(value)]

    def print_info(self, depth, best_eval, best_move):
        print(f"info depth {depth} nodes {self.nodes} "
              f"nps {int((self.nodes * 1000000000) / (time.perf_counter_ns() - self.start_time))} "
              f"score {format_eval(best_eval)} pv {best_move}",
              flush=True)

    """ I use time.perf_counter_ns() instead of time.time_ns() because in some environments time.time_ns() does not 
    update reliably, and the program crashes with "divide by zero" while calculating 
    ((self.nodes * 1000000000) / (time.perf_counter_ns() - self.start_time)). 
    """

    def minmax(self, maximizing, depth, alpha, beta):
        if depth == 0 or self.board.legal_moves.count() == 0:
            self.nodes += 1
            return self.position_eval(self)
        elif maximizing is True:
            best_eval = [-2, 0]
            for eval_move in self.board.legal_moves:
                self.board.push(eval_move)
                temp_eval = self.minmax(False, depth - 1, alpha, beta)
                self.board.pop()
                if temp_eval == [1, -((depth+1)//2)]:  # we found the shortest mate
                    self.nodes += 1
                    return temp_eval
                best_eval = max_eval(best_eval, temp_eval)
                alpha = max_eval(alpha, best_eval)
                if is_worse_or_equal_eval(beta, alpha):
                    break
            if best_eval[0] == -1:
                best_eval[1] += 1
            self.nodes += 1
            return best_eval
        else:
            best_eval = [2, 0]
            for eval_move in self.board.legal_moves:
                self.board.push(eval_move)
                temp_eval = self.minmax(True, depth - 1, alpha, beta)
                self.board.pop()
                if temp_eval == [-1, (depth+1)//2]:  # we found the fastest mate
                    self.nodes += 1
                    return temp_eval
                best_eval = min_eval(best_eval, temp_eval)
                beta = min_eval(beta, best_eval)
                if is_worse_or_equal_eval(beta, alpha):
                    break
            if best_eval[0] == 1:
                best_eval[1] -= 1
            self.nodes += 1
            return best_eval


    def is_running(self):
        if self.stop_time == 0 or time.perf_counter_ns() < self.stop_time:
            return True
        else:
            return False

    def minmax_root(self, move_time, white_time, black_time):
        self.start_time = time.perf_counter_ns()
        self.nodes = 0
        best_eval = [-2, 0]
        depth = 1

        if self.board.legal_moves.count() == 0:
            return "(none)"

        if self.board.turn is chess.WHITE:
            self.player = chess.WHITE
        else:
            self.player = chess.BLACK

        # According to UCI definitions engine is always maximising, no matter if white or black

        # Populate a list of list with legal moves and temporary evaluations
        moves_list = []
        for append_move in self.board.legal_moves:
            moves_list.append([append_move, [0, 0]])

        # Set stop time for search
        # UCI uses milliseconds
        # We are using nanoseconds (1 ns = 1/1.000.000.000 s = 1/1.000.000 ms)
        if move_time != 0:
            self.stop_time = self.start_time + move_time * 950000
        elif self.board.turn == chess.WHITE:
            if white_time == 0:
                self.stop_time = 0
            else:
                self.stop_time = self.start_time + white_time * 45000
        else:
            if black_time == 0:
                self.stop_time = 0
            else:
                self.stop_time = self.start_time + black_time * 45000
        if len(moves_list) == 1:
            self.stop_time = min(self.stop_time, self.start_time + 2000000000)

        # Iterate search at increasing depth until time runs out.
        while self.is_running():
            alpha = [-2, 0]
            beta = [2, 0]
            # A list of moves evaluated
            evaluated_moves_list = []
            for i in range(len(moves_list)):
                if not self.is_running():
                    break
                self.board.push(moves_list[i][0])
                print(f"info depth {depth} currmove {moves_list[i][0]} currmovenumber {i + 1}")
                evaluated_moves_list.append([moves_list[i][0], self.minmax(False, depth -1, alpha, beta)])
                self.board.pop()
                if evaluated_moves_list[i][1] == [1, -((depth+1)//2)]: # we found the shortest mate
                    best_eval = evaluated_moves_list[i][1]
                    best_move = evaluated_moves_list[i][0]
                    self.nodes += 1
                    self.print_info(depth, best_eval, best_move)
                    print(f"info score {format_eval(best_eval)} depth {depth-1}", flush=True)
                    return best_move
                alpha = max_eval(alpha, evaluated_moves_list[i][1])
                if is_worse_or_equal_eval(beta, alpha):
                    break
            # print ("info we copy the list")
            moves_list = copy.deepcopy(evaluated_moves_list)

            """ We sort the moves list
            """
            # print (f"info we sort the list, list length ={len(moves_list)} ")
            moves_list = sort_moves(moves_list)
            best_eval = moves_list[0][1]
            best_move = moves_list[0][0]
            self.print_info(depth, best_eval, best_move)
            depth += 1
        self.nodes += 1
        print(f"info score {format_eval(best_eval)} depth {depth-1}", flush=True)
        return moves_list[0][0]

engine = Engine()

while True:
    command_string = input()

    command = command_string.split()
    if len(command) == 0:
        continue

    if command[0] == "uci":
        print(f"id name {engine.name}")
        print(f"id author {engine.author}")
        print("uciok")

    elif command[0] == "isready":
        print("readyok")

    elif command[0] == "ucinewgame":
        engine.board.reset()

    elif command[0] == "quit":
        quit()

    elif command[0] == "position":
        if command[1] == "fen":
            engine.set_fen(' '.join(command[2:]))
        elif command[1] == "startpos":
            engine.board.reset()
            if len(command) > 2:
                if command[2] == "moves":
                    engine.board.reset()
                    for move in command[3:]:
                        engine.board.push_uci(move)

    elif command[0] == "go":  # TODO: command parsing needs to be redone
        movetime = 0
        wtime = 0
        btime = 0
        if len(command) > 1:
            if command[1] == "movetime":
                movetime = int(command[2])
        if len(command) > 3:
            if command[1] == "wtime":
                wtime = int(command[2])
            if command[3] == "btime":
                btime = int(command[4])
        print(f"bestmove {engine.minmax_root(movetime, wtime, btime)}")
