# Consultas Cypher

Estas consultas correspondem a etapa analitica executada no Neo4j Desktop com a biblioteca Graph Data Science (GDS).

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

## O que cada arquivo faz

- `01_projection.cypher`: projeta o grafo `Author` / `COAUTHORED_WITH` no GDS como nao direcionado.
- `02_louvain.cypher`: executa Louvain considerando o peso das arestas e grava `communityId` nos nos.
- `03_betweenness.cypher`: calcula betweenness de vertices sem pesos e grava `betweenness`.
- `04_network_summary.cypher`: consultas de caracterizacao geral da rede.
- `05_top_communities.cypher`: consultas para maiores comunidades, distribuicao de tamanhos e detalhe da comunidade 415.
- `06_top_authors.cypher`: top autores por betweenness.
- `07_heterophily_and_typology.cypher`: metricas de heterofilia e tipologia dos autores centrais.
- `08_case_studies.cypher`: estudos de caso e ego-rede de Masiero B.
- `09_edge_support.cypher`: consultas auxiliares para interpretar a analise de edge betweenness.

## Observacoes

- O grafo projetado no GDS e nao direcionado.
- O Louvain considera o peso das arestas (`weight`).
- A betweenness de vertices foi calculada sem pesos.
- A edge betweenness foi calculada fora do Neo4j, via script Python, mas as consultas de `09_edge_support.cypher` ajudam a interpretar os resultados.

## Modelo assumido

- Nos: `(:Author)`
- Relacoes: `[:COAUTHORED_WITH]`
- Propriedades relevantes nos nos:
  - `author_id`
  - `author_name`
  - `author_primary_macroarea`
  - `communityId`
  - `betweenness`
- Propriedade relevante nas arestas:
  - `weight`

## Relacao com as tabelas do relatorio

As consultas desta pasta sustentam as tabelas exportadas em `outputs/tables/report/`:

- `05_top_communities.cypher` -> `01_maiores_comunidades.csv`
- `06_top_authors.cypher` -> `02_top_authors_betweenness.csv`
- `07_heterophily_and_typology.cypher` -> `03_tipologia_autores_centrais.csv` e `04_macroarea_perfil.csv`
- `08_case_studies.cypher` -> `05_estudos_caso_autores.csv`
- `05_top_communities.cypher` (comunidade 415) -> `06_estudo_caso_comunidade_415.csv`
