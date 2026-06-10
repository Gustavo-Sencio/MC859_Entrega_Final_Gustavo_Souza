// Calcula betweenness de vertices sem pesos e grava em `betweenness`.

CALL gds.betweenness.write('coauthorshipG', {
  writeProperty: 'betweenness'
})
YIELD
  centralityDistribution,
  computeMillis,
  writeMillis;

// Resumo simples da distribuicao
MATCH (a:Author)
RETURN
  min(a.betweenness) AS min_betweenness,
  percentileCont(a.betweenness, 0.25) AS p25,
  percentileCont(a.betweenness, 0.50) AS median,
  percentileCont(a.betweenness, 0.75) AS p75,
  max(a.betweenness) AS max_betweenness;

