#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mock5 agent: strategy = RANDOM

Author: lumiknit (aasr4r4@gmail.com)

Find random empty space and place a stone.

Use `agent` function.

"""

def agent(game):
  import random
  idx = random.randint(0, game.height * game.width)
  for off in range(game.height * game.width):
    rdx = (idx + off) % (game.height * game.width)
    r, c = game._expand_index(rdx)
    if game.can_place_at(r, c):
      return (r, c)
