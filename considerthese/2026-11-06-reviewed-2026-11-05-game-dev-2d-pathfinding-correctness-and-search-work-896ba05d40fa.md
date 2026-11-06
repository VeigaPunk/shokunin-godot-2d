# Cheapest routes and least search work

Hart, Nilsson and Raphael, [A Formal Basis for the Heuristic Determination of Minimum Cost Paths](https://www.cs.auckland.ac.nz/courses/compsci709s2c/resources/Mike.d/astarNilsson.pdf), July 1968, §§I–III: A* orders by route cost plus estimated remainder. Their admissibility argument uses lower bounds and reopening improved closed nodes; expansion optimality additionally invokes consistency.

Dechter and Pearl, [Generalized Best-First Search Strategies and the Optimality of A*](https://ics.uci.edu/~dechter/publications/r0.pdf), July 1985, §§4.1–4.3.1: equally informed competitors may use discovered information differently. Admissible but inconsistent estimates do not make A* expansion-optimal across their admissible forward-search class. With consistency, the guarantee depends on tie-breaking.

For game pathfinding, cheapest-path correctness and search-work comparisons are different promises. Neither establishes runtime speed or current Godot behavior.

Auckland's annotated eight-page IEEE scan and Dechter's 32-page ACM journal scan retain original pagination; file dates do not date publication. ACM grants conditional copying; unrestricted reuse or training permission is unestablished for either. Links and original commentary only.
