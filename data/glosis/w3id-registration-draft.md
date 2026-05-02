# Draft — Registro w3id.org PURL para GeoBrain

**Status:** rascunho · **NÃO submetido**. Submissão exige PR no repo `perma-id/w3id.org` autorizado pelo owner do projeto.

## Por que registrar

1. IRIs persistentes: hoje os identificadores canônicos vivem em `https://thiagoflc.github.io/geobrain/...`, atrelados a um usuário GitHub. Se o usuário/repo for renomeado ou movido, todas as IRIs quebram.
2. Padrão da indústria: GLOSIS, GSO, OSDU, GeoSciML, BFO, FOAF — todos usam `w3id.org` para garantir IRIs estáveis.
3. Custo zero, gratuito, mantido pela W3C Permanent Identifier Community Group.

## Espaço de nomes proposto

```
https://w3id.org/geolytics/dictionary/    → https://thiagoflc.github.io/geobrain/
https://w3id.org/geolytics/ontology/      → https://thiagoflc.github.io/geobrain/data/geobrain.ttl
https://w3id.org/geolytics/api/v1/        → https://thiagoflc.github.io/geobrain/api/v1/
```

## Procedimento (fonte: https://github.com/perma-id/w3id.org/blob/master/CONTRIBUTING.md)

1. Fork de `https://github.com/perma-id/w3id.org`.
2. Criar diretório `geolytics/` com:

   **`geolytics/.htaccess`**
   ```apache
   # GeoBrain — Ontologia de Exploração e Produção de Petróleo (Brasil)
   # Maintainer: Thiago Lopes <thiagoflc@gmail.com>
   # Source: https://github.com/thiagoflc/geobrain
   # Last updated: 2026-05-01

   Options +FollowSymLinks
   RewriteEngine on
   RewriteBase /geolytics/

   # Content negotiation: Turtle / JSON-LD / RDF/XML / HTML
   RewriteCond %{HTTP_ACCEPT} text/turtle [OR]
   RewriteCond %{HTTP_ACCEPT} application/x-turtle
   RewriteRule ^ontology/?$ https://thiagoflc.github.io/geobrain/data/geobrain.ttl [R=303,L]

   RewriteCond %{HTTP_ACCEPT} application/ld\+json
   RewriteRule ^ontology/?$ https://thiagoflc.github.io/geobrain/data/geolytics.jsonld [R=303,L]

   RewriteRule ^ontology/?$ https://thiagoflc.github.io/geobrain/ [R=303,L]

   # API
   RewriteRule ^api/v1/(.*)$ https://thiagoflc.github.io/geobrain/api/v1/$1 [R=302,L]

   # Default
   RewriteRule ^(.*)$ https://thiagoflc.github.io/geobrain/$1 [R=302,L]
   ```

3. Abrir PR com título: `Add geolytics namespace`.
4. Aguardar review da W3C PIDCG (tipicamente 1-3 semanas).

## Migração das IRIs após aprovação

Substituições no codebase (rg/sed):

```
https://thiagoflc.github.io/geobrain/  →  https://w3id.org/geolytics/
```

Arquivos prováveis a tocar (verificar com `rg`):
- `data/geobrain.ttl` (`@prefix geolytics:` e namespace base)
- `data/full.json`, `data/entity-graph.json` (campos `petrokgraph_uri`)
- `api/v1/index.json`
- `README.md`

Manter redirect 302 do GitHub Pages → IRIs antigas continuam funcionando.

## Checklist antes de submeter

- [ ] `data/geobrain.ttl` está estável e versionado (owl:versionIRI)
- [ ] Owner do projeto autoriza o registro
- [ ] Email de manutenção configurado e monitorado
- [ ] CONTRIBUTING.md atualizado mencionando processo de update do `.htaccess` quando recursos forem reestruturados
