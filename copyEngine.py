"""
This class is responsible for storing all the information about current state of chess game.
It is also responsible for determining the valid moves at the current state.
It will also keep the move log.
"""


class GameState:
    def __init__(self):
        self.board = [
            # board is a 8x8 2D list, each element of the list has two characters
            # the first character represents the color of piece "b" or "w"
            # the second character represent the type of piece
            # "--" empty space with no piece
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveFunctions = {"p": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
                              "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.killer_moves = set()
        self.checkMate = False
        self.staleMate = False
        self.isPieceCapture = False
        self.enPassantPossible = ()  # coordinates for the square where en passant capture is possible
        self.enPassantLog = [self.enPassantPossible]
        self.currentCastleRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastleRights.wks, self.currentCastleRights.bks,
                                             self.currentCastleRights.wqs, self.currentCastleRights.bqs)]

    """
    Takes a move as a parameter and executes it, this won't work for castling, pawn promotion, en-passant
    """

    def make_move(self, move):
        self.board[move.end_row][move.end_cols] = move.piece_moved
        self.board[move.start_row][move.start_cols] = "--"
        self.moveLog.append(move)  # for the undo and click history
        self.whiteToMove = not self.whiteToMove  # swaps the player
        # update king's position
        if move.piece_moved == "wK":
            self.whiteKingLocation = (move.end_row, move.end_cols)
        elif move.piece_moved == "bK":
            self.blackKingLocation = (move.end_row, move.end_cols)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_cols] = move.piece_moved[0] + "Q"

        # update enPassantPossible variable
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:  # only on 2 square advance
            self.enPassantPossible = ((move.start_row + move.end_row) // 2, move.end_cols)
        else:
            self.enPassantPossible = ()

        # en passant
        if move.is_en_passant_move:
            self.board[move.start_row][move.end_cols] = "--"  # capturing the pawn

        # castle move
        if move.is_castle_move:
            if move.end_cols - move.start_cols == 2:  # king side castle move
                self.board[move.end_row][move.end_cols - 1] = self.board[move.end_row][
                    move.end_cols + 1]  # moves the rook
                self.board[move.end_row][move.end_cols + 1] = "--"  # erases the old rook
            else:  # queen side castle move
                self.board[move.end_row][move.end_cols + 1] = self.board[move.end_row][
                    move.end_cols - 2]  # moves the rook
                self.board[move.end_row][move.end_cols - 2] = "--"  # erases the old rook

        self.enPassantLog.append(self.enPassantPossible)

        # update castling rights - whenever it is a king or rook move
        self.update_castle_rights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastleRights.wks, self.currentCastleRights.bks,
                                                 self.currentCastleRights.wqs, self.currentCastleRights.bqs))
        if move.is_piece_capture:
            self.isPieceCapture = True

    def undo_move(self):
        if len(self.moveLog) != 0:  # make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_cols] = move.piece_moved
            self.board[move.end_row][move.end_cols] = move.piece_captured
            self.whiteToMove = not self.whiteToMove  # switch turns back
            # update king's position
            if move.piece_moved == "wK":
                self.whiteKingLocation = (move.start_row, move.start_cols)
            elif move.piece_moved == "bK":
                self.blackKingLocation = (move.start_row, move.start_cols)
            # undo en passant
            if move.is_en_passant_move:
                self.board[move.end_row][move.end_cols] = "--"  # leave landing square blank
                self.board[move.start_row][move.end_cols] = move.piece_captured
            self.enPassantLog.pop()
            self.enPassantPossible = self.enPassantLog[-1]
            # undo castling rights
            self.castleRightsLog.pop()  # get rid of new castle rights from the move we are undoing
            # set the current castle rights to the last one in the list
            castle_rights = self.castleRightsLog[-1]
            self.currentCastleRights = CastleRights(castle_rights.wks, castle_rights.bks,
                                                    castle_rights.wqs, castle_rights.wqs)
            # undo castle move
            if move.is_castle_move:
                if move.end_cols - move.start_cols == 2:  # king side castle move
                    self.board[move.end_row][move.end_cols + 1] = self.board[move.end_row][
                        move.end_cols - 1]  # moves the rook
                    self.board[move.end_row][move.end_cols - 1] = "--"  # erases the old rook
                else:  # queen side castle move
                    self.board[move.end_row][move.end_cols - 2] = self.board[move.end_row][
                        move.end_cols + 1]  # moves the rook
                    self.board[move.end_row][move.end_cols + 1] = "--"  # erases the old rook

            self.checkMate = False
            self.staleMate = False
            self.isPieceCapture = False

    """
    update the castle the rights given move
    """

    def update_castle_rights(self, move):
        if move.piece_moved == "wK":
            self.currentCastleRights.wks = False
            self.currentCastleRights.wqs = False
        elif move.piece_moved == "bK":
            self.currentCastleRights.bks = False
            self.currentCastleRights.bqs = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_cols == 0:  # left rook
                    self.currentCastleRights.wqs = False
                elif move.start_cols == 7:  # right rook
                    self.currentCastleRights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_cols == 0:  # left rook
                    self.currentCastleRights.bqs = False
                elif move.start_cols == 7:  # right rook
                    self.currentCastleRights.bks = False
        # # if rook is captured
        if move.piece_captured == "wR":
            if move.end_row == 7:
                if move.end_cols == 0:
                    self.currentCastleRights.wqs = False
                elif move.end_cols == 7:
                    self.currentCastleRights.wks = False
        elif move.piece_captured == "bR":
            if move.end_row == 0:
                if move.end_cols == 0:
                    self.currentCastleRights.bqs = False
                elif move.end_cols == 7:
                    self.currentCastleRights.bks = False

    ''' ALL MOVES CONSIDERING CHECKS'''

    def get_valid_moves(self):
        temp_en_passant_possible = self.enPassantPossible
        temp_castle_rights = CastleRights(self.currentCastleRights.wks, self.currentCastleRights.bks,
                                          self.currentCastleRights.wqs, self.currentCastleRights.bqs)
        # for log in self.castleRightsLog:
        #     print(log.wks, log.bks, log.wqs, log.bqs)
        # print()
        moves = []
        self.inCheck, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.whiteToMove:
            king_row = self.whiteKingLocation[0]
            king_col = self.whiteKingLocation[1]
        else:
            king_row = self.blackKingLocation[0]
            king_col = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # only 1 check, block check or move king
                moves = self.get_all_possible_moves()
                # to block a check you must have a piece into one the squares between enemy and king
                check = self.checks[0]  # check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]  # enemy piece causing the check
                valid_squares = []  # squares that pieces can move to
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        #  check2 and check3 are check direction
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        # once you get piece end checks
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                # get rid of any moves that don't block or check king
                # go through backwards when you are removing elements from a list
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != 'K':  # move doesn't move king, so it must block or capture
                        if not (moves[i].end_row, moves[i].end_cols) in valid_squares:  # move doesn't block or capture
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.get_king_moves(king_row, king_col, moves)
        else:  # not in check so all moves are fine
            moves = self.get_all_possible_moves()
        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        if self.whiteToMove:
            self.get_castle_moves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.get_castle_moves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        self.enPassantPossible = temp_en_passant_possible
        self.currentCastleRights = temp_castle_rights
        return moves

    def square_under_attack(self, row, col):
        self.whiteToMove = not self.whiteToMove
        opp_moves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove
        for move in opp_moves:
            if move.end_row == row and move.end_cols == col:
                return True
        return False

    """ALL MOVES NOT CONSIDERING CHECKS"""

    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for cols in range(len(self.board[row])):
                turn = self.board[row][cols][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][cols][1]
                    self.moveFunctions[piece](row, cols, moves)  # calls the function based on the piece type
        return moves

    '''Get all the pawn moves'''

    def get_pawn_moves(self, row, cols, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == cols:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:  # white pawn moves
            king_row, king_col = self.whiteKingLocation
            if self.board[row - 1][cols] == "--":  # 1 square advance
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((row, cols), (row - 1, cols), self.board))
                    if row == 6 and self.board[row - 2][cols] == "--":  # 2 squares advance
                        moves.append(Move((row, cols), (row - 2, cols), self.board))
            if cols - 1 >= 0:  # captures to the left
                if not piece_pinned or pin_direction == (-1, -1):
                    if self.board[row - 1][cols - 1][0] == 'b':  # enemy piece to capture
                        moves.append(Move((row, cols), (row - 1, cols - 1), self.board))
                    if (row - 1, cols - 1) == self.enPassantPossible:
                        attacking_piece = blocking_piece = False
                        if king_row == row:
                            if king_col < cols:
                                inside_range = range(king_col + 1, cols - 1)
                                outside_range = range(cols + 1, 8)
                            else:
                                inside_range = range(king_col - 1, cols, -1)
                                outside_range = range(cols - 2, -1, -1)
                            for i in inside_range:
                                if self.board[row][i] != "--":
                                    blocking_piece = True
                            for i in outside_range:
                                square = self.board[row][i]
                                if square[0] == 'b' and (square[1] == 'R' or square[1] == "Q"):
                                    attacking_piece = True
                                elif square != "--":
                                    blocking_piece = True
                        if not attacking_piece or blocking_piece:
                            moves.append(Move((row, cols), (row - 1, cols - 1), self.board, is_en_passant_move=True))

            if cols + 1 <= 7:  # captures to the right
                if not piece_pinned or pin_direction == (-1, 1):
                    if self.board[row - 1][cols + 1][0] == 'b':
                        moves.append(Move((row, cols), (row - 1, cols + 1), self.board))
                    if (row - 1, cols + 1) == self.enPassantPossible:
                        attacking_piece = blocking_piece = False
                        if king_row == row:
                            if king_col < cols:
                                inside_range = range(king_col + 1, cols)
                                outside_range = range(cols + 2, 8)
                            else:
                                inside_range = range(king_col - 1, cols + 1, -1)
                                outside_range = range(cols - 1, -1, -1)
                            for i in inside_range:
                                if self.board[row][i] != "--":
                                    blocking_piece = True
                            for i in outside_range:
                                square = self.board[row][i]
                                if square[0] == 'b' and (square[1] == 'R' or square[1] == "Q"):
                                    attacking_piece = True
                                elif square != "--":
                                    blocking_piece = True
                        if not attacking_piece or blocking_piece:
                            moves.append(Move((row, cols), (row - 1, cols + 1), self.board, is_en_passant_move=True))
        else:  # black pawn moves
            king_row, king_col = self.blackKingLocation
            if self.board[row + 1][cols] == "--":  # 1 square advance
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((row, cols), (row + 1, cols), self.board))
                    if row == 1 and self.board[row + 2][cols] == "--":  # 2 square advance
                        moves.append(Move((row, cols), (row + 2, cols), self.board))
            if cols - 1 >= 0:  # captures to right
                if not piece_pinned or pin_direction == (1, -1):
                    if self.board[row + 1][cols - 1][0] == 'w':  # enemy piece to capture
                        moves.append(Move((row, cols), (row + 1, cols - 1), self.board))
                    if (row + 1, cols - 1) == self.enPassantPossible:
                        attacking_piece = blocking_piece = False
                        if king_row == row:
                            if king_col < cols:
                                inside_range = range(king_col + 1, cols)
                                outside_range = range(cols + 2, 8)
                            else:
                                inside_range = range(king_col - 1, cols + 1, -1)
                                outside_range = range(cols - 1, -1, -1)
                            for i in inside_range:
                                if self.board[row][i] != "--":
                                    blocking_piece = True
                            for i in outside_range:
                                square = self.board[row][i]
                                if square[0] == 'w' and (square[1] == 'R' or square[1] == "Q"):
                                    attacking_piece = True
                                elif square != "--":
                                    blocking_piece = True
                        if not attacking_piece or blocking_piece:
                            moves.append(Move((row, cols), (row + 1, cols - 1), self.board, is_en_passant_move=True))
            if cols + 1 <= 7:  # captures to the left
                if not piece_pinned or pin_direction == (1, 1):
                    if self.board[row + 1][cols + 1][0] == 'w':  # enemy piece to capture
                        moves.append(Move((row, cols), (row + 1, cols + 1), self.board))
                    if (row + 1, cols + 1) == self.enPassantPossible:
                        attacking_piece = blocking_piece = False
                        if king_row == row:
                            if king_col < cols:
                                inside_range = range(king_col + 1, cols - 1)
                                outside_range = range(cols + 1, 8)
                            else:
                                inside_range = range(king_col - 1, cols, -1)
                                outside_range = range(cols - 2, -1, -1)
                            for i in inside_range:
                                if self.board[row][i] != "--":
                                    blocking_piece = True
                            for i in outside_range:
                                square = self.board[row][i]
                                if square[0] == 'w' and (square[1] == 'R' or square[1] == "Q"):
                                    attacking_piece = True
                                elif square != "--":
                                    blocking_piece = True
                        if not attacking_piece or blocking_piece:
                            moves.append(Move((row, cols), (row + 1, cols + 1), self.board, is_en_passant_move=True))

    '''Get all the rook moves'''

    def get_rook_moves(self, row, cols, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == cols:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                # can't remove queen from pin on rook moves, only remove it on bishop moves
                # if self.board[row][cols][1] != 'Q':
                #     self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_column = cols + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:  # on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_column]
                        if end_piece == "--":  # empty space valid
                            moves.append(Move((row, cols), (end_row, end_column), self.board))
                        elif end_piece[0] == enemy_color:  # enemy piece valid
                            moves.append(Move((row, cols), (end_row, end_column), self.board))
                            break
                        else:  # friendly and not empty piece valid
                            break
                else:  # off board
                    break

    '''Get all the knight moves'''

    def get_knight_moves(self, row, cols, moves):
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == cols:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = "w" if self.whiteToMove else "b"
        for k in knight_moves:
            end_row = row + k[0]
            end_column = cols + k[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:  # on board
                if not piece_pinned:
                    end_piece = self.board[end_row][end_column]
                    if end_piece[0] != ally_color:  # enemy piece or empty space
                        moves.append(Move((row, cols), (end_row, end_column), self.board))

    '''Get all the bishop moves'''

    def get_bishop_moves(self, row, cols, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == cols:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, 1), (1, 1), (1, -1), (-1, -1))
        enemy_color = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_column = cols + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:  # on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_column]
                        if end_piece == "--":  # empty space valid
                            moves.append(Move((row, cols), (end_row, end_column), self.board))
                        elif end_piece[0] == enemy_color:  # enemy piece valid
                            moves.append(Move((row, cols), (end_row, end_column), self.board))
                            break
                        else:  # friendly and not empty piece valid
                            break
                else:  # off board
                    break

    '''Get all the queen moves'''

    # def get_queen_moves(self, row, cols, moves):
    #     self.get_bishop_moves(row, cols, moves)
    #     self.get_rook_moves(row, cols, moves)
    def get_queen_moves(self, row, cols, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == cols:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][cols][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, 1), (1, 1), (1, -1), (-1, -1))
        enemy_color = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_column = cols + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:  # on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_column]
                        if end_piece == "--":  # empty space valid
                            moves.append(Move((row, cols), (end_row, end_column), self.board))
                        elif end_piece[0] == enemy_color:  # enemy piece valid
                            moves.append(Move((row, cols), (end_row, end_column), self.board))
                            break
                        else:  # friendly and not empty piece valid
                            break
                else:  # off board
                    break

    '''Get all the king moves'''

    def get_king_moves(self, row, cols, moves):
        king_row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        king_col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = row + king_row_moves[i]
            end_column = cols + king_col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_column < 8:  # on board
                end_piece = self.board[end_row][end_column]
                if end_piece[0] != ally_color:  # empty or enemy piece
                    # place king on end square and check for checks
                    if ally_color == 'w':
                        self.whiteKingLocation = (end_row, end_column)
                    else:
                        self.blackKingLocation = (end_row, end_column)
                    in_check, pins, checks, = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((row, cols), (end_row, end_column), self.board))
                    # place king back on original position
                    if ally_color == 'w':
                        self.whiteKingLocation = (row, cols)
                    else:
                        self.blackKingLocation = (row, cols)

    """
    Returns if the player is in check, a list of pins and a list of checks
    """

    def check_for_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False
        if self.whiteToMove:
            enemy_color = 'b'
            ally_color = 'w'
            start_row = self.whiteKingLocation[0]
            start_col = self.whiteKingLocation[1]
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row = self.blackKingLocation[0]
            start_col = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pins = ()
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pins == ():
                            possible_pins = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece[0] == enemy_color:
                        piece_type = end_piece[1]
                        if (0 <= j <= 3 and piece_type == 'R') or \
                                (4 <= j <= 7 and piece_type == 'B') or \
                                (i == 1 and piece_type == 'p' and
                                 ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))) or \
                                (piece_type == 'Q' and 0 <= j <= 7) or (i == 1 and piece_type == 'K'):
                            if possible_pins == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pins)
                                break
                        else:
                            break
                else:
                    break

        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for k in knight_moves:
            end_row = start_row + k[0]
            end_col = start_col + k[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':
                    in_check = True
                    checks.append((end_row, end_col, k[0], k[1]))
        return in_check, pins, checks

    """
    Generate all valid castle moves for the king at (row, cols) and add them to list of all moves
    """

    def get_castle_moves(self, row, cols, moves):
        if self.inCheck:
            return  # can't castle when king is in check
        if (self.whiteToMove and self.currentCastleRights.wks) or (
                not self.whiteToMove and self.currentCastleRights.bks):
            self.get_king_side_castle_moves(row, cols, moves)
        if (self.whiteToMove and self.currentCastleRights.wqs) or (
                not self.whiteToMove and self.currentCastleRights.bqs):
            self.get_queen_side_castle_moves(row, cols, moves)

    def get_king_side_castle_moves(self, row, cols, moves):
        if self.board[row][cols + 1] == '--' and self.board[row][cols + 2] == '--':
            if not self.square_under_attack(row, cols + 1) and not self.square_under_attack(row, cols + 2):
                moves.append(Move((row, cols), (row, cols + 2), self.board, is_castle_move=True))

    def get_queen_side_castle_moves(self, row, cols, moves):
        if self.board[row][cols - 1] == '--' and self.board[row][cols - 2] == '--' and self.board[row][
            cols - 3] == "--" and \
                not self.square_under_attack(row, cols - 1) and not self.square_under_attack(row, cols - 2):
            moves.append(Move((row, cols), (row, cols - 2), self.board, is_castle_move=True))


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # maps keys to values
    # key : value

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_en_passant_move=False, is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_cols = start_sq[1]
        self.end_row = end_sq[0]
        self.end_cols = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_cols]
        self.piece_captured = board[self.end_row][self.end_cols]
        # pawn promotion
        self.is_pawn_promotion = False
        if (self.piece_moved == "wp" and self.end_row == 0) or (self.piece_moved == "bp" and self.end_row == 7):
            self.is_pawn_promotion = True
        # en passant
        self.is_en_passant_move = is_en_passant_move
        if is_en_passant_move:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"
        self.is_castle_move = is_castle_move
        self.is_piece_capture = self.piece_captured != "--"
        self.move_id = self.start_row * 1000 + self.start_cols * 100 + self.end_row * 10 + self.end_cols

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        # you can add this to make real chess notation
        return self.get_rank_files(self.start_row, self.start_cols) + "-->" + \
            self.get_rank_files(self.end_row, self.end_cols)

    def get_rank_files(self, row, cols):
        return self.cols_to_files[cols] + self.rows_to_ranks[row]

    def __str__(self):
        # castle move
        if self.is_castle_move:
            return "O-O" if self.end_cols == 6 else "O-O-O"

        end_square = self.get_rank_files(self.end_row, self.end_cols)
        # pawn moves
        if self.piece_moved[1] == 'p':
            if self.is_piece_capture:
                return self.cols_to_files[self.start_cols] + "x" + end_square
            else:
                return end_square

            # pawn promotion

        # two of the same type of piece moving to a square , Nbd2 if both knights can move to d2

        # also adding + for check move, and # for checkmate move

        # piece moved
        move_string = self.piece_moved[1]
        if self.is_piece_capture:
            move_string += "x"
        return move_string + end_square

    def __hash__(self):
        return hash(str(self))
