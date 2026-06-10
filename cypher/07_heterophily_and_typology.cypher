// Metricas de heterofilia e tipologia dos autores centrais.

// Tabela dos 15 autores com maior betweenness
MATCH (a:Author)
WHERE a.betweenness IS NOT NULL
WITH a
ORDER BY a.betweenness DESC
LIMIT 15
OPTIONAL MATCH (a)-[:COAUTHORED_WITH]-(b:Author)
WITH a, collect(b) AS neighbors
WITH
  a,
  size(neighbors) AS total_neighbors,
  size([n IN neighbors WHERE n.communityId <> a.communityId]) AS other_community_count,
  size([n IN neighbors WHERE n.author_primary_macroarea <> a.author_primary_macroarea]) AS other_area_count,
  size([
    n IN neighbors
    WHERE n.communityId <> a.communityId
      AND n.author_primary_macroarea <> a.author_primary_macroarea
  ]) AS other_community_other_area_count
WITH
  a,
  total_neighbors,
  other_community_count,
  other_area_count,
  other_community_other_area_count,
  CASE
    WHEN total_neighbors = 0 THEN 0.0
    ELSE toFloat(other_community_count) / total_neighbors
  END AS frac_other_community,
  CASE
    WHEN total_neighbors = 0 THEN 0.0
    ELSE toFloat(other_area_count) / total_neighbors
  END AS frac_other_area,
  CASE
    WHEN other_community_count = 0 THEN 0.0
    ELSE toFloat(other_community_other_area_count) / other_community_count
  END AS frac_external_other_area
RETURN
  a.author_name AS autor,
  round(1000.0 * frac_other_community) / 1000.0 AS `Frac. outra comm.`,
  round(1000.0 * frac_other_area) / 1000.0 AS `Frac. outra area`,
  round(1000.0 * frac_external_other_area) / 1000.0 AS `Frac. ext. outra area`,
  CASE
    WHEN a.betweenness <= 4000000 THEN 'Fora do conjunto central'
    WHEN other_community_count < 5 THEN 'Central local'
    WHEN frac_external_other_area >= 0.7 THEN 'Ponte interarea forte'
    WHEN frac_external_other_area >= 0.4 THEN 'Ponte interarea moderada'
    ELSE 'Central local'
  END AS perfil
ORDER BY a.betweenness DESC;

// Contagem por perfil no subconjunto central
MATCH (a:Author)
WHERE a.betweenness > 4000000
OPTIONAL MATCH (a)-[:COAUTHORED_WITH]-(b:Author)
WITH a, collect(b) AS neighbors
WITH
  a,
  size([n IN neighbors WHERE n.communityId <> a.communityId]) AS other_community_count,
  size([
    n IN neighbors
    WHERE n.communityId <> a.communityId
      AND n.author_primary_macroarea <> a.author_primary_macroarea
  ]) AS other_community_other_area_count
WHERE other_community_count >= 5
WITH
  a,
  other_community_count,
  CASE
    WHEN other_community_count = 0 THEN 0.0
    ELSE toFloat(other_community_other_area_count) / other_community_count
  END AS frac_external_other_area
WITH CASE
  WHEN frac_external_other_area >= 0.7 THEN 'Ponte interarea forte'
  WHEN frac_external_other_area >= 0.4 THEN 'Ponte interarea moderada'
  ELSE 'Central local'
END AS perfil
RETURN perfil, count(*) AS quantidade
ORDER BY quantidade DESC;

// Macroarea principal x perfil
MATCH (a:Author)
WHERE a.betweenness > 4000000
OPTIONAL MATCH (a)-[:COAUTHORED_WITH]-(b:Author)
WITH a, collect(b) AS neighbors
WITH
  a,
  size([n IN neighbors WHERE n.communityId <> a.communityId]) AS other_community_count,
  size([
    n IN neighbors
    WHERE n.communityId <> a.communityId
      AND n.author_primary_macroarea <> a.author_primary_macroarea
  ]) AS other_community_other_area_count
WHERE other_community_count >= 5
WITH
  a.author_primary_macroarea AS macroarea,
  CASE
    WHEN other_community_count = 0 THEN 0.0
    ELSE toFloat(other_community_other_area_count) / other_community_count
  END AS frac_external_other_area
WITH
  macroarea,
  CASE
    WHEN frac_external_other_area >= 0.7 THEN 'Ponte interarea forte'
    WHEN frac_external_other_area >= 0.4 THEN 'Ponte interarea moderada'
    ELSE 'Central local'
  END AS perfil
RETURN macroarea, perfil, count(*) AS quantidade
ORDER BY macroarea, perfil;
