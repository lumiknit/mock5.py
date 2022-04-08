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

class Mock5Analysis:
  """ Omok Anlyzer

  It takes a game board Mock5 and anlayze the state:
  - (TODO) (semi-)opend 4 connections
  - (TODO) 3-3, 3-4, 4-4 after one move
  """

  def __init__(self, game):
    if type(game) is not Mock5: raise TypeError
    self.game = game
    self.run_analysis()

  class Component:
    def __init__(self, first, last, left_blank, inner_blank, right_blank):
      self.first = first
      self.last = last
      self.len = max(abs(first[0] - last[0]), abs(first[1] - last[1]))

      self.dr = _sign(last[0] - first[0])
      self.dc = _sign(last[1] - first[1])

      if dr * dc != 0 and abs(last[0] - first[0]) != abs(last[1] - first[1]):
        raise ValueError

      self.left_blank = left_blank
      self.inner_blank = inner_blank
      self.right_blank = right_blank

      self.n_stones = self.len - self.inner_blank

  def find_all_components(self):
    pass

  def run_analysis(self): pass

