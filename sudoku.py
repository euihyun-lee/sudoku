XY_CELL_MAP = [[0, 0, 0, 1, 1, 1, 2, 2, 2],
               [0, 0, 0, 1, 1, 1, 2, 2, 2],
               [0, 0, 0, 1, 1, 1, 2, 2, 2],
               [3, 3, 3, 4, 4, 4, 5, 5, 5],
               [3, 3, 3, 4, 4, 4, 5, 5, 5],
               [3, 3, 3, 4, 4, 4, 5, 5, 5],
               [6, 6, 6, 7, 7, 7, 8, 8, 8],
               [6, 6, 6, 7, 7, 7, 8, 8, 8],
               [6, 6, 6, 7, 7, 7, 8, 8, 8]]


class Cell:
    # STATE_TRIVIAL = 0 ~ 8
    STATE_NON_TRIVIAL = -1
    STATE_NON_BLANK = -2
    STATE_IMPOSSIBLE = -3

    def __init__(self, capacity_hori, capacity_vert, capacity_cell):
        self.capacity_hori = capacity_hori
        self.capacity_vert = capacity_vert
        self.capacity_cell = capacity_cell
        self.value = -1  # -1: blank, 0~8: filled
        self.state = Cell.STATE_NON_TRIVIAL
        self.candidates = [True for _ in range(9)]

    def set(self, value):
        if value >= 0:
            if not self.candidates[value]:
                return False

        if not self.is_blank:
            self.capacity_hori[self.value] = False
            self.capacity_vert[self.value] = False
            self.capacity_cell[self.value] = False

        if value >= 0:
            self.capacity_hori[value] = True
            self.capacity_vert[value] = True
            self.capacity_cell[value] = True
        
        self.value = value
        assert self.update_state() == Cell.STATE_NON_BLANK or self.value < 0
        return True

    @property
    def is_blank(self):
        return self.value < 0

    def update_state(self):
        # update candidates
        self.candidates = [not (hori or vert or cell)
                           for hori, vert, cell
                           in zip(self.capacity_hori,
                                  self.capacity_vert,
                                  self.capacity_cell)]
        if not self.is_blank:
            self.state = Cell.STATE_NON_BLANK
        elif self.candidates.count(True) == 0:
            self.state = Cell.STATE_IMPOSSIBLE
        elif self.candidates.count(True) == 1:
            self.state = self.candidates.index(True)
        else:
            self.state = Cell.STATE_NON_TRIVIAL
        return self.state

    def __str__(self):
        return str(self.value + 1) if self.value >= 0 else ' '


class Sudoku:
    def __init__(self, board):
        self.init_board()
        self.set_board(board)

    def init_board(self):
        self.capacity_hori_list = [[False for _ in range(9)] for _ in range(9)]
        self.capacity_vert_list = [[False for _ in range(9)] for _ in range(9)]
        self.capacity_cell_list = [[False for _ in range(9)] for _ in range(9)]
        self.board = [[Cell(self.capacity_hori_list[i],
                            self.capacity_vert_list[j],
                            self.capacity_cell_list[XY_CELL_MAP[i][j]])
                       for j in range(9)] for i in range(9)]

    def set_board(self, board):
        for i, row in enumerate(board):
            for j, value in enumerate(row):
                assert self.set(i, j, value)
        assert self.update_state()

    def get(self, i, j):
        return self.board[i][j].value + 1

    def set(self, i, j, value):
        old_value = self.get(i, j)
        success = self.board[i][j].set(value - 1)
        if success:
            if not self.update_state():
                self.set(i, j, old_value)
                success = False
        return success


    def is_done(self):
        for row in self.board:
            for cell in row:
                if cell.is_blank:
                    return False
        return True

    def print_board(self):
        for row in self.board:
            print(' '.join([str(cell) for cell in row]))
        print()

    def solve(self):
        def revoke_changes(mask):
            for i, row in enumerate(self.board):
                for j, cell in enumerate(row):
                    if not mask[i][j]:
                        continue
                    cell.set(-1)
            assert self.update_state()

        assert self.update_state()
        
        # fill trivials
        filled = True
        filled_mask = [[False for _ in range(9)] for _ in range(9)]
        while filled:
            filled = False
            for i, row in enumerate(self.board):
                for j, cell in enumerate(row):
                    if cell.state >= 0: # TRIVIAL
                        assert cell.set(cell.state)
                        filled = True
                        filled_mask[i][j] = True
                        if not self.update_state():
                            revoke_changes(filled_mask)
                            return False

        if self.is_done():
            print("ANSWER:")
            self.print_board()
            input()
            exit(0)
        self.print_board()

        # fill non-trivials
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell.state == Cell.STATE_NON_TRIVIAL:
                    original_candidates = cell.candidates[:]
                    for cand, is_cand in enumerate(original_candidates):
                        if not is_cand:
                            continue
                        if cell.set(cand):
                            if not self.update_state():
                                cell.set(-1)
                                assert self.update_state()
                                continue

                            if self.is_done():
                                print("ANSWER:")
                                self.print_board()
                                input()
                                exit(0)

                            self.print_board()
                            self.solve()
                            cell.set(-1)
                            assert self.update_state()

                    revoke_changes(filled_mask)
                    return False

        # should not reach here
        revoke_changes(filled_mask)
        return False

    def update_state(self):
        is_valid = True
        for row in self.board:
            for cell in row:
                 state = cell.update_state()
                 if state == Cell.STATE_IMPOSSIBLE:
                     is_valid = False
        return is_valid


if __name__ == "__main__":
    board = [[9, 0, 3, 8, 0, 0, 0, 7, 0],
             [7, 0, 0, 5, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 2, 0, 0, 0, 0],
             [5, 2, 0, 0, 4, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 6, 0, 8, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 7, 0, 0, 5, 0, 0],
             [0, 6, 0, 0, 0, 0, 4, 0, 0],
             [0, 0, 0, 0, 0, 8, 0, 0, 0]]
    sdk = Sudoku(board)
    sdk.print_board()

    sdk.solve()
