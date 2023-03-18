# Rush Hour Shift - Board Game Assignment

The UI for the game was made using pygame which can be installed using pip. For the main menu we used tkinter. Here you can pick a map and select different players.

```sh
pip install pygame
python main.py
```

If your python installation does not come with tkinter you can run ```main2.py```. You can select different options by editing the inputs of the ```new_game``` function. There are maps from 0-10 and player indexes can be found using the list below.

```sh
           Map      Player1       Player2
new_game(maps[0], players[8](), players[0]())
```

## Maps

Maps 1-10 were taken from the game setup descriptions at [Ultra Boardgames](https://www.ultraboardgames.com/rush-hour-shift/game-rules.php).

## List of players

- HumanPlayer
- Random
- MinimaxPlayer
- BeamPlayer
- IterativeDeepeningPlayer
- IterativeDeepeningPlayerWithHistory,
- MonteCarloPlayer
- GreedyPlayer
- PoolMonteCarloPlayer
