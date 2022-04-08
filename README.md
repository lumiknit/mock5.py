# mock5.py

Simple omok (five-in-a-row) game in python, to be used with numpy/torch.

## Usage

You can excute it by

```
python play.py [<AGENT>] [<BOARD_HEIGHT> <BOARD_WIDTH>]
```

in your shell.
Default height and width are 15.
If you did not specify agent, you should play two players,
or you will play with it.
Currently there are two agents:

- `random` : Use `mock5/agent_random`. Just move randomly
- `silly` : Use `mock5/agent_analysis_based`. Analyze game board and
  move based on a kind of reward(?) table.

or import the module by

```python
import mock5
# or
from mock5 import Mock5
```

in your python script. More details are in `help(mock5)`.
