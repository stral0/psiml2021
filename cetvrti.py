import copy
import time

from PIL import Image

spot_width = 100
spot_height = 100
spots_left_coords = []
spots_top_coords = []
black_pieces_on_black_tiles = []
white_pieces_on_black_tiles = []
black_pieces_on_white_tiles = []
white_pieces_on_white_tiles = []
black_tile_tmp = None
zero2seven = [0, 1, 2, 3, 4, 5, 6, 7]


def resize_pieces_on_tiles():
    global spot_width
    global spot_height
    global black_pieces_on_black_tiles
    global white_pieces_on_black_tiles
    global black_pieces_on_white_tiles
    global white_pieces_on_white_tiles

    bob = []
    for img in black_pieces_on_black_tiles:
        bob.append(img.resize((int(spot_width), int(spot_height))))
    black_pieces_on_black_tiles = bob

    wob = []
    for img in white_pieces_on_black_tiles:
        wob.append(img.resize((int(spot_width), int(spot_height))))
    white_pieces_on_black_tiles = wob

    bow = []
    for img in black_pieces_on_white_tiles:
        bow.append(img.resize((int(spot_width), int(spot_height))))
    black_pieces_on_white_tiles = bow

    wow = []
    global black_tile_tmp
    for img in [black_tile_tmp] + white_pieces_on_white_tiles:
        wow.append(img.resize((int(spot_width), int(spot_height))))
    white_pieces_on_white_tiles = wow


def preprocess_pieces_and_tiles(path):
    global spot_width
    global spot_height
    global black_pieces_on_black_tiles
    global white_pieces_on_black_tiles
    global black_pieces_on_white_tiles
    global white_pieces_on_white_tiles

    pieces_path = path + '\\pieces'
    tiles_path = path + '\\tiles'
    black_tile_path = tiles_path + '\\black.png'
    white_tile_path = tiles_path + '\\white.png'
    black_pieces_path = pieces_path + '\\black'
    white_pieces_path = pieces_path + '\\white'

    pieces_names = ['pawn', 'bishop', 'knight', 'rook', 'queen', 'king']

    black_pieces = [black_pieces_path + '\\' + piece_name + '.png' for piece_name in pieces_names]
    white_pieces = [white_pieces_path + '\\' + piece_name + '.png' for piece_name in pieces_names]

    black_tile_img = Image.open(black_tile_path)
    global black_tile_tmp
    black_tile_tmp = copy.deepcopy(black_tile_img)
    white_tile_img = Image.open(white_tile_path)

    black_pieces_on_black_tiles = [black_tile_img]
    black_pieces_on_white_tiles = [white_tile_img]

    for black_piece in black_pieces:
        black_piece_img = Image.open(black_piece)
        assert black_piece_img.size == black_tile_img.size == white_tile_img.size

        mask = black_piece_img.split()[1 if black_piece_img.mode == 'LA' else 3].convert('1')

        piece_on_black_tile = Image.composite(black_piece_img, black_tile_img, mask)
        piece_on_white_tile = Image.composite(black_piece_img, white_tile_img, mask)

        black_pieces_on_black_tiles.append(piece_on_black_tile)
        black_pieces_on_white_tiles.append(piece_on_white_tile)

    white_pieces_on_black_tiles = [black_tile_img]
    white_pieces_on_white_tiles = [white_tile_img]

    for white_piece in white_pieces:
        white_piece_img = Image.open(white_piece)
        assert white_piece_img.size == black_tile_img.size == white_tile_img.size

        mask = white_piece_img.split()[1 if white_piece_img.mode == 'LA' else 3].convert('1')

        piece_on_black_tile = Image.composite(white_piece_img, black_tile_img, mask)
        piece_on_white_tile = Image.composite(white_piece_img, white_tile_img, mask)

        white_pieces_on_black_tiles.append(piece_on_black_tile)
        white_pieces_on_white_tiles.append(piece_on_white_tile)


def show_field(board_img, i, j):
    global spot_width
    global spot_height
    global spots_left_coords
    global spots_top_coords

    top = spots_top_coords[i]
    left = spots_left_coords[j]
    right = left + spot_width
    bottom = top + spot_height

    spot = board_img.crop((left, top, right, bottom))
    spot.show()


def get_board_position(board_img):
    global spot_width
    global spot_height
    global spots_left_coords
    global spots_top_coords

    board_position = []
    for left in spots_left_coords:
        for top in spots_top_coords:
            right = left + spot_width
            bottom = top + spot_height
            spot_on_board = board_img.crop((left, top, right, bottom))
            board_position.append(spot_on_board)

    return board_position


def divide_board(image, board_coord):
    board_image = image.crop(board_coord)

    global spot_width
    global spot_height
    global spots_left_coords
    global spots_top_coords

    spot_width = board_image.width / 8
    spot_height = board_image.height / 8

    spots_left_coords = [0]
    spots_top_coords = [0]
    for i in range(7):
        spots_left_coords.append(spots_left_coords[i] + spot_width)
        spots_top_coords.append(spots_top_coords[i] + spot_height)

    board_position = get_board_position(board_image)

    return board_position


def first_part(path):
    image = Image.open(path)
    board_coord = image.getbbox()

    return image, board_coord


def diff(J, I):
    arr1 = J.convert('L')
    arr2 = I.convert('L')

    suma = 0
    for i in range(arr2.size[0]):
        for j in range(arr2.size[1]):
            suma = suma + (arr2.getpixel((i, j)) - arr1.getpixel((i, j))) ** 2

    return suma


def recognize_piece(spot, pieces_with_labels):
    min_diff = -1.0
    label_of_min = ''
    # debuglist = []
    for piece_with_label in pieces_with_labels:
        piece = piece_with_label[0]
        label = piece_with_label[1]
        new_diff = diff(spot, piece)
        # debuglist.append(new_diff)
        if min_diff < 0 or new_diff < min_diff:
            min_diff = new_diff
            label_of_min = label
        if -0.1 < min_diff < 0.1:
            break
    # print(debuglist, label_of_min if 'empty' not in label_of_min else '')

    return label_of_min


def recognize_position(pos):
    global white_pieces_on_white_tiles
    global white_pieces_on_black_tiles
    global black_pieces_on_white_tiles
    global black_pieces_on_black_tiles

    resize_pieces_on_tiles()

    # all_pieces_on_all_tiles
    apoat = white_pieces_on_white_tiles + white_pieces_on_black_tiles
    apoat += black_pieces_on_white_tiles + black_pieces_on_black_tiles

    piece_labels = ['pawn', 'bishop', 'knight', 'rook', 'queen', 'king']
    white_pieces_labels = ['white_' + piece_name for piece_name in piece_labels]
    black_pieces_labels = ['black_' + piece_name for piece_name in piece_labels]
    black_on_black_labels = [piece_name + '_on_black' for piece_name in black_pieces_labels]
    black_on_white_labels = [piece_name + '_on_white' for piece_name in black_pieces_labels]
    white_on_black_labels = [piece_name + '_on_black' for piece_name in white_pieces_labels]
    white_on_white_labels = [piece_name + '_on_white' for piece_name in white_pieces_labels]
    labels = ['empty_on_black', 'empty_on_white'] + white_on_white_labels + ['empty_on_black'] + white_on_black_labels
    labels += ['empty_on_white'] + black_on_white_labels + ['empty_on_black'] + black_on_black_labels

    pieces_with_labels = list(zip(apoat, labels))

    position_text = []
    for spot in pos:
        label = recognize_piece(spot, pieces_with_labels)
        position_text.append(label)

    return position_text


def fix_row(el):
    if 'empty' in el:
        return 1
    if 'black_pawn' in el:
        return 'p'
    if 'black_bishop' in el:
        return 'b'
    if 'black_knight' in el:
        return 'n'
    if 'black_rook' in el:
        return 'r'
    if 'black_queen' in el:
        return 'q'
    if 'black_king' in el:
        return 'k'

    if 'white_pawn' in el:
        return 'P'
    if 'white_bishop' in el:
        return 'B'
    if 'white_knight' in el:
        return 'N'
    if 'white_rook' in el:
        return 'R'
    if 'white_queen' in el:
        return 'Q'
    if 'white_king' in el:
        return 'K'

    # print('This should never happen ', el)
    # assert 1 == 0
    return 1


def following_ones(row):
    new = []
    for i in range(len(row) - 1):
        if row[i] != 1:
            new.append(0)
            continue
        if i > 0:
            if row[i - 1] == 1:
                new.append(-1)
                continue
        counter = 0
        for j in range(i + 1, len(row)):
            if row[j] == 1:
                counter += 1
            else:
                break
        new.append(counter)
    if row[-1] == 1 and row[-2] in [1, 2, 3, 4, 5, 6, 7, 8]:
        new.append(-1)
    else:
        new.append(0)
    return new


def group_ones(row):
    fo = following_ones(row)
    for i in range(len(fo)):
        if row[i] == 1:
            row[i] += fo[i]
    while 0 in row:
        row.pop(row.index(0))

    return row


def getFEN(pos_txt):
    assert len(pos_txt) == 64

    rows = []
    for i in range(8):
        rows.append([])

    current = 0
    for piece in pos_txt:
        rows[current].append(piece)
        current += 1
        current = current % 8

    fem = []
    for row in rows:
        fem.append(list(map(fix_row, row)))

    rows = copy.deepcopy(fem)

    fem = list(map(group_ones, fem))

    finalFem = ''
    for arr in fem:
        for el in arr:
            finalFem = finalFem + str(el)
        finalFem = finalFem + '/'

    return finalFem[:-1], rows


def is_pawn_giving_a_check(rows, color):
    if color == 'w' or color == 'W':
        p = 'P'
        p_coos = []
        for i in range(len(rows)):
            for j in range(len(rows[0])):
                if rows[i][j] == p:
                    p_coos.append((i, j))
        if len(p_coos) == 0:
            return False

        for coo in p_coos:
            if coo[1] != 0:
                if rows[coo[0] - 1][coo[1] - 1] == 'k':
                    return True
            if coo[1] != 7:
                if rows[coo[0] - 1][coo[1] + 1] == 'k':
                    return True
        return False
    else:
        p = 'p'
        assert color == 'b' or color == 'B'
        p_coos = []
        for i in range(len(rows)):
            for j in range(len(rows[0])):
                if rows[i][j] == p:
                    p_coos.append((i, j))
        if len(p_coos) == 0:
            return False

        for coo in p_coos:
            if coo[1] != 0:
                if rows[coo[0] + 1][coo[1] - 1] == 'K':
                    return True
            if coo[1] != 7:
                if rows[coo[0] + 1][coo[1] + 1] == 'K':
                    return True
        return False


def find_king_coo(rows, kingcolor):
    if kingcolor == 'b' or kingcolor == 'B':
        k = 'k'
    else:
        k = 'K'
    for i in range(len(rows)):
        for j in range(len(rows[0])):
            if rows[i][j] == k:
                return i, j
    return 0, 0


def look_for(letter, possible_coos, rows):
    global zero2seven
    returning = []
    for coo in possible_coos:
        if coo[0] not in zero2seven or coo[1] not in zero2seven:
            continue
        if rows[coo[0]][coo[1]] == letter:
            returning.append((coo[0], coo[1]))

    if len(returning) > 0:
        return returning
    return None


def is_knight_giving_a_check(rows, color):
    global zero2seven
    if color == 'w' or color == 'W':
        black_king_coo = find_king_coo(rows, 'b')  # it must exist somewhere
        i = black_king_coo[0]
        j = black_king_coo[1]
        possible_knight_coos = [(i + 2, j + 1), (i - 2, j + 1), (i + 2, j - 1), (i - 2, j - 1), (i + 1, j + 2),
                                (i - 1, j + 2), (i + 1, j - 2), (i - 1, j - 2)]
        return False if look_for('N', possible_knight_coos, rows) is None else True

    else:
        white_king_coo = find_king_coo(rows, 'w')  # it must exist somewhere

        i = white_king_coo[0]
        j = white_king_coo[1]
        possible_knight_coos = [(i + 2, j + 1), (i - 2, j + 1), (i + 2, j - 1), (i - 2, j - 1), (i + 1, j + 2),
                                (i - 1, j + 2), (i + 1, j - 2), (i - 1, j - 2)]
        return False if look_for('n', possible_knight_coos, rows) is None else True


def is_rook_giving_a_check(rows, color, queencall=False):
    global zero2seven
    if color == 'w' or color == 'W':
        r = 'R'
        if queencall:
            r = 'Q'
        black_king_coo = find_king_coo(rows, 'b')  # it must exist somewhere
        i = black_king_coo[0]
        j = black_king_coo[1]

        possible_rook_coos = list(zip([i, i, i, i, i, i, i, i], zero2seven)) + list(
            zip(zero2seven, [j, j, j, j, j, j, j, j]))

        rook_coo = look_for(r, possible_rook_coos, rows)

        if rook_coo is None:
            return False

        row = rows[i][:]
        column = [row[j] for row in rows]  # rows[:][j]

        helper_arr = [row, column]

        for h in helper_arr:
            if r in h:
                Rs = [i for i, x in enumerate(h) if x == r]
                for R in Rs:
                    king_coo_here = h.index('k' if color == 'w' or color == 'W' else 'K')
                    if R < king_coo_here:
                        no_check = False
                        for tmp in range(R + 1, king_coo_here):
                            if h[tmp] != 1:
                                no_check = True
                        if not no_check:
                            return True
                    else:
                        no_check = False
                        for tmp in range(king_coo_here + 1, R):
                            if h[tmp] != 1:
                                no_check = True
                        if not no_check:
                            return True
        return False
    else:
        r = 'r'
        if queencall:
            r = 'q'
        black_king_coo = find_king_coo(rows, 'w')  # it must exist somewhere
        i = black_king_coo[0]
        j = black_king_coo[1]

        possible_rook_coos = list(zip([i, i, i, i, i, i, i, i], zero2seven)) + list(
            zip(zero2seven, [j, j, j, j, j, j, j, j]))

        rook_coo = look_for(r, possible_rook_coos, rows)
        if rook_coo is None:
            return False

        row = rows[i][:]
        column = [row[j] for row in rows]

        helper_arr = [row, column]

        for h in helper_arr:
            if r in h:
                Rs = [i for i, x in enumerate(h) if x == r]
                for R in Rs:
                    king_coo_here = h.index('k' if color == 'w' or color == 'W' else 'K')
                    if R < king_coo_here:
                        no_check = False
                        for tmp in range(R + 1, king_coo_here):
                            if h[tmp] != 1:
                                no_check = True
                        if not no_check:
                            return True
                    else:
                        no_check = False
                        for tmp in range(king_coo_here + 1, R):
                            if h[tmp] != 1:
                                no_check = True
                        if not no_check:
                            return True
        return False


def is_bishop_giving_a_check(rows, color, queencall=False):
    global zero2seven
    black_king_coo = (0, 0)
    if color == 'w' or color == 'W':
        r = 'B'
        if queencall:
            r = 'Q'
        black_king_coo = find_king_coo(rows, 'b')  # it must exist somewhere
    else:
        r = 'b'
        if queencall:
            r = 'q'
        black_king_coo = find_king_coo(rows, 'w')  # it must exist somewhere

    i = black_king_coo[0]
    j = black_king_coo[1]

    possible_bishop_coos = [
        (i + 1, j + 1),
        (i + 1, j - 1),
        (i - 1, j + 1),
        (i - 1, j - 1),

        (i + 2, j + 2),
        (i + 2, j - 2),
        (i - 2, j + 2),
        (i - 2, j - 2),

        (i + 3, j + 3),
        (i + 3, j - 3),
        (i - 3, j + 3),
        (i - 3, j - 3),

        (i + 4, j + 4),
        (i + 4, j - 4),
        (i - 4, j + 4),
        (i - 4, j - 4),

        (i + 5, j + 5),
        (i + 5, j - 5),
        (i - 5, j + 5),
        (i - 5, j - 5),

        (i + 6, j + 6),
        (i + 6, j - 6),
        (i - 6, j + 6),
        (i - 6, j - 6),

        (i + 7, j + 7),
        (i + 7, j - 7),
        (i - 7, j + 7),
        (i - 7, j - 7)
    ]

    bishop_coos = look_for(r, possible_bishop_coos, rows)
    if bishop_coos is None:
        return False

    for bishop_coo in bishop_coos:
        ib = bishop_coo[0]
        jb = bishop_coo[1]
        no_check = False
        if ib > i and jb > j:
            while ib != i:
                ib = ib - 1
                jb = jb - 1
                if rows[ib][jb] != 1 and ib != i:
                    no_check = True
                    break
            if not no_check:
                return True

        if ib < i and jb > j:
            while ib != i:
                ib = ib + 1
                jb = jb - 1
                if rows[ib][jb] != 1 and ib != i:
                    no_check = True
                    break
            if not no_check:
                return True

        if ib < i and jb < j:
            while ib != i:
                ib = ib + 1
                jb = jb + 1
                if rows[ib][jb] != 1 and ib != i:
                    no_check = True
                    break
            if not no_check:
                return True

        if ib > i and jb < j:
            while ib != i:
                ib = ib - 1
                jb = jb + 1
                if rows[ib][jb] != 1 and ib != i:
                    no_check = True
                    break
            if not no_check:
                return True
    return False


def is_queen_giving_a_check(rows, color):
    if is_rook_giving_a_check(rows, color, True):
        return True
    if is_bishop_giving_a_check(rows, color, True):
        return True
    return False


def is_king_giving_a_check(rows, color):
    our_king = 'K'
    opposing_king = 'k'
    if color == 'b':
        our_king, opposing_king = opposing_king, our_king

    our_i = 0
    our_j = 0
    opp_i = 0
    opp_j = 0
    for i in range(len(rows)):
        for j in range(len(rows[0])):
            if rows[i][j] == our_king:
                our_i = i
                our_j = j
            if rows[i][j] == opposing_king:
                opp_i = i
                opp_j = j
    if abs(our_i - opp_i) <= 1 and abs(our_j - opp_j) <= 1:
        return True
    return False


def is_giving_a_check(rows, color):
    if is_pawn_giving_a_check(rows, color):
        # print(color + ' ' + ' pawn is giving check')
        return True
    if is_bishop_giving_a_check(rows, color):
        # print(color + ' ' + ' bishop is giving check')
        return True
    if is_knight_giving_a_check(rows, color):
        # print(color + ' ' + ' knight is giving check')
        return True
    if is_rook_giving_a_check(rows, color):
        # print(color + ' ' + ' rook is giving check')
        return True
    if is_queen_giving_a_check(rows, color):
        # print(color + ' ' + ' queen is giving check')
        return True

    if is_king_giving_a_check(rows, color):
        return True

    return False


def who_is_giving_a_check(rows):
    if is_giving_a_check(rows, color='w'):
        return 'W'
    if is_giving_a_check(rows, color='b'):
        return 'B'
    return '-'


def get_check_arr(color):
    check_arr = []
    if color == 'w':
        check_arr += [1, 'p', 'n', 'b', 'q', 'r', 'k']
    else:
        check_arr += [1, 'P', 'N', 'B', 'Q', 'R', 'K']
    return check_arr


def get_new_boards(board, new_coos, i, j):
    new_boards = []
    for new_coo in new_coos:
        tmp_board = copy.deepcopy(board)
        tmp_board[i][j] = 1
        tmp_board[new_coo[0]][new_coo[1]] = board[i][j]
        new_boards.append(tmp_board)

    return new_boards


def is_knight_move_legal(board, color, new_i, new_j):
    if board[new_i][new_j] == 1:
        return True

    check_arr = get_check_arr(color)

    if board[new_i][new_j] in check_arr:
        return True
    return False


def knight_next_move(board, color, i, j):
    global zero2seven

    possible_knight_coos = [(i + 2, j + 1), (i - 2, j + 1), (i + 2, j - 1), (i - 2, j - 1), (i + 1, j + 2),
                            (i - 1, j + 2), (i + 1, j - 2), (i - 1, j - 2)]
    new_coos = []
    for coo in possible_knight_coos:
        if coo[0] in zero2seven and coo[1] in zero2seven:
            if is_knight_move_legal(board, color, coo[0], coo[1]):
                new_coos.append(coo)
    return get_new_boards(board, new_coos, i, j)


def is_bishop_move_legal(board, color, i, j, new_i_coo, new_j_coo):
    new_i = new_i_coo
    new_j = new_j_coo

    check_arr = get_check_arr(color)

    something_on_the_way = False
    if new_i > i and new_j > j:
        while new_i != i:
            i = i + 1
            j = j + 1
            if board[i][j] != 1 and i != new_i:
                return False
        if board[new_i][new_j] in check_arr:
            return True
        return False
    if new_i < i and new_j > j:
        while new_i != i:
            i = i - 1
            j = j + 1
            if board[i][i] != 1 and new_i != i:
                return False
        if board[new_i][new_j] in check_arr:
            return True
        return False

    if new_i < i and new_j < j:
        while new_i != i:
            i = i - 1
            j = j - 1
            if board[i][j] != 1 and new_i != i:
                return False
        if board[new_i][new_j] in check_arr:
            return True
        return False

    if new_i > i and new_j < j:
        while new_i != i:
            i = i + 1
            j = j - 1
            if board[i][j] != 1 and new_i != i:
                return False
        if board[new_i][new_j] in check_arr:
            return True
        return False
    return False


def bishop_next_move(board, color, i, j):
    global zero2seven

    possible_bishop_coos = [
        (i + 1, j + 1),
        (i + 1, j - 1),
        (i - 1, j + 1),
        (i - 1, j - 1),

        (i + 2, j + 2),
        (i + 2, j - 2),
        (i - 2, j + 2),
        (i - 2, j - 2),

        (i + 3, j + 3),
        (i + 3, j - 3),
        (i - 3, j + 3),
        (i - 3, j - 3),

        (i + 4, j + 4),
        (i + 4, j - 4),
        (i - 4, j + 4),
        (i - 4, j - 4),

        (i + 5, j + 5),
        (i + 5, j - 5),
        (i - 5, j + 5),
        (i - 5, j - 5),

        (i + 6, j + 6),
        (i + 6, j - 6),
        (i - 6, j + 6),
        (i - 6, j - 6),

        (i + 7, j + 7),
        (i + 7, j - 7),
        (i - 7, j + 7),
        (i - 7, j - 7)
    ]

    new_coos = []
    for coo in possible_bishop_coos:
        if coo[0] in zero2seven and coo[1] in zero2seven:
            if is_bishop_move_legal(board, color, i, j, coo[0], coo[1]):
                new_coos.append(coo)

    return get_new_boards(board, new_coos, i, j)


def is_rook_move_legal(board, color, i, j, new_i_org, new_j_org):
    check_arr = get_check_arr(color)
    new_i = new_i_org
    new_j = new_j_org

    if i > new_i:
        i, new_i = new_i, i

    if j > new_j:
        j, new_j = new_j, j

    something_in_the_way = False

    if j == new_j:
        for curr_i in range(i + 1, new_i):
            if board[curr_i][j] != 1:
                return False

        if not something_in_the_way:
            if board[new_i_org][new_j_org] in check_arr:
                return True
            return False

    elif i == new_i:
        for curr_j in range(j + 1, new_j):
            if board[i][curr_j] != 1:
                return False

        if not something_in_the_way:
            if board[new_i_org][new_j_org] in check_arr:
                return True
            return False
    else:
        return False


def rook_next_move(board, color, i, j):
    global zero2seven

    possible_rook_coos = list(zip([i, i, i, i, i, i, i, i], zero2seven)) + list(
        zip(zero2seven, [j, j, j, j, j, j, j, j]))

    new_coos = []
    for coo in possible_rook_coos:
        if coo[0] in zero2seven and coo[1] in zero2seven:
            if is_rook_move_legal(board, color, i, j, coo[0], coo[1]):
                new_coos.append(coo)
    return get_new_boards(board, new_coos, i, j)


def is_queen_move_legal(board, color, i, j, new_i, new_j):
    if i == new_i or new_j == j:
        return is_rook_move_legal(board, color, i, j, new_i, new_j)
    return is_bishop_move_legal(board, color, i, j, new_i, new_j)


def queen_next_move(board, color, i, j):
    global zero2seven

    possible_queen_coos = list(zip([i, i, i, i, i, i, i, i], zero2seven)) + list(
        zip(zero2seven, [j, j, j, j, j, j, j, j]))
    possible_queen_coos += [
        (i + 1, j + 1),
        (i + 1, j - 1),
        (i - 1, j + 1),
        (i - 1, j - 1),

        (i + 2, j + 2),
        (i + 2, j - 2),
        (i - 2, j + 2),
        (i - 2, j - 2),

        (i + 3, j + 3),
        (i + 3, j - 3),
        (i - 3, j + 3),
        (i - 3, j - 3),

        (i + 4, j + 4),
        (i + 4, j - 4),
        (i - 4, j + 4),
        (i - 4, j - 4),

        (i + 5, j + 5),
        (i + 5, j - 5),
        (i - 5, j + 5),
        (i - 5, j - 5),

        (i + 6, j + 6),
        (i + 6, j - 6),
        (i - 6, j + 6),
        (i - 6, j - 6),

        (i + 7, j + 7),
        (i + 7, j - 7),
        (i - 7, j + 7),
        (i - 7, j - 7)
    ]

    new_coos = []
    for coo in possible_queen_coos:
        if coo[0] in zero2seven and coo[1] in zero2seven:
            if is_queen_move_legal(board, color, i, j, coo[0], coo[1]):
                new_coos.append(coo)
    return get_new_boards(board, new_coos, i, j)


def is_pawn_move_legal(board, new_i, new_j):
    if board[new_i][new_j] == 1:
        return True
    return False


def white_pawn_next_move(board, color, i, j):
    global zero2seven

    possible_pawn_coos = []
    if i == 6:
        possible_pawn_coos.append((i - 2, j))
    possible_pawn_coos.append((i - 1, j))

    new_coos = []
    for coo in possible_pawn_coos:
        if coo[0] in zero2seven and coo[1] in zero2seven:
            if is_pawn_move_legal(board, coo[0], coo[1]):
                new_coos.append(coo)

    check_arr = ['p', 'b', 'n', 'r', 'q', 'k']
    if board[i - 1][j - 1] in check_arr:
        new_coos.append((i - 1, j - 1))
    if board[i - 1][j + 1] in check_arr:
        new_coos.append((i - 1, j + 1))

    return get_new_boards(board, new_coos, i, j)


def black_pawn_next_move(board, color, i, j):
    global zero2seven

    possible_pawn_coos = []
    if i == 1:
        possible_pawn_coos.append((i + 2, j))
    possible_pawn_coos.append((i + 1, j))

    new_coos = []
    for coo in possible_pawn_coos:
        if coo[0] in zero2seven and coo[1] in zero2seven:
            if is_pawn_move_legal(board, coo[0], coo[1]):
                new_coos.append(coo)

    check_arr = ['P', 'B', 'N', 'R', 'Q', 'K']
    if board[i + 1][j - 1] in check_arr:
        new_coos.append((i - 1, j - 1))
    if board[i + 1][j + 1] in check_arr:
        new_coos.append((i - 1, j + 1))

    return get_new_boards(board, new_coos, i, j)


def is_king_move_legal(board, color, i, j):
    check_arr = get_check_arr(color)
    if board[i][j] in check_arr:
        return True
    return False


def king_next_move(board, color, i, j):
    possible = [
        (i, j + 1),
        (i, j - 1),
        (i + 1, j + 1),
        (i + 1, j - 1),
        (i - 1, j + 1),
        (i - 1, j - 1),
        (i + 1, j),
        (i - 1, j)
    ]
    new_coos = []
    for coo in possible:
        if coo[0] in zero2seven and coo[1] in zero2seven:
            if is_king_move_legal(board, color, coo[0], coo[1]):
                new_coos.append(coo)

    return get_new_boards(board, new_coos, i, j)


def next_moves_white(board):
    # print('stigao do ovde, evo tabla')
    # for b in board:
    #     print(b)
    # exit()
    check_arr = ['P', 'B', 'N', 'R', 'Q', 'K']
    functions_array = [white_pawn_next_move, bishop_next_move, knight_next_move, rook_next_move, queen_next_move,
                       king_next_move]

    all_new_boards = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] in check_arr:
                all_new_boards = all_new_boards + functions_array[check_arr.index(board[i][j])](board, 'w', i, j)

    return all_new_boards


def next_moves_black(board):
    check_arr = ['p', 'b', 'n', 'r', 'q', 'k']
    functions_array = [black_pawn_next_move, bishop_next_move, knight_next_move, rook_next_move, queen_next_move,
                       king_next_move]

    all_new_boards = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] in check_arr:
                all_new_boards = all_new_boards + functions_array[check_arr.index(board[i][j])](board, 'b', i, j)

    return all_new_boards


def all_possible_next_moves(board, who):
    if who == 'w' or who == 'W':
        on_move = 'b'
    elif who == 'b' or who == 'B':
        on_move = 'w'
    else:
        print('This should never happen!')
        return []

    if on_move == 'b':
        return next_moves_black(board)
    else:
        return next_moves_white(board)


def is_it_a_mate(board, who):
    if who == '-':
        return 0

    all_possible_boards = all_possible_next_moves(board, who)

    for next_board in all_possible_boards:
        if not is_giving_a_check(next_board, who):
            return 0
    return 1


def main():
    folder_path = input()
    image_name = folder_path.replace('\\', '/').split('/')[-1] + '.png'
    im, board_coo = first_part(folder_path + '\\' + image_name)

    position = divide_board(im, board_coo)

    preprocess_pieces_and_tiles(folder_path)

    position_text = recognize_position(position)

    fen, rows = getFEN(position_text)

    who = who_is_giving_a_check(rows)

    is_it_mate = is_it_a_mate(rows, who=who)

    print(str(board_coo[1]) + ',' + str(board_coo[0]))
    print(fen)
    print(who)
    print(is_it_mate)


if __name__ == '__main__':
    main()
