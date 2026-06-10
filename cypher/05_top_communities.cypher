// Consultas para resultados de comunidades estruturais.

// Total de comunidades
MATCH (a:Author)
RETURN count(DISTINCT a.communityId) AS total_communities;

// Distribuicao de tamanhos das comunidades
MATCH (a:Author)
WITH a.communityId AS communityId, count(*) AS tamanho
RETURN tamanho, count(*) AS quantidade_comunidades
ORDER BY tamanho ASC;

// Top 15 comunidades com macroarea dominante por "autores equivalentes"
MATCH (a:Author)
WHERE a.communityId IS NOT NULL
WITH a.communityId AS communityId, count(*) AS total_comunidade
ORDER BY total_comunidade DESC
LIMIT 15
MATCH (b:Author)
WHERE b.communityId = communityId
  AND b.author_primary_macroarea IS NOT NULL
  AND b.author_primary_macroarea <> ''
WITH communityId, total_comunidade,
     CASE
       WHEN b.author_primary_macroarea STARTS WITH 'Tie: '
         THEN split(substring(b.author_primary_macroarea, 5), ' | ')
       ELSE [b.author_primary_macroarea]
     END AS macroareas
UNWIND macroareas AS macroarea
WITH communityId, total_comunidade, macroarea, 1.0 / size(macroareas) AS peso
WITH communityId, total_comunidade, macroarea, sum(peso) AS peso_total
ORDER BY communityId, peso_total DESC, macroarea ASC
WITH communityId, total_comunidade, collect({
  macroarea: macroarea,
  peso: peso_total
}) AS dist
RETURN
  communityId,
  total_comunidade AS tamanho_comunidade,
  dist[0].macroarea AS macroarea_dominante,
  round(dist[0].peso * 100) / 100.0 AS autores_equivalentes,
  round(10000.0 * dist[0].peso / total_comunidade) / 100.0 AS proporcao_percentual
ORDER BY tamanho_comunidade DESC;

// Distribuicao tematica detalhada da comunidade 415
MATCH (a:Author)
WHERE a.communityId = 415
WITH count(a) AS total_comunidade
MATCH (b:Author)
WHERE b.communityId = 415
  AND b.author_primary_macroarea IS NOT NULL
  AND b.author_primary_macroarea <> ''
WITH total_comunidade,
     CASE
       WHEN b.author_primary_macroarea STARTS WITH 'Tie: '
         THEN split(substring(b.author_primary_macroarea, 5), ' | ')
       ELSE [b.author_primary_macroarea]
     END AS macroareas
UNWIND macroareas AS macroarea
WITH total_comunidade, macroarea, 1.0 / size(macroareas) AS peso
WITH total_comunidade, macroarea, sum(peso) AS autores_equivalentes
RETURN
  macroarea,
  round(autores_equivalentes * 100) / 100.0 AS autores_equivalentes,
  round(10000.0 * autores_equivalentes / total_comunidade) / 100.0 AS percentual
ORDER BY autores_equivalentes DESC, macroarea ASC;

