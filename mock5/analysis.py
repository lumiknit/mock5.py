#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mock5 analysis

Author: lumiknit (aasr4r4@gmail.com)

Analysis tool for Mock5.

The purpose of this module is:
  * Find game is finished
  * Find out double-3, double-4, 3-4, over-5-stones-in-a-row
"""

#-- Analysis class

def _sign(x):
  if x > 0: return 1
  elif x < 0: return -1
  else: return 0

N_OVER_5 = 7
N_5 = 6
N_OPEN_4 = 5
N_OPEN_3 = 4
N_4 = 3
N_3 = 2
N_2 = 1

B_OVER_5 = 0b1000000
B_5 = 0b100000
B_OPEN_4 = 0b10000
B_OPEN_3 = 0b1000
B_4 = 0b100
B_3 = 0b10
B_2 = 0b1

def B_str(bm):
  if bm & B_OVER_5: return ">5"
  elif bm & B_5: return "=5"
  elif bm & B_OPEN_4: return "+4"
  elif bm & B_4: return "4"
  elif bm & B_OPEN_3: return "+3"
  elif bm & B_3: return "3"
  elif bm & B_2: return "2"
  return "."

class Analysis:
  """ Omok Anlyzer

  It takes a game board Mock5 and anlayze the state:
  - (TODO) (semi-)opend 4 connections
  - (TODO) 3-3, 3-4, 4-4 after one move
  """
  def __init__(self, game):
    self.game = game
    self.sz = game.height * game.width
    self.result = [None,]
    for i in range(2):
      a = [[0] * self.sz for i in range(4)]
      self.result.append(a)
    self.run_analysis()

  def print_result(self, c, dir):
    r = "====================================="
    r += "\n Analaysis, Color {}, Dir {}".format(c, dir)
    r += "\n   |"
    for i in range(self.game.width): r += " {:2d}".format(i)
    r += "\n--+"
    for i in range(self.game.width): r += "--"
    for i in range(self.game.height):
      r += "\n{:2d} |".format(i)
      for j in range(self.game.width):
        if self.game[i, j] > 0:
          r += " {:>2}".format(
              'o' if self.game[i, j] == c else 'X')
        else:
          r += " {:>2}".format(
              B_str(self.result[c][dir][i * self.game.width + j]))
    print(r)

  def is_marked(self, color, dir, idx, bm):
    return 0 != (self.result[color][dir][idx] & bm)

  def mark(self, color, dir, idx, bm):
    self.result[color][dir][idx] |= bm

  class _Window:
    def __init__(self, an, dir):
      self.board = [3] * 7
      self.dir = dir
      self.idx = [None] * 7
      self.n_color = [0, 0, 0, 5]
      self.p = 0
      self.an = an

    def color_at(self, off):
      return self.board[(self.p + off) % 7]

    def push(self, color=3, idx=None):
      self.idx[self.p] = idx
      self.board[self.p] = color
      self.p = (self.p + 1) % 7
      self.n_color[self.color_at(0)] -= 1
      self.n_color[self.color_at(5)] += 1

    def mark(self, c, off, bm):
      return self.an.mark(c, self.dir, self.idx[(self.p + off) % 7], bm)

    def _check_5(self, c):
      # Find empty idx
      j = 1
      while self.color_at(j) != 0: j += 1
      # If one of boundary has same color,
      # it is >=6-connect
      if self.color_at(0) == c or self.color_at(6) == c:
        self.mark(c, j, B_OVER_5)
      else:
        self.mark(c, j, B_5)

    def _check_4(self, c):
      for i in range(1, 6): self.mark(c, i, B_4)
      if self.color_at(1) == 0 and self.color_at(6) == 0:
        for i in range(2, 6):
          self.mark(c, i, B_OPEN_4)
      if self.color_at(0) == 0 and self.color_at(5) == 0:
        for i in range(1, 5):
          self.mark(c, i, B_OPEN_4)

    def _check_3(self, c):
      for i in range(1, 6): self.mark(c, i, B_3)
      if self.color_at(1) != 0 or self.color_at(5) != 0: return
      if self.color_at(2) == 0:
        if self.color_at(0) == 0:
          self.mark(c, 1, B_OPEN_3)
          self.mark(c, 2, B_OPEN_3)
        elif self.color_at(6) == 0:
          self.mark(c, 2, B_OPEN_3)
      elif self.color_at(4) == 0:
        if self.color_at(6) == 0:
          self.mark(c, 4, B_OPEN_3)
          self.mark(c, 5, B_OPEN_3)
        elif self.color_at(0) == 0:
          self.mark(c, 4, B_OPEN_3)
      else:
        if self.color_at(0) == 0:
          self.mark(c, 1, B_OPEN_3)
          self.mark(c, 3, B_OPEN_3)
        elif self.color_at(6) == 0:
          self.mark(c, 3, B_OPEN_3)
          self.mark(c, 5, B_OPEN_3)

    def _check_2(self, c):
      j = 1
      while self.color_at(j) == 0: j += 1
      for i in range(max(1, j - 2), min(j + 2, 5) + 1):
        self.mark(c, i, B_2)

    def check_connection(self):
      if self.n_color[3] == 0:
        c = 0
        if self.n_color[1] == 0: c = 2
        elif self.n_color[2] == 0: c = 1
        if c > 0:
          if self.n_color[c] == 4: self._check_5(c)
          elif self.n_color[c] == 3: self._check_4(c)
          elif self.n_color[c] == 2: self._check_3(c)
          elif self.n_color[c] == 1: self._check_2(c)

    def push_and_check(self, color=3, idx=None):
      self.push(color, idx)
      self.check_connection()

  def fill_result(self):
    # Row
    for i in range(self.game.height):
      w = self._Window(self, 0)
      for (r, c) in self.game.iter_row(i):
        w.push_and_check(self.game[r, c], self.game._reduce_index(r, c))
      w.push_and_check()
    # Col
    for i in range(self.game.width):
      w = self._Window(self, 1)
      for (r, c) in self.game.iter_column(i):
        w.push_and_check(self.game[r, c], self.game._reduce_index(r, c))
      w.push_and_check()
    # Diagonal
    for i in range(self.game.width + self.game.height - 1):
      w = self._Window(self, 2)
      for (r, c) in self.game.iter_right_down(i):
        w.push_and_check(self.game[r, c], self.game._reduce_index(r, c))
      w.push_and_check()
      w = self._Window(self, 3)
      for (r, c) in self.game.iter_left_down(i):
        w.push_and_check(self.game[r, c], self.game._reduce_index(r, c))
      w.push_and_check()

  def get_critical_at(self, color, dir, idx):
    bm = self.result[color][dir][idx]
    if bm & B_OVER_5: return N_OVER_5
    elif bm & B_5: return N_5
    elif bm & B_OPEN_4: return N_OPEN_4
    elif bm & B_4: return N_4
    elif bm & B_OPEN_3: return N_OPEN_3
    elif bm & B_3: return N_3
    elif bm & B_2: return N_2
    return 0

  def run_analysis(self):
    self.fill_result()

