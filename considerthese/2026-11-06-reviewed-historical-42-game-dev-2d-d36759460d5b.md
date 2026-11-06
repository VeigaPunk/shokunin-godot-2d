# Corners and thin features are different promises

[Green](https://cdn.fastly.steamstatic.com/apps/valve/2007/SIGGRAPH2007_AlphaTestedMagnification.pdf),2007, replaces coverage with a low-resolution signed-distance channel. Interpolation supports magnification and effects with inexpensive integration, but limits representable topology. Single-channel corners round off. The paper already combines two edge channels: later work did not invent that idea.

[Chlumský's thesis](https://github.com/Chlumsky/msdfgen/files/3050967/thesis.pdf), May2015, directly assigns edges to channels and reconstructs through their median. Collision correction replaces problematic cells with single-channel behavior, sacrificing corner quality locally. Threshold tuning balances missed artifacts against false positives. Thin features remain a separate problem; the thesis discusses thickening as future work rather than guaranteeing preservation.

Use the older representation as a transparent comparison, then specify which corners, slots and separations matter. Neither reading establishes today's library behavior or Godot performance. No generator, artwork, benchmark or proof executed.

Green reserves rights. The thesis permits constrained nonprofit use while reserving copyright; this does not clear fonts or software separately. Original commentary and links only, no source or figures redistributed.

Optional exercises omitted; originals retained.
