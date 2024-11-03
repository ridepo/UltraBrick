#!/usr/bin/env python3
# Copyright (C) <2024>  <Riccardo De Ponti>
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

import time
import chess
import PeSTO


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
        if self.board.is_stalemate():  # TODO or self.board.can_claim_draw():
            return ["cp", 0]
        if self.board.is_checkmate():
            if self.board.turn is self.player:
                return ["mate", -1]
            else:
                return ["mate", 1]

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

        return ["cp", int(value)]

    @staticmethod
    def is_better_eval(eval_1, eval_2):  # Returns True is the first eval is better, False otherwise.

        """ Special case 1: if both evaluations are expressed in centipawns, return True if the first one is higher,
        false otherwise.
        """
        if eval_1[0] == "cp" == eval_2[0]:
            if eval_1[1] > eval_2[1]:
                return True
            else:
                return False

        """ Special case 2: if the evaluations are identical, return False.
        """
        if eval_1 == eval_2:
            return False

        e_list = [eval_1, eval_2]
        positive_infinites_list = []
        positive_mates_list = []
        cp_list = []
        negative_mates_list = []
        negative_infinites_list = []

        """ There are 5 kinds of evaluations, from best (for the maximising engine) to worst: 
        1. Positive infinities (used only as worst case while minimising). 
        2. Positive mates (expressed in moves, not plies), which mean that the engine is winning. Lower scores are 
        better (mating in 1 is better than mating in 2). 
        3. Centipawns. Higher is better (the engine has more pieces or they are in a better position). 
        4. Negative mates (expressed in moves, not in plies), which mean that the engine is losing. Lower scores are 
        better (getting mated in -2 moves is better than getting mated in -1). 
        5. Negative infinities (used only as worst case while maximising).
        """
        for e in e_list:
            if e[0] == "inf" and e[1] > 0:
                positive_infinites_list.append(e)
            if e[0] == "mate" and e[1] > 0:
                positive_mates_list.append(e)
            if e[0] == "cp":
                cp_list.append(e)
            if e[0] == "mate" and e[1] < 0:
                negative_mates_list.append(e)
            if e[0] == "inf" and e[1] < 0:
                negative_infinites_list.append(e)

        # There is no need to sort positive infinities because we only use ["inf", 1].
        positive_mates_list.sort(reverse=False, key=lambda x: x[1])
        cp_list.sort(reverse=True, key=lambda x: x[1])
        negative_mates_list.sort(reverse=False, key=lambda x: x[1])
        # There is no need to sort negative infinities because we only use ["inf", -1].

        e_list = positive_infinites_list + positive_mates_list + cp_list + negative_mates_list + negative_infinites_list
        if eval_1 == e_list[0]:
            return True
        else:
            return False

    def max_eval(self, eval_1, eval_2):
        if self.is_better_eval(eval_1, eval_2):
            return eval_1
        else:
            return eval_2

    def min_eval(self, eval_1, eval_2):
        if self.is_better_eval(eval_1, eval_2):
            return eval_2
        else:
            return eval_1

    def is_worse_or_equal_eval(self, eval_1, eval_2):
        return not self.is_better_eval(eval_1, eval_2)

    def print_info(self, depth, best_eval, moves_list):
        print(f"info depth {depth} nodes {self.nodes} "
              f"nps {int((self.nodes * 1000000000) / (time.perf_counter_ns() - self.start_time))} "
              f"score {best_eval[0]} {best_eval[1]} pv {moves_list[0][0]}",
              flush=True)

    """ I use time.perf_counter_ns() instead of time.time_ns() because in some environments time.time_ns() does not 
    update reliably, and the program crashes with "divide by zero" while calculating 
    ((self.nodes * 1000000000) / (time.perf_counter_ns() - self.start_time)). 
    """

    def minmax(self, maximizing, depth, alpha, beta):
        if depth == 1 or self.board.legal_moves.count() == 0 or (
                self.stop_time != 0 and time.perf_counter_ns() >= self.stop_time):
            self.nodes += 1
            return self.position_eval(self)
        elif maximizing is True:
            max_eval = ["inf", -1]
            for eval_move in self.board.legal_moves:
                self.board.push(eval_move)
                temp_eval = self.minmax(False, depth - 1, alpha, beta)
                self.board.pop()
                if temp_eval == ["mate", 1]:
                    self.nodes += 1
                    return temp_eval
                max_eval = self.max_eval(max_eval, temp_eval)
                alpha = self.max_eval(alpha, max_eval)
                if self.is_worse_or_equal_eval(beta, alpha):
                    break
            if max_eval[0] == "mate" and max_eval[1] < 0:
                max_eval[1] -= 1
            self.nodes += 1
            return max_eval
        else:
            min_eval = ["inf", 1]
            for eval_move in self.board.legal_moves:
                self.board.push(eval_move)
                temp_eval = self.minmax(True, depth - 1, alpha, beta)
                self.board.pop()
                if temp_eval == ["mate", -1]:
                    self.nodes += 1
                    return temp_eval
                min_eval = self.min_eval(min_eval, temp_eval)
                beta = self.min_eval(beta, min_eval)
                if self.is_worse_or_equal_eval(beta, alpha):
                    break
            if min_eval[0] == "mate" and min_eval[1] > 0:
                min_eval[1] += 1
            self.nodes += 1
            return min_eval

    @staticmethod
    def sort_moves(m_list):
        cp_list = []
        positive_mates_list = []
        negative_mates_list = []

        for m in m_list:
            if m[1][0] == "cp":
                cp_list.append(m)
            if m[1][0] == "mate" and m[1][1] > 0:
                positive_mates_list.append(m)
            if m[1][0] == "mate" and m[1][1] < 0:
                negative_mates_list.append(m)

        positive_mates_list.sort(reverse=False, key=lambda x: x[1][1])
        cp_list.sort(reverse=True, key=lambda x: x[1][1])
        negative_mates_list.sort(reverse=False, key=lambda x: x[1][1])

        return positive_mates_list + cp_list + negative_mates_list

    def minmax_root(self, move_time, white_time, black_time):
        self.start_time = time.perf_counter_ns()
        self.nodes = 0
        best_eval = ["inf", -1]
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
            moves_list.append([append_move, ["cp", 0]])

        # Set stop time for search
        if move_time != 0:
            self.stop_time = self.start_time + move_time * 980000
        elif self.board.turn == chess.WHITE:
            if white_time == 0:
                self.stop_time = 0
            else:
                self.stop_time = self.start_time + white_time * 50000
        else:
            if black_time == 0:
                self.stop_time = 0
            else:
                self.stop_time = self.start_time + black_time * 50000

        # Iterate search at increasing depth until time runs out.
        while self.stop_time == 0 or time.perf_counter_ns() < self.stop_time:
            alpha = ["inf", -1]
            beta = ["inf", 1]
            for i in range(len(moves_list)):
                if self.stop_time == 0 or time.perf_counter_ns() < self.stop_time:
                    self.board.push(moves_list[i][0])
                    print(f"info depth {depth} currmove {moves_list[i][0]} currmovenumber {i + 1}")
                    moves_list[i][1] = self.minmax(False, depth, alpha, beta)
                    self.board.pop()
                    if moves_list[i][1] == ["mate", 1]:
                        self.nodes += 1
                        self.print_info(depth, best_eval, moves_list)
                        print(f"info score {moves_list[i][1][0]} {moves_list[i][1][1]} depth {depth}", flush=True)
                        return moves_list[i][0]
                alpha = self.max_eval(alpha, moves_list[i][1])
                if self.is_worse_or_equal_eval(beta, alpha):
                    break
            """ The engine only sorts the moves list when a depth level is completed. The only exception is if 
            it didn't finish the first depth level: it means it is very low on time and it uses what it has.
            """
            if self.stop_time == 0 or time.perf_counter_ns() < self.stop_time or depth == 1:
                moves_list = self.sort_moves(moves_list)
                best_eval = moves_list[0][1]
                self.print_info(depth, best_eval, moves_list)
                depth += 1
        self.nodes += 1
        self.print_info(depth - 1, best_eval, moves_list)
        print(f"info score {best_eval[0]} {best_eval[1]} depth {depth - 1}", flush=True)
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
