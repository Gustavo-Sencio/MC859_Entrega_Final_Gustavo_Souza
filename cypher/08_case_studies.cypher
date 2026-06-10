// Estudos de caso e consultas de visualizacao.

// Tabela de estudos de caso: Reis F., Masiero B. e Franco T.T.
MATCH (a:Author)
WHERE a.author_name IN ['Reis F.', 'Masiero B.', 'Franco T.T.']
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
RETURN
  a.author_name AS autor,
  round(
    1000.0 * CASE
      WHEN total_neighbors = 0 THEN 0.0
      ELSE toFloat(other_community_count) / total_neighbors
    END
  ) / 1000.0 AS `Frac. outra comm.`,
  round(
    1000.0 * CASE
      WHEN total_neighbors = 0 THEN 0.0
      ELSE toFloat(other_area_count) / total_neighbors
    END
  ) / 1000.0 AS `Frac. outra area`,
  round(
    1000.0 * CASE
      WHEN other_community_count = 0 THEN 0.0
      ELSE toFloat(other_community_other_area_count) / other_community_count
    END
  ) / 1000.0 AS `Frac. ext. outra area`,
  CASE
    WHEN a.betweenness <= 4000000 THEN 'Fora do conjunto central'
    WHEN other_community_count < 5 THEN 'Central local'
    WHEN toFloat(other_community_other_area_count) / other_community_count >= 0.7 THEN 'Ponte interarea forte'
    WHEN toFloat(other_community_other_area_count) / other_community_count >= 0.4 THEN 'Ponte interarea moderada'
    ELSE 'Central local'
  END AS perfil
ORDER BY a.betweenness DESC;

// Ego-rede de Masiero B. com classificacao visual dos vizinhos
MATCH (a:Author {author_id: '26638969400'})
MATCH (a)-[:COAUTHORED_WITH]-(n:Author)
WITH a, collect(n) AS neighbors
UNWIND neighbors AS n
WITH
  a,
  n,
  CASE
    WHEN n.communityId = a.communityId THEN 'SameCommunity'
    WHEN n.author_primary_macroarea = a.author_primary_macroarea THEN 'OtherCommunitySameArea'
    ELSE 'OtherCommunityOtherArea'
  END AS ego_color
SET n.ego_color = ego_color
SET a.is_focus = true
RETURN a, n;

// Subgrafo da ego-rede de Masiero B.
MATCH (a:Author {author_id: '26638969400'})
MATCH (a)-[:COAUTHORED_WITH]-(n:Author)
WITH a, collect(n) AS neighbors
MATCH (u:Author)-[r:COAUTHORED_WITH]-(v:Author)
WHERE u = a OR v = a OR (u IN neighbors AND v IN neighbors)
RETURN u, r, v;

