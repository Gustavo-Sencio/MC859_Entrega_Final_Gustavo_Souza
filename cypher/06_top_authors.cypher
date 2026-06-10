// Top autores por betweenness.

MATCH (a:Author)
WHERE a.betweenness IS NOT NULL
RETURN
  a.author_id AS author_id,
  a.author_name AS author_name,
  a.author_primary_macroarea AS macroarea_principal,
  a.communityId AS communityId,
  a.betweenness AS betweenness
ORDER BY a.betweenness DESC
LIMIT 15;

