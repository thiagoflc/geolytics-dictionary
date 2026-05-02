# Bibliografia das traduções PT/ES

Fontes consultadas para a tradução dos 254 conceitos GLOSIS (88 lithology + 166 petrography) ao português e espanhol peninsular.

## Português (pt-BR)

- **CPRM Glossário Geológico Ilustrado (2018)** — Serviço Geológico do Brasil, Companhia de Pesquisa de Recursos Minerais.
  http://recursomineralmg.cprm.gov.br/glossario/
- **ABNT NBR 6502:1995** — Rochas e solos — Terminologia. Associação Brasileira de Normas Técnicas.
- **DNPM Léxico Estratigráfico do Brasil** — Departamento Nacional de Produção Mineral.
- **Schlumberger Oilfield Glossary (PT-BR)** — https://glossary.slb.com/pt
- **FAO/UNESCO Soil Map of the World — Versão portuguesa** — IPGRI/EMBRAPA.

## Espanhol peninsular (es-ES)

- **IGME Diccionario de Términos Geológicos** — Instituto Geológico y Minero de España.
  https://www.igme.es/
- **CSIC Glosario de Edafología** — Consejo Superior de Investigaciones Científicas.
- **AEMA — Agencia Europea de Medio Ambiente** — terminologia INSPIRE em espanhol.
- **Schlumberger Oilfield Glossary (ES)** — https://glossary.slb.com/es

## Equivalências latino-americanas notáveis

Onde a forma peninsular diverge significativamente da latino-americana (raro em geologia), notar com `notes` no CSV:

| EN | es-ES | es-MX | es-AR |
|---|---|---|---|
| weathering | meteorización | intemperismo | meteorización |
| eolian | eólico | eólico | eólico |
| peat | turba | turba | turba |
| loam | franco | franco / marga | franco |

(diferenças mínimas; usaremos forma peninsular `es-ES` taggeada como `@es`.)

## Schema das colunas CSV

```
id          identificador GLOSIS (ex: lithologyValueCode-IB1)
en          rótulo inglês original (read-only — NÃO editar)
suggestion  sugestão automática gerada por seed-translations.js
reviewed    rótulo final canônico (preencher manualmente)
source      origem da tradução
            ∈ {auto:cognate, CPRM:2018, ABNT:NBR-6502, IGME:diccionario,
               SLB:glossary, manual}
reviewer    iniciais do revisor (ex: TFL, AS)
notes       observações (gênero, contexto, falsos cognatos evitados)
```

## Política de aceitação

- `auto:cognate` sem `reviewed` preenchido → falha o `apply-translations.js`.
- `reviewed` preenchido → vence sempre, mesmo se contradiz `suggestion`.
- `source: manual` requer `reviewer` não-vazio.
