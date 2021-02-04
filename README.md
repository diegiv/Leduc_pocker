# Leduc_pocker

The goal is the deployment of a bot for playing a 2-player poker game. The software is required to produce a strategy for player 1 and a strategy for player 2.
Nowadays, the mainstream approach to solve a 2-player zero-sum game suggests that a bot should be composed of a number of components, namely:

Abstraction generator: given the game tree, a reduced version of the game is produced, even with loss of information (i.e., the optimal solution for the abstract game has no guarantee to be an optimal solution for the original, non-abstracted, game); this step is motivated by the fact that huge games cannot be practically solved exactly.
Game solver: given the abstract game, the optimal strategies of the players are computed by using an anytime algorithm with theoretical guarantees to converge eventually to the optimal solution; the strategies produced by the game solver are said blueprint.
Subgame re-solver: the blueprint is mapped to the original game. In doing this task, the blueprint is refined by expanding the abstraction and then re-solving a subgame under the assumption that the behavior of the players off such subgame is that prescribed by the blueprint. The rationale is that the blueprint may be too coarse when played in practice, and an on-the-fly refinement may lead to improve the performance of the strategy dramatically.
