# -*- coding: utf-8 -*-
"""mock5/read_record.py

Author: lumiknit (aasr4r4@gmail.com)

Record (generated by gen.cpp) reader for torch
"""
import torch

def read_record_from_file(h, w, filename):
  """Record (generated by gen.cpp) reader for torch

  Returns:
    X (torch.tensor(<NUM_SAMPLE>, 3, h, w)): one-hot-encoding version tensor
    Y (torch.tensor(<NUM_SAMPLE>, 1)): label. 1 = good, -1 = bad
  """
  X = []
  Y = []
  with open(filename) as file:
    left = 0
    v = 0
    for line in file:
      if left <= 0:
        z = [torch.ones(h, w, dtype=torch.float),
             torch.zeros(h, w, dtype=torch.float),
             torch.zeros(h, w, dtype=torch.float)]
        bd = torch.stack(z)
        v, left = map(int, line.split())
      else:
        print(bd)
        idx = int(line)
        y = idx // w
        x = idx % w
        bd[0][y][x] = 0
        bd[v][y][x] = 1
        X.append(bd.clone())
        Y.append(torch.tensor([3 - v * 2], dtype=torch.float))
        v = 3 - v
        left -= 1
  Xs = torch.stack(X)
  Ys = torch.stack(Y)
  return Xs, Ys

if __name__ == "__main__":
  x, y  = read_record_from_file(11, 11, "out")
  print(x.shape, y.shape)
  print(x)
  print(y)
