// Projeta o grafo de coautoria para o GDS como nao direcionado.

CALL gds.graph.exists('coauthorshipG')
YIELD exists
WITH exists
WHERE exists
CALL gds.graph.drop('coauthorshipG', false)
YIELD graphName AS droppedGraph
RETURN droppedGraph;

// Se o grafo nao existir, a consulta acima nao retorna linhas. Em seguida:

CALL gds.graph.project(
  'coauthorshipG',
  'Author',
  {
    COAUTHORED_WITH: {
      type: 'COAUTHORED_WITH',
      orientation: 'UNDIRECTED',
      properties: 'weight'
    }
  }
)
YIELD
  graphName,
  nodeCount,
  relationshipCount,
  createMillis;
