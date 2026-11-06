# 2D: packing quality depends on the problem contract

[Baker, Coffman and Rivest](https://people.csail.mit.edu/rivest/pubs/BCR80.pdf),1980, study fixed-width, open-height packing without quarter-turns. Bottom-left performance depends on ordering; even its best ordering need not produce an optimum.

[Jylänki's report](https://github.com/juj/RectangleBinPack/blob/master/RectangleBinPack.pdf), February27,2010, studies finite bins with permitted rotation and practical variants including maximal free rectangles. Its comparisons use best-known solutions, not necessarily proven optima.

These are different contracts, not merely a newer bound for the same task. Earlier analysis remains useful for understanding ordering limits. Finite-bin results cannot silently authorize rotation in a sprite pipeline whose consumer cannot reconstruct orientation.

Selected model, limitation, maximal-rectangle and results passages read; no packing or proof executed. The earlier scan bears SIAM copyright. The repository's public-domain notice covers code, not an established license for the report. No general report reuse grant verified. Original commentary only; no figures or implementation copied.

Optional exercises omitted; originals retained.
