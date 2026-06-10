# Consultas Cypher

Estas consultas correspondem a etapa analitica executada no Neo4j Desktop com a
biblioteca Graph Data Science (GDS).

## Ordem sugerida

1. `01_projection.cypher`
2. `02_louvain.cypher`
3. `03_betweenness.cypher`
4. `04_network_summary.cypher`
5. `05_top_communities.cypher`
6. `06_top_authors.cypher`
7. `07_heterophily_and_typology.cypher`
8. `08_case_studies.cypher`
9. `09_edge_support.cypher`

## Observacoes

- O grafo projetado no GDS e nao direcionado.
- O Louvain considera o peso das arestas (`weight`).
- A betweenness de vertices foi calculada sem pesos.
- A edge betweenness foi calculada fora do Neo4j, via script Python, mas as
  consultas de `09_edge_support.cypher` ajudam a interpretar os resultados.

## Modelo assumido

- Nos: `(:Author)`
- Relacoes: `[:COAUTHORED_WITH]`
- Propriedades relevantes:
  - `author_id`
  - `author_name`
  - `author_primary_macroarea`
  - `communityId`
  - `betweenness`
  - `weight` nas arestas
