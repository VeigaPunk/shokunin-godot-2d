# 2D: deep duplication is a versioned graph policy

Godot's tagged [4.4 Resource contract](https://github.com/godotengine/godot/blob/4.4-stable/doc/classes/Resource.xml) excludes resources inside arrays and dictionaries from duplication. The [4.5 contract](https://github.com/godotengine/godot/blob/4.5-stable/doc/classes/Resource.xml) with deep=true recursively copies containers and, by default, duplicates internal resources. It adds duplicate_deep modes controlling subresource scope.

Under 4.5, repeated references to one duplicated resource remain repeated references to one copy. INTERNAL excludes external-path resources; ALL includes them. Property duplication flags still supply exceptions. Therefore deep copying does not mean independently cloning every occurrence. These are tagged contracts, not runtime measurements.

**Proposed practice, unperformed:** Author a resource graph with two references to one pathless resource and one external resource. Duplicate it under explicit shallow, internal and all policies. Predict identity relationships, not values alone. Change one copied value and observe which references see it. Compare supported policies on pinned 4.4 and 4.5 builds separately; mark unavailable APIs rather than emulating them silently. Record graph, properties, flags, identities, mutations and build versions. Cap at four cases and one hour; no production assets or installations.

This differs from ResourceLoader cache freshness. No graph, engine or training was executed; no assimilation. Constructor requirements remain separate.

Original commentary and invented graph; no code copied or documentation reuse clearance asserted.

Destination: VeigaPunk/shokunin-godot-2d, main, considerthese/2026-11-12-resource-duplication-graph.md.
