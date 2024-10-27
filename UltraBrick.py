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


class Engine:
    def __init__(self):
        self.name = "UltraBrick"
        self.author = "Riccardo De Ponti"
        self.board = chess.Board()
        self.player = chess.WHITE
        self.nodes = 0
        self.start_time = 0
        self.stop_time = 0
        self.middlegame_tables, self.endgame_tables = self.init_tables()

    def set_fen(self, fen_string):
        self.board.set_fen(fen_string)

    @staticmethod
    def init_tables():
        middlegame_pawn_table = (
            0, 0, 0, 0, 0, 0, 0, 0,
            98, 134, 61, 95, 68, 126, 34, -11,
            -6, 7, 26, 31, 65, 56, 25, -20,
            -14, 13, 6, 21, 23, 12, 17, -23,
            -27, -2, -5, 12, 17, 6, 10, -25,
            -26, -4, -4, -10, 3, 3, 33, -12,
            -35, -1, -20, -23, -15, 24, 38, -22,
            0, 0, 0, 0, 0, 0, 0, 0,
        )

        endgame_pawn_table = (
            0, 0, 0, 0, 0, 0, 0, 0,
            178, 173, 158, 134, 147, 132, 165, 187,
            94, 100, 85, 67, 56, 53, 82, 84,
            32, 24, 13, 5, -2, 4, 17, 17,
            13, 9, -3, -7, -7, -8, 3, -1,
            4, 7, -6, 1, 0, -5, -1, -8,
            13, 8, 8, 10, 13, 0, 2, -7,
            0, 0, 0, 0, 0, 0, 0, 0,
        )

        middlegame_knight_table = (
            -167, -89, -34, -49, 61, -97, -15, -107,
            -73, -41, 72, 36, 23, 62, 7, -17,
            -47, 60, 37, 65, 84, 129, 73, 44,
            -9, 17, 19, 53, 37, 69, 18, 22,
            -13, 4, 16, 13, 28, 19, 21, -8,
            -23, -9, 12, 10, 19, 17, 25, -16,
            -29, -53, -12, -3, -1, 18, -14, -19,
            -105, -21, -58, -33, -17, -28, -19, -23,
        )

        endgame_knight_table = (
            -58, -38, -13, -28, -31, -27, -63, -99,
            -25, -8, -25, -2, -9, -25, -24, -52,
            -24, -20, 10, 9, -1, -9, -19, -41,
            -17, 3, 22, 22, 22, 11, 8, -18,
            -18, -6, 16, 25, 16, 17, 4, -18,
            -23, -3, -1, 15, 10, -3, -20, -22,
            -42, -20, -10, -5, -2, -20, -23, -44,
            -29, -51, -23, -15, -22, -18, -50, -64,
        )

        middlegame_bishop_table = (
            -29, 4, -82, -37, -25, -42, 7, -8,
            -26, 16, -18, -13, 30, 59, 18, -47,
            -16, 37, 43, 40, 35, 50, 37, -2,
            -4, 5, 19, 50, 37, 37, 7, -2,
            -6, 13, 13, 26, 34, 12, 10, 4,
            0, 15, 15, 15, 14, 27, 18, 10,
            4, 15, 16, 0, 7, 21, 33, 1,
            -33, -3, -14, -21, -13, -12, -39, -21,
        )

        endgame_bishop_table = (
            -14, -21, -11, -8, -7, -9, -17, -24,
            -8, -4, 7, -12, -3, -13, -4, -14,
            2, -8, 0, -1, -2, 6, 0, 4,
            -3, 9, 12, 9, 14, 10, 3, 2,
            -6, 3, 13, 19, 7, 10, -3, -9,
            -12, -3, 8, 10, 13, 3, -7, -15,
            -14, -18, -7, -1, 4, -9, -15, -27,
            -23, -9, -23, -5, -9, -16, -5, -17,
        )

        middlegame_rook_table = (
            32, 42, 32, 51, 63, 9, 31, 43,
            27, 32, 58, 62, 80, 67, 26, 44,
            -5, 19, 26, 36, 17, 45, 61, 16,
            -24, -11, 7, 26, 24, 35, -8, -20,
            -36, -26, -12, -1, 9, -7, 6, -23,
            -45, -25, -16, -17, 3, 0, -5, -33,
            -44, -16, -20, -9, -1, 11, -6, -71,
            -19, -13, 1, 17, 16, 7, -37, -26,
        )

        endgame_rook_table = (
            13, 10, 18, 15, 12, 12, 8, 5,
            11, 13, 13, 11, -3, 3, 8, 3,
            7, 7, 7, 5, 4, -3, -5, -3,
            4, 3, 13, 1, 2, 1, -1, 2,
            3, 5, 8, 4, -5, -6, -8, -11,
            -4, 0, -5, -1, -7, -12, -8, -16,
            -6, -6, 0, 2, -9, -9, -11, -3,
            -9, 2, 3, -1, -5, -13, 4, -20,
        )

        middlegame_queen_table = (
            -28, 0, 29, 12, 59, 44, 43, 45,
            -24, -39, -5, 1, -16, 57, 28, 54,
            -13, -17, 7, 8, 29, 56, 47, 57,
            -27, -27, -16, -16, -1, 17, -2, 1,
            -9, -26, -9, -10, -2, -4, 3, -3,
            -14, 2, -11, -2, -5, 2, 14, 5,
            -35, -8, 11, 2, 8, 15, -3, 1,
            -1, -18, -9, 10, -15, -25, -31, -50,
        )

        endgame_queen_table = (
            -9, 22, 22, 27, 27, 19, 10, 20,
            -17, 20, 32, 41, 58, 25, 30, 0,
            -20, 6, 9, 49, 47, 35, 19, 9,
            3, 22, 24, 45, 57, 40, 57, 36,
            -18, 28, 19, 47, 31, 34, 39, 23,
            -16, -27, 15, 6, 9, 17, 10, 5,
            -22, -23, -30, -16, -16, -23, -36, -32,
            -33, -28, -22, -43, -5, -32, -20, -41,
        )

        middlegame_king_table = (
            -65, 23, 16, -15, -56, -34, 2, 13,
            29, -1, -20, -7, -8, -4, -38, -29,
            -9, 24, 2, -16, -20, 6, 22, -22,
            -17, -20, -12, -27, -30, -25, -14, -36,
            -49, -1, -27, -39, -46, -44, -33, -51,
            -14, -14, -22, -46, -44, -30, -15, -27,
            1, 7, -8, -64, -43, -16, 9, 8,
            -15, 36, 12, -54, 8, -28, 24, 14,
        )

        endgame_king_table = (
            -74, -35, -18, -18, -11, 15, 4, -17,
            -12, 17, 14, 17, 17, 38, 23, 11,
            10, 17, 23, 15, 20, 45, 44, 13,
            -8, 22, 24, 27, 26, 33, 26, 3,
            -18, -4, 21, 24, 27, 23, 9, -11,
            -19, -3, 11, 21, 23, 16, 7, -9,
            -27, -11, 4, 13, 14, 4, -5, -17,
            -53, -34, -21, -11, -28, -14, -24, -43
        )

        middlegame_values = {
            "p": 82,
            "n": 337,
            "b": 365,
            "r": 477,
            "q": 1025,
            "k": 0
        }

        endgame_values = {
            "p": 94,
            "n": 281,
            "b": 297,
            "r": 512,
            "q": 936,
            "k": 0
        }

        middlegame_pesto_tables = {
            "p": middlegame_pawn_table,
            "n": middlegame_knight_table,
            "b": middlegame_bishop_table,
            "r": middlegame_rook_table,
            "q": middlegame_queen_table,
            "k": middlegame_king_table
        }

        endgame_pesto_tables = {
            "p": endgame_pawn_table,
            "n": endgame_knight_table,
            "b": endgame_bishop_table,
            "r": endgame_rook_table,
            "q": endgame_queen_table,
            "k": endgame_king_table
        }

        def flip_table(table):
            flip_temp_table = list(table)
            for i in range(len(table)):
                flip_temp_table[i] = table[i ^ 56]
            return tuple(flip_temp_table)

        middlegame_tables = ()
        endgame_tables = ()
        for piece in ("p", "n", "b", "r", "q", "k"):
            temp_table = []
            for square in chess.SQUARES:
                temp_table.append(middlegame_values[piece] + middlegame_pesto_tables[piece][square])
            middlegame_tables = middlegame_tables + (tuple(flip_table(temp_table)),)
            middlegame_tables = middlegame_tables + (tuple(temp_table),)
            temp_table = []
            for square in chess.SQUARES:
                temp_table.append(endgame_values[piece] + endgame_pesto_tables[piece][square])
            endgame_tables = endgame_tables + (tuple(flip_table(temp_table)),)
            endgame_tables = endgame_tables + (tuple(temp_table),)
        return middlegame_tables, endgame_tables

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
                piece_index = (2 * piece_type - color) - 1
                for square in self.board.pieces(piece_type, color):
                    middlegame[not color] += self.middlegame_tables[piece_index][square]
                    endgame[not color] += self.endgame_tables[piece_index][square]
                    game_phase += game_phase_values[piece_index]

        middlegame_score = middlegame[chess.WHITE] - middlegame[chess.BLACK]
        endgame_score = endgame[chess.WHITE] - endgame[chess.BLACK]
        middlegame_phase = game_phase
        middlegame_phase = min(middlegame_phase, 24)
        endgame_phase = 24 - middlegame_phase
        value = (middlegame_score * middlegame_phase + endgame_score * endgame_phase) / 24

        if self.player == chess.WHITE:
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
