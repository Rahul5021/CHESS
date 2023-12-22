"""
This is our main driver file. This will be responsible for handling user input and displaying current GameState Object.
"""

import pygame as pg
import copyEngine
import chessAI
import pygame_gui
from multiprocessing import Queue, Process


pg.init()
BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_WIDTH = 225
MOVE_LOG_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_WIDTH // DIMENSION
MAX_FPS = 15
IMAGES = {}
SOUNDS = {}

'''
 Initialize global dictionary of images. This will be called exactly once.
'''


def load_images():
    pieces = ["wp", "bp", "wR", "bR", "wN", "bN", "wB", "bB", "wQ", "bQ", "wK", "bK"]
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load("images/" + piece + ".png"), (64, 64))
    # We can access an image by 'IMAGES["wp"]


def load_sounds():
    sounds = ["capture", "draw", "move-self", "game_over"]
    for sound in sounds:
        SOUNDS[sound] = pg.mixer.Sound("sounds/" + sound + ".wav")


"""
The main driver of our code. This will handle user input and updating graphics.
"""


def main():
    screen = pg.display.set_mode((BOARD_WIDTH + MOVE_LOG_WIDTH, BOARD_HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    gs = copyEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_log_font = pg.font.SysFont("Arial", 15, True, False)
    move_made = False  # flag variable for when move is made
    animate = False
    game_over = False
    game_over_sound_played = False  # flag to indicate if game over sound has been played
    draw_sound_played = False
    load_images()  # only once before while loop
    load_sounds()
    running = True
    sq_selected = ()  # no square is selected initially,keeps track of the last click of the user ,(tuple: (row,column))
    player_clicks = []  # keeps track of player clicks, (two tuples: [(6,4),(4,4)])
    player_one = True  # if human is playing white, then this will be true. If an AI is playing then false.
    player_two = False  # same as above for black
    ai_thinking = False
    move_finder_process = None
    move_undone = False
    while running:
        human_turn = (gs.whiteToMove and player_one) or (not gs.whiteToMove and player_two)
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            # mouse handlers
            elif e.type == pg.MOUSEBUTTONDOWN:
                if not game_over:
                    location = pg.mouse.get_pos()  # (x,y) location of mouse.
                    cols = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row, cols):  # the user clicked the same square twice
                        sq_selected = ()  # deselect
                        player_clicks = []  # clearing player clicks
                    else:
                        sq_selected = (row, cols)
                        player_clicks.append(sq_selected)  # append for both 1st and second clicks
                    if len(player_clicks) == 2 and human_turn:  # after 2nd click
                        move = copyEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                if move.piece_captured != "--":
                                    pg.mixer.Sound.play(SOUNDS["capture"])
                                else:
                                    pg.mixer.Sound.play(SOUNDS["move-self"])
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = ()  # resets the user clicks
                                player_clicks = []  # clear player clicks
                        if not move_made:
                            player_clicks = [sq_selected]
            # key handlers
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_z:  # undo when 'z' is pressed
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                    draw_sound_played = False
                    game_over_sound_played = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                if e.key == pg.K_r:  # reset the board when 'r' is pressed
                    gs = copyEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    animate = False
                    move_made = False
                    game_over = False
                    draw_sound_played = False
                    game_over_sound_played = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
        # AI move finder logic
        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                print("thinking...")
                return_queue = Queue()
                move_finder_process = Process(target=chessAI.find_best_move, args=(gs, valid_moves, return_queue))
                move_finder_process.start()
                # ai_move = chessAI.find_best_move(gs, valid_moves)
            if not move_finder_process.is_alive():
                print("Done Thinking")
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = chessAI.find_random_move(valid_moves)
                gs.make_move(ai_move)
                move_made = True
                animate = True
                ai_thinking = False

        if move_made:
            if animate:
                animate_move(gs.moveLog[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False
            move_undone = False
        draw_game_state(screen, gs, valid_moves, sq_selected, gs.whiteKingLocation, gs.blackKingLocation, move_log_font)
        if gs.inCheck:
            if gs.checkMate:
                game_over = True
                if not game_over_sound_played:
                    pg.mixer.Sound.play(SOUNDS["game_over"])
                    game_over_sound_played = True
                if gs.whiteToMove:
                    draw_end_game_text(screen, "Black Wins")
                else:
                    draw_end_game_text(screen, "White Wins")
        if gs.staleMate:
            if not draw_sound_played:
                pg.mixer.Sound.play(SOUNDS["draw"])
                pg.time.delay(100)
                draw_sound_played = True
            game_over = True
            draw_end_game_text(screen, "Draw")
        pg.display.flip()


# def last_move(screen, move):
#     print("here")
#     start_row, start_cols = move.start_row, move.start_cols
#     end_row, end_cols = move.end_row, move.end_cols
#     s = pg.Surface((SQ_SIZE, SQ_SIZE))  # create a surface to draw on
#     s.set_alpha(128)  # set transparency
#     s.fill(pg.Color('brown'))  # set color
#     screen.blit(s, pg.Rect(start_cols * SQ_SIZE, start_row * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # draw on the screen
#     screen.blit(s, pg.Rect(end_cols * SQ_SIZE, end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # draw on the screen

"""
highlight square selected and moves for square selected
"""


def highlight_square(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        row, col = sq_selected
        if gs.board[row][col][0] == ("w" if gs.whiteToMove else "b"):  # sq_selected is a piece that can be moves
            # highlight selected square
            s = pg.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(255)  # transparency value
            s.fill(pg.Color("goldenrod"))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
            # highlight moves from that square\
            s.set_alpha(150)
            s.fill(pg.Color("goldenrod"))
            for move in valid_moves:
                if move.start_row == row and move.start_cols == col:
                    screen.blit(s, (move.end_cols * SQ_SIZE, move.end_row * SQ_SIZE))


"""
Responsible for highlighting the king when its in check but not checkmate
"""


def check(screen, w_location, b_location, gs):
    if gs.inCheck:
        if gs.whiteToMove:
            row, col = w_location[0], w_location[1]
            s = pg.Surface((SQ_SIZE, SQ_SIZE))  # create a surface to draw on
            s.set_alpha(225)  # set transparency
            s.fill(pg.Color('red'))  # set color
            screen.blit(s, pg.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # draw on the screen
        else:
            row, col = b_location[0], b_location[1]
            s = pg.Surface((SQ_SIZE, SQ_SIZE))  # create a surface to draw on
            s.set_alpha(225)  # set transparency
            s.fill(pg.Color('red'))  # set color
            screen.blit(s, pg.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # draw on the screen


"""
Responsible for all graphics within a current game state
"""


def draw_game_state(screen, gs, valid_moves, sq_selected, w_location, b_location, move_log_font):
    draw_board(screen)  # draw the squares on the board
    highlight_square(screen, gs, valid_moves, sq_selected)
    check(screen, w_location, b_location, gs)
    draw_pieces(screen, gs.board)  # draw pieces on top of square
    draw_move_log(screen, gs, move_log_font)


"""
Draw the squares on the board
"""


def draw_board(screen):
    colors = [pg.Color("beige"), pg.Color("darkgreen")]
    for row in range(DIMENSION):
        for cols in range(DIMENSION):
            color = colors[((row+cols) % 2)]
            pg.draw.rect(screen, color, pg.Rect(cols*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    pg.display.set_caption("CHESS")

# Draw the pieces on the board


def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for cols in range(DIMENSION):
            piece = board[row][cols]
            if piece != "--":
                screen.blit(IMAGES[piece], pg.Rect(cols*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

# animating a move


def animate_move(move, screen, board, clock):
    beige = (245, 245, 220)
    dark_green = (0, 100, 0)
    colors = (beige, dark_green)
    d_r = move.end_row - move.start_row
    d_c = move.end_cols - move.start_cols
    frames_per_square = 8  # frames to move one square
    frame_count = (abs(d_r) + abs(d_c)) * frames_per_square
    for frame in range(frame_count + 1):
        r, c = (move.start_row + d_r * frame/frame_count, move.start_cols + d_c * frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_cols) % 2]
        end_square = pg.Rect(move.end_cols * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pg.draw.rect(screen, color, end_square)
        if move.piece_captured != '--':
            if move.is_en_passant_move:
                en_passant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = pg.Rect(move.end_cols * SQ_SIZE, en_passant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        screen.blit(IMAGES[move.piece_moved], pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pg.display.flip()
        clock.tick(100)


"""
Draws the move log
"""


def draw_move_log(screen, gs, font):
    move_log_rect = pg.Rect(BOARD_WIDTH, 0, MOVE_LOG_WIDTH, MOVE_LOG_HEIGHT)
    pg.draw.rect(screen, pg.Color("Black"), move_log_rect)
    move_log = gs.moveLog
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + "." + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i+1]) + "  "
        move_texts.append(move_string)
    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]
        text_object = font.render(text, True, pg.Color("White"))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


def draw_end_game_text(screen, text):
    font = pg.font.SysFont("arial", 32, True, False)
    text_object = font.render(text, False, pg.Color("Black"))
    text_location = pg.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                  BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, pg.Color("gray"))
    screen.blit(text_object, text_location.move(2, 2))


# def login_form():
#     # GUI manager
#     manager = pygame_gui.UIManager((BOARD_WIDTH, BOARD_HEIGHT))
#
#     # Create text inputs
#     username_input = pygame_gui.elements.UITextEntryLine(relative_rect=pg.Rect((50, 100), (400, 50)), manager=manager)
#     password_input = PasswordTextInput(relative_rect=pg.Rect((50, 200), (400, 50)), manager=manager)
#
#     error_message = ""
#
#     running = True
#     while running:
#         time_delta = clock.tick(60) / 1000.0
#
#         for event in pg.event.get():
#             if event.type == pg.QUIT:
#                 running = False
#
#             # GUI manager process events
#             manager.process_events(event)
#
#             if event.type == pg.KEYDOWN:
#                 if event.key == pg.K_RETURN:
#                     username = username_input.get_text()
#                     password = password_input.get_text()
#
#                     if authenticate_user(username, password):
#                         running = False
#                         # Start the game or perform other actions
#                     else:
#                         error_message = "Invalid username or password"
#
#         screen.fill(pg.Color("white"))
#
#         # GUI manager draw UI
#         manager.update(time_delta)
#         manager.draw_ui(screen)
#
#         font = pg.font.Font(None, 32)
#
#         # Username label
#         username_label = font.render("Username:", True, pg.Color("black"))
#         screen.blit(username_label, (50, 70))
#
#         # Password label
#         password_label = font.render("Password:", True, pg.Color("black"))
#         screen.blit(password_label, (50, 170))
#
#         # Error message
#         error_text = font.render(error_message, True, pg.Color("red"))
#         screen.blit(error_text, (50, 300))
#
#         pg.display.flip()

if __name__ == "__main__":
    main()
