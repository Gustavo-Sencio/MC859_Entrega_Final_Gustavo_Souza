// Consultas de caracterizacao geral da rede.

// Numero de vertices e arestas
MATCH (a:Author)
WITH count(a) AS total_nodes
MATCH ()-[r:COAUTHORED_WITH]-()
RETURN total_nodes, count(r) / 2 AS total_edges;

// Grau medio
MATCH (a:Author)
RETURN avg(COUNT { (a)--() }) AS average_degree;

// Grau ponderado medio
MATCH (a:Author)
OPTIONAL MATCH (a)-[r:COAUTHORED_WITH]-()
WITH a, sum(r.weight) AS weighted_degree
RETURN avg(weighted_degree) AS average_weighted_degree;
