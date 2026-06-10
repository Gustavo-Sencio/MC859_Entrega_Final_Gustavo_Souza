// Consultas auxiliares para interpretar a analise de edge betweenness.

// Macroarea dominante de uma comunidade especifica
// Substitua 7708 pelo communityId de interesse.
MATCH (a:Author)
WHERE a.communityId = 7708
  AND a.author_primary_macroarea IS NOT NULL
  AND a.author_primary_macroarea <> ''
WITH collect(a.author_primary_macroarea) AS areas, count(a) AS total_comunidade
UNWIND areas AS area_raw
WITH total_comunidade,
     CASE
       WHEN area_raw STARTS WITH 'Tie: ' THEN split(substring(area_raw, 5), ' | ')
       ELSE [area_raw]
     END AS area_list
UNWIND area_list AS macroarea
WITH total_comunidade, macroarea, 1.0 / size(area_list) AS peso
WITH total_comunidade, macroarea, sum(peso) AS peso_total
RETURN
  macroarea AS macroarea_dominante,
  round(peso_total * 100) / 100.0 AS autores_equivalentes,
  round(100.0 * peso_total / total_comunidade * 100) / 100.0 AS proporcao_percentual
ORDER BY peso_total DESC
LIMIT 1;

// Suporte para anotar as top arestas por edge betweenness:
// substitua a lista de pares abaixo pelos pares retornados pelo script Python.
WITH [
  {source: '14831722300', target: '57201607778'},
  {source: '57201607778', target: '6603267575'}
] AS pairs
UNWIND pairs AS pair
MATCH (a:Author {author_id: pair.source})
MATCH (b:Author {author_id: pair.target})
WITH pair, a, b, [a.communityId, b.communityId] AS communities
UNWIND communities AS cid
WITH pair, a, b, collect(DISTINCT cid) AS needed_communities
CALL (needed_communities) {
  UNWIND needed_communities AS cid
  MATCH (m:Author)
  WHERE m.communityId = cid
    AND m.author_primary_macroarea IS NOT NULL
    AND m.author_primary_macroarea <> ''
  WITH cid,
       CASE
         WHEN m.author_primary_macroarea STARTS WITH 'Tie: '
           THEN split(substring(m.author_primary_macroarea, 5), ' | ')
         ELSE [m.author_primary_macroarea]
       END AS macroareas
  UNWIND macroareas AS macroarea
  WITH cid, macroarea, 1.0 / size(macroareas) AS peso
  WITH cid, macroarea, sum(peso) AS peso_total
  ORDER BY cid, peso_total DESC, macroarea ASC
  WITH cid, collect({macroarea: macroarea, peso: peso_total}) AS dist
  RETURN collect({
    communityId: cid,
    macroarea_dominante: dist[0].macroarea
  }) AS community_info
}
WITH pair, a, b, community_info,
     [x IN community_info WHERE x.communityId = a.communityId][0].macroarea_dominante AS macro_a,
     [x IN community_info WHERE x.communityId = b.communityId][0].macroarea_dominante AS macro_b
RETURN
  a.author_name AS autor_origem,
  b.author_name AS autor_destino,
  a.communityId AS comunidade_origem,
  b.communityId AS comunidade_destino,
  macro_a AS macroarea_dominante_comunidade_origem,
  macro_b AS macroarea_dominante_comunidade_destino,
  CASE WHEN macro_a = macro_b THEN 'Sim' ELSE 'Nao' END AS mesmas_macroareas_dominantes
ORDER BY autor_origem, autor_destino;
