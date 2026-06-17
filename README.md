# Entrega Final - MC859

Implementacao e artefatos da entrega final do projeto de MC859 sobre analise de centralidade e comunidades em uma rede de coautoria associada a UNICAMP.

## Objetivo

O projeto constroi uma rede de coautoria a partir de publicacoes coletadas na Scopus e investiga se autores com alta centralidade de intermediacao atuam como pontes entre comunidades estruturais e macroareas tematicas distintas. Como complemento, o repositorio tambem inclui uma analise de `edge betweenness centrality` das arestas.

## Estrutura do repositorio

- `src/`: scripts Python do pipeline.
- `cypher/`: consultas executadas no Neo4j Desktop / GDS.
- `data/raw/`: dados base usados no pipeline (`articles.csv`, `authors.csv`) e CSVs usados para popular o Neo4j (`neo4j_seed/`).
- `data/interim/`: saídas intermediarias do processamento tematico.
- `data/graph/`: representacao consolidada do grafo em GraphML.
- `outputs/analysis_output/`: metricas e figuras estruturais do grafo.
- `outputs/neo4j_exports/`: exportacoes tabulares de resultados produzidos no Neo4j.
- `outputs/tables/report/`: tabelas em CSV correspondentes a tabelas usadas no relatorio.
- `outputs/tables/`: tabelas auxiliares, incluindo o ranking de edge betweenness.

## Dependencias

Bibliotecas Python usadas no pipeline:

- `requests`
- `pandas`
- `numpy`
- `matplotlib`

Dependencias externas:

- Neo4j Desktop
- Neo4j Graph Data Science (GDS)

## Configuracao da API Scopus

Os scripts de coleta usam a API da Scopus. Para executar novamente a coleta, substitua o valor `KEY` em:

- `src/01_collect_scopus_data.py`
- `src/02_collect_article_topics.py`

por uma chave valida da API da Elsevier.

## Ordem sugerida de execucao

### 1. Coleta de dados base

```bash
python3 src/01_collect_scopus_data.py
```

Gera:

- `data/raw/articles.csv`
- `data/raw/authors.csv`

### 2. Coleta de temas dos artigos

```bash
python3 src/02_collect_article_topics.py
```

Gera:

- `data/interim/article_topics.csv`
- `data/interim/checkpoints/article_topics_progress.csv`

### 3. Classificacao de temas de artigos em macroareas

```bash
python3 src/03_classify_article_macroareas.py
```

Gera:

- `data/interim/article_macroareas_output/articles_research_macroareas.csv`
- `data/interim/article_macroareas_output/unclassified_article_terms.csv`

### 4. Agregacao de macroareas no nivel dos autores

```bash
python3 src/04_aggregate_author_macroareas.py
```

Gera:

- `data/interim/author_macroareas_output/author_macroareas_from_articles.csv`

### 5. Construcao do grafo em GraphML

```bash
python3 src/05_build_graphml.py
```

Gera:

- `data/graph/coauthorship.graphml`

### 6. Analise estrutural basica do grafo

```bash
python3 src/06_analyze_graph.py
```

Gera arquivos em:

- `outputs/analysis_output/`

### 7. Exportacao para carga no Neo4j

```bash
python3 src/07_export_neo4j_csv.py
```

Gera:

- `data/raw/neo4j_seed/authors_nodes.csv`
- `data/raw/neo4j_seed/coauthorship_edges.csv`

### 8. Analise no Neo4j

No Neo4j Desktop, importe os arquivos de `data/raw/neo4j_seed/` e execute as consultas da pasta `cypher/` na ordem descrita em `cypher/README.md`.

As consultas cobrem:

- projecao do grafo no GDS
- Louvain
- betweenness de vertices
- metricas de heterofilia
- consultas para tabelas do relatorio
- consultas auxiliares para interpretacao das arestas

### 9. Edge betweenness centrality das arestas

```bash
python3 src/08_edge_betweenness.py
```

Gera:

- `outputs/tables/all_edge_betweenness.csv`
- `outputs/tables/top30_all_edge_betweenness.csv`

## Tabelas do relatorio

As tabelas em formato CSV correspondentes ao relatorio estao em:

- `outputs/tables/report/01_maiores_comunidades.csv`
- `outputs/tables/report/02_top_authors_betweenness.csv`
- `outputs/tables/report/03_tipologia_autores_centrais.csv`
- `outputs/tables/report/04_macroarea_perfil.csv`
- `outputs/tables/report/05_estudos_caso_autores.csv`
- `outputs/tables/report/06_estudo_caso_comunidade_415.csv`

## Observacao sobre reproducao

O repositorio inclui tanto os scripts quanto os principais arquivos de entrada e saida usados na analise. Assim, mesmo sem repetir toda a coleta na Scopus, e possivel inspecionar o pipeline, reconstruir o grafo e reproduzir a etapa analitica no Neo4j a partir dos CSVs e do GraphML incluidos.
