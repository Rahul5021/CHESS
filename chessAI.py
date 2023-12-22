import random

piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3
MAX_KILLER_MOVES = 20

knight_position_score = [[1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 2, 2, 2, 2, 2, 2, 1],
                         [1, 2, 3, 3, 3, 3, 2, 1],
                         [1, 2, 3, 4, 4, 3, 2, 1],
                         [1, 2, 3, 4, 4, 3, 2, 1],
                         [1, 2, 3, 3, 3, 3, 2, 1],
                         [1, 2, 2, 2, 2, 2, 2, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1]]

bishop_position_score = [[4, 3, 2, 1, 1, 2, 3, 4],
                         [3, 4, 3, 2, 2, 3, 4, 3],
                         [2, 3, 4, 3, 3, 4, 3, 2],
                         [1, 2, 3, 4, 4, 3, 2, 1],
                         [1, 2, 3, 4, 4, 3, 2, 1],
                         [2, 3, 4, 3, 3, 4, 3, 2],
                         [3, 4, 3, 2, 2, 3, 4, 3],
                         [4, 3, 2, 1, 1, 2, 3, 4]]

rook_position_score = [[4, 3, 4, 4, 4, 4, 3, 4],
                       [4, 4, 4, 4, 4, 4, 4, 4],
                       [1, 1, 2, 3, 3, 2, 1, 1],
                       [1, 2, 3, 4, 4, 3, 2, 1],
                       [1, 2, 3, 4, 4, 3, 2, 1],
                       [1, 1, 2, 3, 3, 2, 1, 1],
                       [4, 4, 4, 4, 4, 4, 4, 4],
                       [4, 3, 4, 4, 4, 4, 3, 4]]

queen_position_score = [[1, 1, 1, 3, 1, 1, 1, 1],
                        [1, 2, 3, 3, 3, 1, 1, 1],
                        [1, 4, 3, 3, 3, 4, 2, 1],
                        [1, 2, 3, 3, 3, 2, 2, 1],
                        [1, 2, 3, 3, 3, 2, 2, 1],
                        [1, 4, 3, 3, 3, 4, 2, 1],
                        [1, 2, 3, 3, 3, 1, 1, 1],
                        [1, 1, 1, 3, 1, 1, 1, 1]]

white_pawn_position_score = [[8, 8, 8, 8, 8, 8, 8, 8],
                             [8, 8, 8, 8, 8, 8, 8, 8],
                             [5, 6, 6, 7, 7, 6, 6, 5],
                             [2, 3, 3, 5, 5, 3, 3, 2],
                             [1, 2, 3, 4, 4, 3, 2, 1],
                             [1, 1, 2, 3, 3, 2, 1, 1],
                             [1, 1, 1, 0, 0, 1, 1, 1],
                             [0, 0, 0, 0, 0, 0, 0, 0]]

black_pawn_position_score = [[0, 0, 0, 0, 0, 0, 0, 0],
                             [1, 1, 1, 0, 0, 1, 1, 1],
                             [1, 1, 2, 3, 3, 2, 1, 1],
                             [1, 2, 3, 4, 4, 3, 2, 1],
                             [2, 3, 3, 5, 5, 3, 3, 2],
                             [2, 3, 3, 5, 5, 3, 3, 2],
                             [5, 6, 6, 7, 7, 6, 6, 5],
                             [8, 8, 8, 8, 8, 8, 8, 8],
                             [8, 8, 8, 8, 8, 8, 8, 8]]

king_position_scores = [[1, 1.5, 2, 2.5, 2.5, 2, 1.5, 1],
                        [1.5, 2, 2.5, 3, 3, 2.5, 2, 1.5],
                        [2, 2.5, 3, 3.5, 3.5, 3, 2.5, 2],
                        [2.5, 3, 3.5, 4, 4, 3.5, 3, 2.5],
                        [2.5, 3, 3.5, 4, 4, 3.5, 3, 2.5],
                        [2, 2.5, 3, 3.5, 3.5, 3, 2.5, 2],
                        [1.5, 2, 2.5, 3, 3, 2.5, 2, 1.5],
                        [1, 1.5, 2, 2.5, 2.5, 2, 1.5, 1]]

piece_position_scores = {"N": knight_position_score, "B": bishop_position_score, "Q": queen_position_score,
                         "R": rook_position_score, "wp": white_pawn_position_score, "bp": black_pawn_position_score,
                         "K": king_position_scores}

"""
Picks and returns a random move
"""


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


"""
helper method to make first recursive call
"""


def find_best_move(gs, valid_moves, return_queue):
    global next_move, move_count
    next_move = None
    random.shuffle(valid_moves)
    move_count = 0
    tt = {}
    find_move_pvs(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(move_count)
    return_queue.put(next_move)


"""
NegaMax Algorithm with Principal Variation Search (PVS)
"""
def find_move_pvs(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move, move_count
    move_count += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)
    # move ordering function call
    ordered_moves = new_order_moves(gs, valid_moves, depth)
    max_score = -CHECKMATE
    for index, move in enumerate(ordered_moves):
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = 0
        if index == 0:
            score = -find_move_pvs(gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        else:
            score = -find_move_pvs(gs, next_moves, depth - 1, -alpha - 1, -alpha, -turn_multiplier)
            if alpha < score < beta:
                score = -find_move_pvs(gs, next_moves, depth - 1, -beta, -score, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
        if max_score > alpha:  # pruning happens
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def find_best_move_pvs(gs, valid_moves, return_queue):
    global next_move, move_count
    next_move = None
    random.shuffle(valid_moves)
    move_count = 0
    tt = {}
    find_move_pvs(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(move_count)
    return_queue.put(next_move)


"""
A positive score is good for white, a negative score is good for black
"""


def score_board(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    if gs.staleMate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piece_position_score = 0
                if square[1] == 'p':
                    piece_position_score = piece_position_scores[square][row][col]
                else:
                    piece_position_score = piece_position_scores[square[1]][row][col]
                if square[0] == 'w':
                    if square[1] == 'K':
                        score += piece_score[square[1]] * 10 + piece_position_score * .1
                    else:
                        score += piece_score[square[1]] + piece_position_score * .1
                elif square[0] == 'b':
                    if square[1] == 'K':
                        score -= piece_score[square[1]] * 10 + piece_position_score * .1
                    else:
                        score -= piece_score[square[1]] + piece_position_score * .1
    pawn_structure_score = evaluate_pawn_structure(gs)
    score += pawn_structure_score
    if gs.inCheck:
        if gs.whiteToMove:
            score -= 0.5
        else:
            score += 0.5
    return score


# move ordering


def new_order_moves(gs, valid_moves, depth):
    if len(gs.killer_moves) > MAX_KILLER_MOVES:
        oldest_moves = sorted(gs.killer_moves, key=lambda move: gs.moveLog.index(move))[0:MAX_KILLER_MOVES // 2]
        for move in oldest_moves:
            gs.killer_moves.remove(move)

    # Technique 1: Order checkmate moves first
    scored_moves = []
    checkmate_moves = []
    for move in valid_moves:
        gs.make_move(move)
        if gs.checkMate:
            checkmate_moves.append((move, depth))
        else:
            score = score_board(gs)
            scored_moves.append((move, score))
        gs.undo_move()

    if checkmate_moves:
        checkmate_moves.sort(key=lambda move: move[1])
        ordered_moves = [move_tuple[0] for move_tuple in checkmate_moves]
    else:
        # Technique 2: Order captures before other moves
        capture_moves = []
        for move in scored_moves:
            if gs.board != "--":
                capture_moves.append(move)
                scored_moves.remove(move)
        capture_moves.sort(key=lambda x: x[1], reverse=True)
        scored_moves.sort(key=lambda x: x[1], reverse=True)

    # Technique 3: Use history heuristic to order non-capture moves
        history_moves = []
        for move in scored_moves:
            if gs.moveLog:
                for i in range(0, len(gs.moveLog), 2):
                    if move[0] == gs.moveLog[i]:
                        history_moves.append(move)
                        scored_moves.remove(move)
                        break
        history_moves.sort(key=lambda x: x[1], reverse=True)
        scored_moves.sort(key=lambda x: x[1], reverse=True)

        # Technique 4: Use killer moves to order non-capture moves
        killer_moves_list = list(gs.killer_moves)
        for move in scored_moves:
            if move[0] in gs.killer_moves:
                killer_moves_list.append(move[0])
                scored_moves.remove(move)
        killer_moves_list.sort(key=lambda x: x[1], reverse=True)
        scored_moves.sort(key=lambda x: x[1], reverse=True)

        # Combine all ordered move lists
        ordered_moves = [move_tuple[0] for move_tuple in capture_moves + history_moves + scored_moves]

    return ordered_moves


# pawn structure
# pawn structure evaluation
def evaluate_pawn_structure(gs):
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square == 'wp':
                # Isolated pawn penalty
                if col > 0 and gs.board[row][col - 1] != 'wp' and gs.board[row + 1][col - 1] != 'wp' and \
                        gs.board[row - 1][col - 1] != 'wp':
                    score -= 0.5
                elif col < 7 and gs.board[row][col + 1] != 'wp' and gs.board[row + 1][col + 1] != 'wp' and \
                        gs.board[row - 1][col + 1] != 'wp':
                    score -= 0.5

                # Passed pawn bonus
                if row >= 5 and gs.board[row - 1][col] == '--' and gs.board[row - 2][col] == '--' and \
                        gs.board[row - 3][col] == '--':
                    score += 1

                # Pawn chain bonus
                if row >= 1 and gs.board[row - 1][col] == 'wp':
                    if row >= 2 and gs.board[row - 2][col] == 'wp':
                        if row >= 3 and gs.board[row - 3][col] == 'wp':
                            score += 1
                        else:
                            score += 0.5
                    else:
                        score += 0.25

            elif square == 'bp':
                # Isolated pawn penalty
                if col > 0 and gs.board[row][col - 1] != 'bp' and gs.board[row + 1][col - 1] != 'bp' and \
                        gs.board[row - 1][col - 1] != 'bp':
                    score += 0.5
                elif col < 7 and gs.board[row][col + 1] != 'bp' and gs.board[row + 1][col + 1] != 'bp' and \
                        gs.board[row - 1][col + 1] != 'bp':
                    score += 0.5

                # Passed pawn bonus
                if row <= 2 and gs.board[row + 1][col] == '--' and gs.board[row + 2][col] == '--' and \
                        gs.board[row + 3][col] == '--':
                    score -= 1

                # Pawn chain bonus
                if row <= 6 and gs.board[row + 1][col] == 'bp':
                    if row <= 5 and gs.board[row + 2][col] == 'bp':
                        if row <= 4 and gs.board[row + 3][col] == 'bp':
                            score -= 1
                        else:
                            score -= 0.5
                    else:
                        score -= 0.25
    return score


