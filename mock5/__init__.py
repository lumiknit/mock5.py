#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mock5

Author: lumiknit (aasr4r4@gmail.com)

Simple Omok (five-in-a-row) game for RL with numpy/torch.

The main part of this module is the class `Mock5`.
See `help(Mock5)`

Example:
  # For playing game with to user, run this script such as:
  ./mock5.py
  # or
  ./mock5.py <board_height> <board_width>

  # or read `example_of_Mock5` (at the bottom of mock5.py).
"""

__all__ = ['Mock5']
__version__ = '0.0.1'

#-- Constants

# Stone color
EMPTY = 0
BLACK = 1
WHITE = 2

# Stone color to displayed character
_STONE_CHAR = ['.', 'O', 'X']

#-- Helpers

def _digit_to_int(s, offset=0):
  """Digit-to-integer converter
  
  Take a char in /0-9a-zA-Z/ return the integer.

  Returns:
    int | None: 0-9 for char in /0-9/ 10-35 for char in /A-Za-z/, else None
  """
  v = ord(s[offset])
  if 48 <= v and v < 48 + 10: return v - 48
  elif 65 <= v and v < 65 + 26: return v - 65 + 10
  elif 97 <= v and v < 97 + 26: return v - 97 + 10
  else: return None

def _int_to_digit(v):
  """Digit-to-integer converter
  
  Take an integer between 0 and 35, return /0-9A-Z/

  Returns:
    str | None: /0-9/ for 0-9, /A-Z/ for 10-35, else None
  """
  if 0 <= v and v < 10: return chr(48 + v)
  elif 10 <= v and v < 10 + 26: return chr(65 + v - 10)
  else: return None

#-- Game class

class Mock5:
  """ Omok Game Class

  This class provides methods to
  * Create a board (__init__)
  * Pretty print (__str__)
  * Provide indexing by row-column (__getitem__, __setitem__)
  * Duplicate and rotate/flip a board (duplicate, replay, rotate_ccw, etc.)
  * Make an iterater of indices (iter_row/column/right_down/left_down)
  * Get first (row,col) of iterator (first_of_row/column/right_down/left_down)
  * Extract a line of board (slice_row/column/right_down/left_down)
  * "Action" i.e. placing a stone (can_place_at, place_stone)
  * History for backtrack (undo)
  * Simple analysis to check game is finished (check_win)
  * Generate empty-or-not array (empty_array, empty_numpy, empty_tensor)
  * And, convert board into numpy.array and torch.tensor (numpy, tensor)

  Note that each cells of `board` contains 0 (empty), 1 (black) or 2 (white).
  Also, each of 1 and 2 stand for player 1 and player 2.

  Attributes:
    height (int): Height of board
    width (int): Width of board
    board (int[height * width]):
      1-D list of status of each cells on board.
      To index `(row, col)`, you should index as `board[row * width + col]`
    history (int[]):
      1-D list of stone placing history.
      It contains an index of board, not (row, col).
      In default settings, 1P=black player must place the first stone.
      Thus, you can consider that odd index = black stone and even = white.
    player (1 | 2): Index of player who should place stone now
  """

  # Constructor
  def __init__(self, height=15, width=15, board=None, history=None):
    """ Constructor

    Args:
      height (int): Height of board (1~36)
      width (int): Width of board (1~36)
      board (int[height * width]?):
        If it's not None, it'll copy all board contents.
      history (int[]?):
        If it's not None, it'll put stones following history.

    Note:
      If both of board and history is non-None, it duplicate board first,
      and then follows history.
    """
    if (type(height) is not int) or (type(width) is not int):
      raise TypeError
    if height <= 0 or height > 36 or width <= 0 or width > 36:
      raise Exception("Mock5 board size should be between 1 and 36!")
    # Board informations
    self.height = height
    self.width = width
    if board is not None:
      # If board is given, duplicate it.
      if len(board) != height * width:
        raise ValueError
      self.board = list(board)
    else:
      self.board = [0] * (self.height * self.width)
    # Turn informations
    self.player = 1
    self.history = []
    # Place stones
    if history is not None:
      for idx in history:
        r, c = self._expand_index(idx)
        self.place_stone(r, c)

  # Pretty-printed board
  def __str__(self):
    """ ToString

    Returns: (A string in the below format:)
      =====================================
       [ Turn XXX ; 1P's turn (tone = O) ]
        | 0 1 2 3
      --+--------
      0 | . . O .
      1 | . X . .
      2 | . O . X
    """
    r = "====================================="
    r += "\n [ Turn {:3d} ; {}P's turn (tone = {}) ]" \
        .format(len(self.history), self.player, _STONE_CHAR[self.player])
    r += "\n  |"
    for i in range(self.width): r += " {}".format(_int_to_digit(i))
    r += "\n--+"
    for i in range(self.width): r += "--"
    for i in range(self.height):
      r += "\n{} |".format(_int_to_digit(i))
      for j in range(self.width):
        r += " {}".format(_STONE_CHAR[self.board[i * self.width + j]])
    return r

  # Indexing

  def _reduce_index(self, r, c):
    """
    Encode (row, col) into (row + width + col)
    """
    return r * self.width + c

  def _expand_index(self, idx):
    """
    Decode (row + width + col) into (row, col)
    """
    return (idx // self.width, idx % self.width)

  def _check_key(self, key):
    """
    Check key is valid (row, col) tuple
    """
    if (type(key) is not tuple) or len(key) != 2: raise TypeError
    if (type(key[0]) is not int) or (type(key[1]) is not int): raise TypeError
    if key[0] < 0 or key[0] >= self.height: raise IndexError
    if key[1] < 0 or key[1] >= self.width: raise IndexError

  def __getitem__(self, key):
    """ Index

    Args:
      key ((int, int)): (row, column) pair

    Returns:
      0|1|2: Cell of board at (row, column)

    Raises:
      TypeError: Type of key is not (int, int)
      IndexError: row or column is out of range

    Examples:
      g = Mock5()
      g[3, 2]  # 4-th row, 3-rd column (because of 0-based indexing)
    """
    self._check_key(key)
    return self.board[self._reduce_index(key[0], key[1])]

  def __setitem__(self, key, value):
    """ Index and Change Value

    Args:
      key ((int, int)): (row, column) pair
      value (int): 0 (empty), 1 (black) or 2 (white)

    Raises:
      TypeError: Type of key is not (int, int)
      IndexError: row or column is out of range

    Examples:
      g = Mock5()
      g[3, 2] = 1  # 4-th row, 3-rd column (because of 0-based indexing)
    """
    self._check_key(key)
    if (type(value) is not int) or value < 0 or value > 2:
      raise TypeError
    self.board[self._reduce_index(key[0], key[1])] = value

  # Duplicate

  def duplicate(self):
    """ Duplicate Board

    Make a duplicate of board.
    It DOES NOT preserve history.
    """
    return self.__class__(self.height, self.width, board=self.board)

  def replay(self, angle=0, flip=0):
    """ Duplicate Board by History

    Make a replay of history.
    It duplicate a game board following by history.

    Args:
      angle (int): Rotation angle. 0, 1, 2 or 3
      flip (int): Flip. 1 is flip, 0 is not.
    """
    if angle == 0 and flip == 0:
      return self.__class__(self.height, self.width, history=self.history)
    l = len(self.history)
    h = [0] * l
    for i in range(l):
      r, c = self.history[i] // self.width, self.history[i] % self.width
      mw = self.width - 1
      mh = self.height - 1
      if flip % 2 == 1: c = mw - c
      if angle % 4 == 0: h[i] = r * self.width + c
      if angle % 4 == 1: h[i] = (mw - c) * self.height + r
      elif angle % 4 == 2: h[i] = (mh - r) * self.width + (mw - c)
      elif angle % 4 == 3: h[i] = c * self.height + (mh - r)
    if angle % 2 == 1:
      return self.__class__(self.width, self.height, history=h)
    else:
      return self.__class__(self.height, self.width, history=h)

  # History-based Duplicate Method with D4-Group Operations
  
  def rotate_ccw(self):
    """ Rotate Board CCW
    
    Create a new board, which is rotated 90 deg CCW of original board.
    """
    def rotate_idx(idx):
      r, c = self._expand_index(idx)
      c = self.width - c - 1
      return c * self.height + r
    new_history = list(map(rotate_idx, self.history))
    return self.__class__(self.width, self.height, history=new_history)

  def flip_vertical(self):
    """ Flip Board Vertically
    
    Create a new board, which is flipped up and down of original board.
    """
    def flip_idx(idx):
      r, c = self._expand_index(idx)
      r = self.height - r - 1
      return r * self.width + c
    new_history = list(map(flip_idx, self.history))
    return self.__class__(self.height, self.width, history=new_history)

  #-- Index Iterator

  class _IndexIter:
    """ Index Iterator
    
    Iterate from (sr, sc) increasing by (dr, dc).
    It returns (row, column)

    IT MAY OCCUR INF LOOP. DO NOT USE THIS.
    """
    def __init__(self, game, sr, sc, dr, dc):
      if dr == 0 and dc == 0: raise ValueError
      self.game = game
      self.r = sr
      self.c = sc
      self.dr = dr
      self.dc = dc
      if dr >= 0: self.br = self.game.height
      else: self.br = -1
      if dc >= 0: self.bc = self.game.width
      else: self.bc = -1

    def __iter__(self): return self

    def __next__(self):
      if self.r == self.br or self.c == self.bc:
        raise StopIteration
      else:
        ret = (self.r, self.c)
        self.r += self.dr
        self.c += self.dc
        return ret

  def first_of_row(self, idx):
    """ First element's (row, colun) of idx-th row
    """
    if idx < 0 or idx >= self.height: raise IndexError
    return (idx, 0)

  def first_of_column(self, idx):
    """ First element's (row, colun) of idx-th column
    """
    if idx < 0 or idx >= self.width: raise IndexError
    return (0, idx)

  def first_of_right_down(self, idx):
    """ First element's (row, colun) of idx-th right-down diagonal
    """
    r, c = 0, 0
    if idx < 0: raise IndexError
    elif idx < self.height: r = self.height - idx - 1
    elif idx < self.width + self.height - 1: c = idx - self.height + 1
    else: raise IndexError
    return (r, c)

  def first_of_left_down(self, idx):
    """ First element's (row, colun) of idx-th left-down diagonal
    """
    r, c = 0, self.width - 1
    if idx < 0: raise IndexError
    elif idx < self.width: c = idx
    elif idx < self.width + self.height - 1: r = idx - self.width + 1
    else: raise IndexError
    return (r, c)

  def iter_row(self, idx):
    """ Index iterator for idx-th row
    
    Iterator each elements in idx-th row
    """
    r, c = self.first_of_row(idx)
    return self._IndexIter(self, r, c, 0, 1)

  def iter_column(self, idx):
    """ Index iterator for idx-th column
    
    Iterator each element in idx-th column
    """
    r, c = self.first_of_column(idx)
    return self._IndexIter(self, r, c, 1, 0)

  def iter_right_down(self, idx):
    """ Index itererator right down diagonal
    
    Iterator each element following right down direction.
    Both of row and column increasing
    """
    r, c = self.first_of_right_down(idx)
    return self._IndexIter(self, r, c, 1, 1)

  def iter_left_down(self, idx):
    """ Index itererator rleft down diagonal
    
    Iterator each element following left down direction.
    Column decreases while row increasing
    """
    r, c = self.first_of_left_down(idx)
    return self._IndexIter(self, r, c, 1, -1)

  #-- Slice

  def slice_row(self, idx):
    """ Extrat row
    
    Make a idx-th row slice of board
    """
    return [self[r, c] for r, c in self.iter_row(idx)]

  def slice_column(self, idx):
    """ Extrat column
    
    Make a idx-th column slice of board
    """
    return [self[r, c] for r, c in self.iter_column(idx)]

  def slice_right_down(self, idx):
    """ Extrat right down diagonal
    
    Make a idx-th slice of board in right down direciton
    """
    return [self[r, c] for r, c in self.iter_right_down(idx)]
  
  def slice_left_down(self, idx):
    """ Extrat left down diagonal
    
    Make a idx-th slice of board in left down direciton
    """
    return [self[r, c] for r, c in self.iter_left_down(idx)]

  # Placing stone methods

  def can_place_at(self, r, c, player = None):
    """ Check player's Stone Can Be Placed
    
    Check player's stone can be placed at r row and c column.

    Args:
      r (int): Row index
      c (int): Column index
      player (int?): A stone's owner. If it's None, it'll be the current player

    Returns:
      bool: True iff placing at (r, c) does not violate any rules.
        Rules include
        - At most one stone on each cell
        - (TODO) In renju-settings, black cannot make double 3, double 4,
          and over 5 in a row.
    """
    if (type(r) is not int) or (type(c) is not int): raise TypeError
    if r < 0 or r >= self.height or c < 0 or c >= self.width: raise IndexError
    if player == None:
      player = self.player
    is_empty = (self[r, c] == 0)
    # TODO: For renju rule,
    # we prohibit to check double-3, double-4 and more-than-5-stones
    return is_empty

  def place_stone(self, r, c, player = None):
    """ Place a Stone at
    
    Place player's stone at r row c column.
    If you cannot place a stone at the point, it'll do nothing and return false
    Otherwise, it'll place a stone, pass the turn to opponent and return true

    Args:
      r (int): Row index
      c (int): Column index
      player (int?): A stone's owner. If it's None, it'll be the current player

    Returns:
      bool: True iff a stone is placed without violating any rules.
    """
    if not self.can_place_at(r, c, player): return False
    if player == None:
      player = self.player
      self.player = 3 - self.player
      self.history.append(self._reduce_index(r, c))
    self[r, c] = player
    return True

  def place_stone_at_index(self, idx, player = None):
    """ Place a Stone at the Index
    
    Place player's stone at idx = (row * width + col) index

    Args:
      idx (int): Value of (row * width + col)
      player (int?): A stone's owner. If it's None, it'll be the current player

    Returns:
      bool: True iff a stone is placed without violating any rules.
    """
    r, c = self._expand_index(idx)
    return self.place_stone(r, c, player)

  # History

  def history_depth(self):
    """ Depth of history
    Returns:
      int: The length of history of this game
    """
    return len(self.history)

  def undo(self):
    """ Undo

    Take the last move back.
    The last stone will be removed, and the last element of history erased.
    If no stones have benn placed, it'll do nothing.

    Returns:
      int: New length of history of this game
    """
    if len(self.history) > 0:
      idx = self.history.pop()
      if self.board[idx] != 3 - self.player:
        raise Exception("Board is corrupted!")
      self.board[idx] = 0
      self.player = 3 - self.player
    return len(self.history)

  def make_history_int_pair_array(self, winner=0):
    """ Make history into Array<Int, Int>

    Returns:
      list(int, int):
        [0]=winner, [1]=length
        [even]=stone position, [odd]=0
    """
    a = [winner, len(self.history)]
    for i in self.history:
      a.append(i)
      a.append(0)
    return a

  # Check game finished

  def _scan_with_iter(self, iter):
    """ Check 5 in a row in the direction of iter
    
    Return color if there are 5 stones of same colors.
    """
    cnt = 1
    p = self[iter.__next__()]
    for r, c in iter:
      cnt = cnt + 1 if self[r, c] == p else 1
      p = self[r, c]
      if cnt >= 5 and p > 0: return p
    return None

  def check_win(self):
    """ Check the Game is Finished

    Scan all board, and find out 5 stones in a row

    Note:
      If there are multiple 5 stones in a row, it'll choose one randomly.
      This case does not occur if you did not change a board arbitrarily,
      and run check_win for every turns to halt when game is finished.

    Returns:
      None | int:
        None if game is not finished
        1 | 2 if the player 1 or 2 wins
        0 if they draw
    """
    # Scan in 4 directions
    # Hori
    for x in range(self.height):
      v = self._scan_with_iter(self.iter_row(x))
      if v is not None:
        return v
    # Vert
    for x in range(self.width):
      v = self._scan_with_iter(self.iter_column(x))
      if v is not None:
        return v
    # Diagonal
    for x in range(self.height + self.width - 1):
      v = self._scan_with_iter(self.iter_right_down(x))
      if v is not None:
        return v
      v = self._scan_with_iter(self.iter_left_down(x))
      if v is not None:
        return v
    # Check draw
    if len(self.history) >= self.width * self.height:
      # Draw
      return 0
    # Not finished
    return None

  # Play game

  def play(self, input1=None, input2=None, random_first=True, \
      print_intermediate_state=True, \
      print_messages=True):
    """ Run a Game with Two Players

    Take two players and process game.

    Args:
      input1,2 ((Mock5) => (int, int)):
        A function take an argument `Mock5`, and return the index of row and
        column where stone to be placed.
        If the stone cannot be placed at (row, col), it'll be considered as
        cheat, and the player will lose.
        If it return (False, 0), it means 'GG'
        If it return (False, 1), it means 'UNDO'
        The two features only for testing.
        Default value is user input (using stdin).
      random_first (Bool?):
        If False, input1 plays with black stones, and input2 plays with white.
        Otherwise, stone colors are randomly chosen.
        Even if the colors are exchanged (1p=white, 2p=black),
        it'll return 1 if 1p win and return 2 if 2p win.
      print_intermediate_state (Bool):
        Print every intermediate state f it's True
      print_messages (Bool):
        Print messages if it's True

    Returns:
      int: 1 if input1 win, 2 if input2 win, 0 if they draw
    """
    def user_input(game):
      while True:
        v = input("row-col (e.g. 3a, 77) ; 'gg' ; 'undo' > ").strip()
        try:
          if v == 'gg': return False, 0
          elif v == 'undo': return False, 1
          v = [y for x in map(list, v.split()) for y in x]
          if len(v) != 2: raise Exception()
          r = _digit_to_int(v[0])
          c = _digit_to_int(v[1])
          if (r is None) or (c is None): raise Exception()
          if not self.can_place_at(r, c): raise IndexError()
          return r, c
        except IndexError:
          print("Cannot place stone at {}, {}!".format(v[0], v[1]))
        except Exception:
          print("Wrong input!")
        finally: pass
    user_input.name = "user"
    import random
    exchanged = False
    if random_first and random.random() < 0.5:
      exchanged = True
      input1, input2 = input2, input1
    if input1 is None: input1 = user_input
    if input2 is None: input2 = user_input
    pif = [None, input1, input2]
    def player_name(idx):
      if hasattr(pif[idx], "name"):
        return "{}p ({})".format(idx, pif[idx].name)
      else: return "{}p ({})".format(idx, pif[idx])
    winner = None
    while True:
      if print_intermediate_state:
        print(str(self))
      ret = pif[self.player](self)
      if ret is None: r, c = False, 0
      else: r, c = ret
      if (r is None) or (r is False):
        if c == 1:
          self.undo()
          self.undo()
        elif c == 0:
          if print_messages:
            print("{} give up!".format(player_name(self.player)))
          winner = 3 - self.player
          break
      else:
        if not self.place_stone(r, c):
          if print_messages:
            print("{} cheats! (try to place stone at {}, {})" \
                .format(player_name(self.player), r, c))
          winner = 3 - self.player
          break
      winner = self.check_win()
      if winner != None:
        if print_messages:
          print(str(self))
          if winner == 0: print("Draw!")
          else: print("{} win!".format(player_name(winner)))
        break
    if (winner is not None) and winner > 0 and exchanged:
      winner = 3 - winner
    return winner

  # Tensor helpers

  def _map_for_player(self, player=None):
    """
    Return m such that
      m = [0, 1, 2] if player = 1
      m = [0, 2, 1] if player = 2
    If m is mapped to board, the meaning of each cell value is changed:
      0 means empty
      1 means given player's stone
      2 means opponent's stone
    """
    if player == None: player = self.player
    return [0, player, 3 - player]

  def board_for(self, player=None):
    """
    Make a copy of board, which contains given player's stones as 1
    and opponent's stones as 2

    Args:
      player (int?):
        1 or 2 to specify player.
        Default value is current player.

    Returns:
      int[height * width]: Copy of board
    """
    m = self._map_for_player(player)
    return [m[x] for x in self.board]

  def one_hot_encoding(self, player=None):
    """
    Make an one hot encoding version of board.
    return[0] is marked by 1 iff the cell is empty,
    return[1] is marked by 1 iff there is the given player's stone
    return[2] is marked by 1 iff there is the opponent's stone

    Args:
      player (int?):
        1 or 2 to specify player.
        Default value is current player.

    Returns:
      int[3][height * width]: One hot encoding version board
    """
    m = self._map_for_player(player)
    a = [[0] * (self.height * self.width) for _ in range(3)]
    for i in range(self.height * self.width):
      a[m[self.board[i]]][i] = 1
    return a

  def numpy(self, player=None, one_hot_encoding=True, rank=None, dtype=None):
    """ numpy.array Conversion

    Convert self into numpy.array.
    Note that value/index 1 means the given player's stone.

    Args:
      player (int?):
        1 or 2 to specify player.
        Default value is current player.
      one_hot_encoding (bool):
        Make one hot encoding version if True,
        otherwise, make array filled with 0, 1, 2
        Default value is True
      rank (int): Rank of result array. See Returns.
      dtype (numpy.dtype):
        Element type of result array.
        Default value is numpy.float

    Returns:
      numpy.array(dtype=dtype): There are 5 variations of rank/dim
        one_hot_encoding & rank=3 => [3][height][width]   (default)
        one_hot_encoding & rank=2 => [3][height * width]
        one_hot_encoding & rank=1 => [3 * height * width]
        !one_hot_encoding & rank=2 => [height][width]
        !one_hot_encoding & rank=1 => [height * width]    (default)
    """
    import numpy as np
    if dtype is None: dtype = np.float
    if one_hot_encoding:
      a = self.one_hot_encoding(player=player)
      n = np.array(a, dtype=dtype)
      if rank == 1:
        n = n.reshape(-1)
      elif rank == 2: pass
      else:
        n = n.reshape(3, self.height, self.width)
      return n
    else:
      a = self.board_for(player=player)
      n = np.array(a)
      if rank == 2:
        n = n.reshape(self.width, self.height)
      return n

  def tensor(self, player=None, one_hot_encoding=True, rank=None, dtype=None):
    """ torch.tensor conversion

    Convert self into torch.tensor.
    Note that value/index 1 means the given player's stone.

    Note:
      This method may return a VIEW of tensor (when it's reshaped)

    Args:
      player (int?):
        1 or 2 to specify player.
        Default value is current player.
      one_hot_encoding (bool):
        Make one hot encoding version if True,
        otherwise, make array filled with 0, 1, 2
        Default value is True
      rank (int): Rank of result tensor. See Returns.
      dtype (torch.dtype):
        Element type of result tensor.
        Default value is torch.float

    Returns:
      torch.tensor(dtype=dtype): There are 5 variations of rank/dim
        one_hot_encoding & rank=3 => [3][height][width]   (default)
        one_hot_encoding & rank=2 => [3][height * width]
        one_hot_encoding & rank=1 => [3 * height * width]
        !one_hot_encoding & rank=2 => [height][width]
        !one_hot_encoding & rank=1 => [height * width]    (default)
    """
    import torch
    if dtype is None: dtype = torch.float
    if one_hot_encoding:
      a = self.one_hot_encoding(player=player)
      n = torch.tensor(a, dtype=dtype)
      if rank == 1:
        n = n.view(-1)
      elif rank == 2: pass
      else:
        n = n.view(3, self.height, self.width)
      return n
    else:
      a = self.board_for(player=player)
      n = torch.tensor(a)
      if rank == 2:
        n = n.view(self.width, self.height)
      return n

  def tensors_with_a_stone(
      self, player=None, one_hot_encoding=True, rank=None, dtype=None):
    """ torch.tensor conversion with placing a stone to each place

    Convert self into an array of torch.tensor.
    See `.tensor()` for more information about arguments and returns

    Returns:
      list(int): indices where stone is placed. (Not (row, col), but index)
      torch.tensor: See `.tensor()`
    """
    import torch
    if player is None: player = self.player
    Xs = []
    idxs = []
    for i in range(self.height * self.width):
      if self.place_stone_at_index(i):
        idxs.append(i)
        Xs.append(self.tensor(
          player=player, one_hot_encoding=one_hot_encoding,
          rank=rank, dtype=dtype
        ))
        self.undo()
    X = torch.stack(Xs)
    return idxs, X

  # Empty-or-not array

  def empty_array(self, empty=True, non_empty=False):
    """ Empty cell array

    Make an array, where each cell denote whether the board is empty or not.
    Default, array will be filled with True(empty)/False(non-empty)

    Args:
      empty (Any): Value to denote that cell is empty
      non_empty (Any): Value to denote that cell is not empty

    Returns:
      type(empty)[height * width]:
        [idx] equals to empty iff board[idx] == 0 (empty)
    """
    m = [empty, non_empty, non_empty]
    return [m[self.board[idx]] for idx in range(self.height * self.width)]

  def empty_numpy(self, rank=1, empty=1., non_empty=0., dtype=None):
    """ Numpy array of empty

    Make a numpy array,
    where each cell denote whether the board is empty or not.
    Default, array will be filled with 1.0(empty)/0.0(non-empty)

    Args:
      rank (1|2): See Returns
      empty (Any): Value to denote that cell is empty
      non_empty (Any): Value to denote that cell is not empty
      dtype (numpy.dtype?):
        dtype of numpy.array.
        In default, it follows the type of empty

    Returns:
      numpy.array(dtype=dtype): There are 2 variations of rank
        rank=1 => [height * width]   (default)
        rank=2 => [height][width]
    """
    import numpy as np
    if dtype is None: dtype = type(empty)
    em = self.empty_array(empty, non_empty)
    arr = np.array(em, dtype=dtype)
    if rank == 2:
      return arr.reshape(self.height, self.width)
    else:
      return arr

  def empty_tensor(self, rank=1, empty=True, non_empty=False, dtype=None):
    """ Torch tensor of empty

    Make a torch tensor,
    where each cell denote whether the board is empty or not.
    Default, array will be filled with True(empty)/False(non-empty)

    Note:
      This method may return a VIEW of tensor (when it's reshaped)

    Args:
      rank (1|2): See Returns
      empty (Any): Value to denote that cell is empty
      non_empty (Any): Value to denote that cell is not empty
      dtype (torch.dtype?):
        dtype of torch.tensor
        In default, it follows the type of empty

    Returns:
      torch.tensor(dtype=dtype): There are 2 variations of rank
        rank=1 => [height * width]   (default)
        rank=2 => [height][width]
    """
    import torch
    if dtype is None: dtype = type(empty)
    em = self.empty_array(empty, non_empty)
    tensor = torch.tensor(em, dtype=dtype)
    if rank == 2:
      return tensor.view(self.height, self.width)
    return tensor

  # Plot
  def plot(self):
    """ Plotting with matplotlib
    
    Plotting with matplotlib.
    To display, use `plt.show()` after calling it,
    to save as a file, use `plt.savefig(...)` after calling it.
    """
    import matplotlib.pyplot as plt
    fonts = [
      {'weight': 'bold', 'size': 20, 'color': 'white'},
      {'weight': 'bold', 'size': 20, 'color': 'black'},
    ]
    colors = ['black', 'white']
    plt.figure(figsize=(self.width, self.height))
    plt.axis('off')
    for i in range(1, self.height + 1):
      plt.plot([1, self.width], [i, i], zorder=1.0, c = '0.5')
    for i in range(1, self.width + 1):
      plt.plot([i, i], [1, self.height], zorder=1.0, c = '0.5')
    for i, p in enumerate(self.history):
      y = self.height - p // self.width
      x = 1 + p % self.width
      lbl = str(i + 1)
      fnt = fonts[i % 2]
      plt.gcf().gca().add_patch(
          plt.Circle(
            (x, y), 0.46, zorder=2.0,
            color=colors[i % 2], fill=True))
      plt.gcf().gca().add_patch(
          plt.Circle(
            (x, y), 0.46, zorder=2.0,
            color='black', fill=False))
      plt.text(
          x, y, lbl, zorder=3.0,
          ha='center', va='center', fontdict=fnt)

#-- Example

def example_of_Mock5():
  """ Example of Mock5 Usage
  """
  # Create default size board.
  game_1 = Mock5()
  # You can make your preferring size board.
  game_2 = Mock5(19, 19)
  # The first turn is for a black stone!
  # Place a stone at row=3, column=4
  game_2.place_stone(3, 4) # BLACK
  # Then, next turn is for a white tone!
  # Place a stone at row=6, column=2
  game_2.place_stone(6, 2) # WHITE
  # Note that every index is 0-based!
  # The first row is 0-th and the first column is 0-th too.
  game_2.place_stone(0, 0) # BLACK
  # `str` is useful to see the current state of game.
  pp = str(game_2)
  print(pp)
  # or, just `print(game_2)`
  # You cannot place stone over stone!
  # If you try it, `.place_stone` will do nothing and return False
  if not game_2.place_stone(3, 4):
    print("There was a stone at (3, 4)! You can't place a stone there.")
  # If you just want to check you can place a stone at some cell,
  # use `.can_place_at`
  print("Can place at (3, 4)? {}".format(game_2.can_place_at(3, 4)))
  print("Can place at (2, 10)? {}".format(game_2.can_place_at(2, 10)))
  # Mock5 manages history. You can undo.
  print("# Before UNDO:")
  print(game_2)
  l = game_2.undo()
  print("# {} histories left".format(l))
  print("# After UNDO:")
  print(game_2)
  # To find the game is finished (i.e. there is 5 stones in a row)
  # use `.check_win`!
  print("Win? {}".format(game_2.check_win()))
  # => None, it means game is not finished yet.
  game_2.place_stone(1, 10) # Player 2 = WHITE
  game_2.place_stone(1, 11) # Player 1 = BLACK
  game_2.place_stone(2, 10)
  game_2.place_stone(2, 11)
  game_2.place_stone(3, 10)
  game_2.place_stone(3, 11)
  game_2.place_stone(4, 10)
  game_2.place_stone(4, 11)
  game_2.place_stone(5, 10)
  print(game_2)
  print("Win? {}".format(game_2.check_win()))
  # => 2, it means the player 2 wins.
  game_3 = Mock5(3, 3)
  for i in range(9): game_3.place_stone_at_index(i) # Fill out board!
  print(game_3)
  print("Win? {}".format(game_3.check_win()))
  # => 0, it means there are no 5-in-a-row, and no empty cell.
  # Since nobody can place a stone, they draw.

  # If you make a loop and repeat 
  # - calculate next stone position checking place-ability
  # - place a stone
  # - check there is a winner, and choose halt or not
  # you have an Omok game!
  # However, this is too inconvinient.
  # In this case, you can use `.play`.
  # First, make an agent, which take a board, and give the position of
  # next stone.
  def stupid_player(game):
    # Find first empty
    for r in range(game.height): # Each row
      for c in range(game.width): # Each column
        if game[r, c] == 0: # Check empty
          return (r, c) # Return row, column
    return None # You can't do anything
  # Then, play with 2 of them
  winner = Mock5(4, 4).play(stupid_player, stupid_player)
  # winner is 0, 1, or 2. 0 implies draw, others implies the index of winner.
  # After machine learning process, you will want to test your agent.
  # Then make a wrapper such as:
  def model_wrapper(model):
    def player(game):
      i = torch.argmax(model(game.tensor()))
      return game._expand_index(i)
    return player 
  # And put `model_wrapper(model)` to `.play` method.
  # Also, if you do not specify player, you must play with STDIN.

  # You can take numpy.array or torch.tensor from Mock5.
  # game.numpy()
  # game.tensor()
  # game.empty_numpy()
  # game.empty_tensor()
  # More details in docstring of those method.
