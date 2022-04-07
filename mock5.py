#!/usr/bin/env python

# mock5.py
# Simple omok(five-in-a-row) game
# Author: lumiknit (aasr4r4@gmail.com)

# Stone color
EMPTY = 0
BLACK = 1
WHITE = 2
STONE_CHAR = ['.', 'O', 'X']

def digit_to_int(s, offset=0):
  v = ord(s[offset])
  if 48 <= v and v < 48 + 10: return v - 48
  elif 65 <= v and v < 65 + 26: return v - 65 + 10
  elif 97 <= v and v < 97 + 26: return v - 97 + 10
  else: return None

def int_to_digit(v):
  if 0 <= v and v < 10: return chr(48 + v)
  elif 10 <= v and v < 10 + 26: return chr(65 + v - 10)
  else: return None

class Mock5:
  # Constructor
  def __init__(self, height=15, width=15, board=None, history=None):
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
    r = "====================================="
    r += "\n [ Turn {:3d} ; {}P's turn (tone = {}) ]" \
        .format(len(self.history), self.player, STONE_CHAR[self.player])
    r += "\n  |"
    for i in range(self.width): r += " {}".format(int_to_digit(i))
    r += "\n--+"
    for i in range(self.width): r += "--"
    for i in range(self.height):
      r += "\n{} |".format(int_to_digit(i))
      for j in range(self.width):
        r += " {}".format(STONE_CHAR[self.board[i * self.width + j]])
    return r

  # Indexing
  # key must be `(row, column)``

  def _reduce_index(self, r, c):
    return r * self.width + c

  def _expand_index(self, idx):
    return (idx // self.width, idx % self.width)

  def _check_key(self, key):
    if (type(key) is not tuple) or len(key) != 2: raise TypeError
    if (type(key[0]) is not int) or (type(key[1]) is not int): raise TypeError
    if key[0] < 0 or key[0] >= self.height: raise IndexError
    if key[1] < 0 or key[1] >= self.width: raise IndexError

  def __getitem__(self, key):
    self._check_key(key)
    return self.board[self._reduce_index(key[0], key[1])]

  def __setitem__(self, key, value):
    self._check_key(key)
    if (type(value) is not int) or value < 0 or value > 2:
      raise TypeError
    self.board[self._reduce_index(key[0], key[1])] = value

  # Duplicate

  def duplicate(self):
    return self.__class__(self.height, self.width, board=self.board)

  def replay(self):
    return self.__class__(self.height, self.width, history=self.history)

  # History-based Duplicate Method with D4-Group Operations
  
  def rotate_ccw(self):
    def rotate_idx(idx):
      r, c = self._expand_index(idx)
      c = self.width - c - 1
      return c * self.height + r
    new_history = list(map(rotate_idx, self.history))
    return self.__class__(self.width, self.height, history=new_history)

  def flip_vertical(self):
    def flip_idx(idx):
      r, c = self._expand_index(idx)
      r = self.height - r - 1
      return r * self.width + c
    new_history = list(map(flip_idx, self.history))
    return self.__class__(self.height, self.width, history=new_history)

  # Placing stone methods

  def can_place_at(self, r, c, player = None):
    if (type(r) is not int) or (type(c) is not int): raise TypeError
    if r < 0 or r >= self.height or c < 0 or c >= self.width: raise IndexError
    if player == None:
      player = self.player
    is_empty = (self[r, c] == 0)
    # TODO: For renju rule,
    # we prohibit to check double-3, double-4 and more-than-5-stones
    return is_empty

  def place_stone(self, r, c, player = None):
    if not self.can_place_at(r, c, player): return False
    if player == None:
      player = self.player
      self.player = 3 - self.player
      self.history.append(self._reduce_index(r, c))
    self[r, c] = player
    return True

  def undo(self):
    if len(self.history) > 0:
      idx = self.history.pop()
      if self.board[idx] != 3 - self.player:
        raise Exception("Board is corrupted!")
      self.board[idx] = 0
      self.player = 3 - self.player

  # Check game finished

  def check_win(self):
    # If there is 5 in a row, return a winner index (1 or 2)
    # If they draw, return 0
    # Otherwise, return None

    # Scan in 4 directions
    # Hori
    for r in range(self.height):
      cnt = 1
      for c in range(1, self.width):
        cnt = cnt + 1 if self[r, c] == self[r, c - 1] else 1
        if cnt >= 5 and self[r, c] > 0: return self[r, c]
    # Vert
    for c in range(self.width):
      cnt = 1
      for r in range(1, self.height):
        cnt = cnt + 1 if self[r - 1, c] == self[r, c] else 1
        if cnt >= 5 and self[r, c] > 0: return self[r, c]
    # RightBottom Diagonal
    for d in range(self.width + self.height - 1):
      r, c = 0, 0
      if d < self.width: r, c = self.height - 1, d
      else: r, c = self.height - 1 - (d - self.width + 1), self.width - 1
      off, cnt = 1, 1
      while r - off >= 0 and c - off >= 0:
        cnt = cnt + 1 \
            if self[r - (off - 1), c - (off - 1)] == self[r - off, c - off] \
            else 1
        if cnt >= 5 and self[r - off, c - off] > 0:
          return self[r - off, c - off]
        off += 1
    # LeftBottom Diagonal
    for d in range(self.width + self.height - 1):
      r, c = 0, 0
      if d < self.height: r, c = d, 0
      else: r, c = self.height - 1, d - (self.height - 1)
      off, cnt = 1, 1
      while r - off >= 0 and c + off < self.width:
        cnt = cnt + 1 \
            if self[r - (off - 1), c + (off - 1)] == self[r - off, c + off] \
            else 1
        if cnt >= 5 and self[r - off, c + off] > 0:
          return self[r - off, c + off]
        off += 1
    if len(self.history) >= self.width * self.height:
      # Draw
      return 0
    # Not finished
    return None

  # Play game

  def play(self, input1=None, input2=None):
    # Input is a function take Mock5 and return row and column
    # Example of input: User input
    def user_input(game):
      while True:
        v = input("row-column (e.g. 3a) > ").strip()
        try:
          if v == 'gg': return False, 0
          elif v == 'undo': return False, 1
          v = [y for x in map(list, v.split()) for y in x]
          r = digit_to_int(v[0])
          c = digit_to_int(v[1])
          if (r is None) or (c is None): raise Exception()
          if not self.can_place_at(r, c): raise IndexError()
          return r, c
        except IndexError:
          print("Cannot place stone at {}, {}!".format(v[0], v[1]))
        except Exception:
          print("Wrong input!")
        finally: pass
    if input1 is None: input1 = user_input
    if input2 is None: input2 = user_input
    pif = [None, input1, input2]
    while True:
      print(str(self))
      r, c = pif[self.player](self)
      if r is False:
        if c == 1: self.undo()
        elif c == 0:
          print("Player {} give up!".format(self.player))
          return 3 - self.player
      else:
        if not self.place_stone(r, c):
          print("Player {} cheats! (try to place stone at {}, {})" \
              .format(self.player, r, c))
          return 3 - self.player
      w = self.check_win()
      if w != None:
        print(str(self))
        if w == 0: print("Draw!")
        else: print("Player {} win!".format(w))
        return w

  # Tensor helpers

  def _map_for_player(self, player=None):
    if player == None: player = self.player
    return [0, player, 3 - player]

  def board_for(self, player=None):
    m = self._map_for_player(player)
    return [m[x] for x in self.board]

  def one_hot_encoding(self, player=None):
    m = self._map_for_player(player)
    a = [[0] * (self.height * self.width) for _ in range(3)]
    for i in range(self.height * self.width):
      a[m[self.board[i]]][i] = 1
    return a

  def numpy(self, player=None, one_hot_encoding=True, rank=None, dtype=None):
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

class Mock5Analysis:
  def __init__(self, game):
    if type(game) is not Mock5: raise TypeError
    self.game = game
    self.run_analysis()

  def run_analysis(): pass

if __name__ == "__main__":
  g = Mock5()
  g.play()
