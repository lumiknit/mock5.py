#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mock5 agent: strategy = pt

Author: lumiknit (aasr4r4@gmail.com)

Add more random actions

"""

from mock5.analysis import *
import numpy as np

def score_at(game, a, i):
  mn = 0
  cnt = 1
  s = 0
  for dir in range(4):
    m = a.get_critical_at(game.player, dir, i)
    o = a.get_critical_at(3 - game.player, dir, i)
    s += m + o * 0.9
    if mn == m * 2 + 1: cnt += 1
    elif mn < m * 2 + 1: mn, cnt = m * 2 + 1, 1
    if mn == o * 2: cnt += 1
    elif mn < o * 2: mn, cnt = o * 2, 1
  if mn >= N_5 * 2:
    return 5 + (mn % 2) # Left 1 turn
  elif mn >= N_OPEN_4 * 2 or int(mn / 2) == N_4 and cnt >= 2:
    return 3 + (mn % 2) # Left 2 turn
  elif mn >= N_OPEN_3 * 2:
    return 1 + (mn % 2) # Left 1 turn
  elif mn > 0:
    return s / (8 * N_4)
  else:
    return 0

def policy(game):
  sz = game.height * game.width
  a = Analysis(game)
  lh = len(game.history)
  if lh == 0:
    # First, place a stone near to center
    a = np.zeros(sz)
    hr = int(game.height / 2)
    hc = int(game.width / 2)
    hm = max(2, int((game.height - 15) / 2), int((game.height - 15) / 2))
    for dr in range(-hm + 1, hm):
      for dc in range(-hm + 1, hm):
        a[(hr + dr) * game.width + (hc + dc)] = 1
    return a
  elif lh <= 2:
    # Then, place a stone around
    a = np.zeros(sz)
    i = game.history[0]
    r, c = i // game.width, i % game.width
    for dr in range(-lh, lh + 1):
      xr = r + dr
      if 0 <= xr and xr < game.height:
        for dc in range(-lh, lh + 1):
          xc = c + dc
          if 0 <= xc and xc < game.width:
            a[xr * game.width + xc] = 1
    return a
  mz = [np.zeros(sz) for i in range(7)]
  for i in range(sz):
    if game.board[i] == 0:
      score = score_at(game, a, i)
      if score >= 1: mz[int(score)][i] = 1
      else: mz[0][i] = score
  for i in range(6, 0, -1):
    if mz[i].sum() > 0: return mz[i]
  return mz[0]
policy.name = "pt"

def agent(game):
  sz = game.height * game.width
  p = policy(game)
  m = (np.array(game.board) == 0).astype(int)
  a = p * m
  sa = a.sum()
  sm = m.sum()
  if sa > 0: idx = np.random.choice(sz, p=a/sa)
  elif sm > 0: idx = np.random.choice(sz, p=m/sm)
  else: return None
  return game._expand_index(idx)

agent.name = "agent-pt"
