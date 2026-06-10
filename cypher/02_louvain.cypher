// Executa Louvain considerando o peso das arestas e grava `communityId`.

CALL gds.louvain.write('coauthorshipG', {
  writeProperty: 'communityId',
  relationshipWeightProperty: 'weight'
})
YIELD
  communityCount,
  modularity,
  modularities,
  ranLevels,
  didConverge,
  computeMillis,
  writeMillis;

// Quantidade total de comunidades gravadas
MATCH (a:Author)
RETURN count(DISTINCT a.communityId) AS total_communities;

