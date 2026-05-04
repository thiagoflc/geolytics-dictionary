# Schema dos glossários Axon Petrobras (`data/axon/*.json`)

Este documento especifica o formato de cada arquivo de glossário Axon, como organizar IDs por área, e o procedimento para adicionar uma nova área.

> **Contexto.** Em F3 ingerimos o export Axon da área **Exploração** (40 entradas: 1 Area + 9 Domínios + 10 Assuntos + 2 Subassuntos + 18 Termos) — ver [data/axon/exploracao.json](../data/axon/exploracao.json). Em F9, o pipeline foi refatorado para suportar **múltiplas áreas** (Produção, Reservatório, Geofísica, Engenharia de Poço, …), uma por arquivo, listadas em [data/axon/manifest.json](../data/axon/manifest.json).

## 1. Estrutura de diretórios

```
data/axon/
  manifest.json          # lista de áreas ingeridas + planejadas
  exploracao.json        # F3 — área Exploração (única ingerida hoje)
  _template.json         # esqueleto a copiar para novas áreas
  <nova-area>.json       # áreas futuras
```

O pipeline (`scripts/generate.js → loadAxonManifest`) lê o manifest, itera as entradas com `status="ingested"`, carrega cada arquivo e funde as hierarquias no entity-graph.

## 2. Top-level keys de cada arquivo de área

| Key                | Tipo                          | Obrigatório | Descrição                                                  |
| ------------------ | ----------------------------- | ----------- | ---------------------------------------------------------- |
| `$schema`          | string (URI JSON Schema)      | Sim         | Sempre `http://json-schema.org/draft-07/schema#`.          |
| `id`               | string                        | Sim         | Identificador do arquivo, ex.: `axon-petrobras-glossary`.  |
| `label`            | string (pt-BR)                | Sim         | Rótulo humano, ex.: `Glossário Axon Petrobras (Produção)`. |
| `version`          | semver                        | Sim         | Versão do conteúdo, incrementa a cada review do curador.   |
| `source`           | string                        | Sim         | Origem do export (ex.: nome do arquivo XLSX + data).       |
| `license`          | string                        | Sim         | Licença, normalmente `Petrobras-internal (uso interno)`.   |
| `areas`            | array<Entry>                  | Sim         | Tipicamente 1 entrada — a Área Petrobras-pai.              |
| `domains`          | array<Entry>                  | Sim         | Domínios (pode ser `[]` se só houver Termos).              |
| `subjects`         | array<Entry>                  | Sim         | Assuntos (pode ser `[]`).                                  |
| `subsubjects`      | array<Entry>                  | Sim         | Subassuntos (pode ser `[]`).                               |
| `terms`            | array<Entry>                  | Sim         | Termos (pode ser `[]`).                                    |

## 3. Schema de cada entrada (`Entry`)

| Campo                       | Tipo               | Obrigatório | Descrição                                                                 |
| --------------------------- | ------------------ | ----------- | ------------------------------------------------------------------------- |
| `id`                        | string (slug)      | Sim         | Identificador único globalmente. Convenção em §4.                         |
| `name_pt`                   | string (pt-BR)     | Sim         | Nome canônico em português.                                               |
| `name_en`                   | string (en)        | Recomendado | Nome em inglês (default: igual ao pt-BR).                                 |
| `axon_type`                 | enum               | Sim         | Um de `Area`, `Dominio`, `Assunto`, `Subassunto`, `Termo`.                |
| `parent_id`                 | string             | Cond.       | ID do pai na hierarquia. Obrigatório exceto para a entrada raiz `Area`.   |
| `axon_path`                 | string             | Recomendado | Caminho hierárquico humano (`Exploração / Geomecânica / …`).              |
| `definition_pt`             | string (pt-BR)     | Sim         | Definição original do export Axon.                                        |
| `definition_pt_canonical`   | string (pt-BR)     | Recomendado | Definição revisada pelo curador (default: igual a `definition_pt`).       |
| `synonyms_pt`               | array<string>      | Opcional    | Sinônimos pt-BR.                                                          |
| `synonyms_en`               | array<string>      | Opcional    | Sinônimos en.                                                             |
| `legal_source`              | string             | Opcional    | Citação legal/normativa quando aplicável (ex.: `ANP 47/2014, art. 3º`).   |
| `links_to_existing`         | array<string>      | Opcional    | IDs de nós já existentes no entity-graph que este Termo descreve. Não duplica — vira ponte `is_specialization_of` em `scripts/generate.js`. |

## 4. Convenção de IDs (anti-colisão entre áreas)

A área **Exploração** (F3, único arquivo já ingerido) usa o prefixo histórico **sem** o `area_id` no slug:

```
axon-area-exploracao
axon-dom-geomecanica
axon-asn-perfilagem
axon-ssn-acervo-amostras
axon-term-poco
```

Para **manter compatibilidade com o entity-graph publicado**, esse prefixo permanece exatamente como está em `data/axon/exploracao.json`. Não renomear.

Para **toda nova área** (Produção, Reservatório, Geofísica, Engenharia de Poço, …), os IDs **devem** incluir o `area_id` para evitar colisões — duas áreas podem legitimamente ter um Domínio "Geomecânica", e cada um precisa de ID distinto:

```
axon-producao-area-producao
axon-producao-dom-elevacao-artificial
axon-producao-asn-bombeio-centrifugo-submerso
axon-producao-ssn-monitoramento-bcs
axon-producao-term-bcs

axon-reservatorio-dom-modelagem-dinamica
axon-geofisica-dom-aquisicao-sismica
axon-engenharia-poco-dom-perfuracao
```

Em resumo:

| Área              | Convenção de prefixo                |
| ----------------- | ----------------------------------- |
| `exploracao` (F3) | `axon-{type}-{slug}` (legacy)       |
| Todas as outras   | `axon-{area_id}-{type}-{slug}`      |

Onde `{type}` ∈ {`area`, `dom`, `asn`, `ssn`, `term`}.

A validação em `loadAxonManifest()` emite **warning** se uma área não-`exploracao` tiver IDs sem o prefixo `axon-{area_id}-`, mas não aborta — fica a cargo do curador resolver.

## 5. Receita: como adicionar uma nova área (4 passos)

1. **Exportar a tabela Axon** da área no Axon Petrobras (XLSX).
2. **Transformar o XLSX em JSON** seguindo este schema. Copie [data/axon/_template.json](../data/axon/_template.json) para `data/axon/<area-id>.json` e preencha cada lista (`areas`, `domains`, `subjects`, `subsubjects`, `terms`). **Use IDs com o prefixo `axon-<area-id>-`** (§4).
3. **Atualizar o manifest** em [data/axon/manifest.json](../data/axon/manifest.json):
   - Mover a entrada de `future_areas_planned` para `areas`.
   - Setar `status: "ingested"`, preencher `file`, `ingested_in`, `source`, e `stats`.
4. **Regenerar o pipeline**: `node scripts/generate.js`. O loader pega a nova área automaticamente.

Após esses 4 passos, o curador deve revisar com a checklist abaixo (§6) **antes** de fazer commit.

## 6. Checklist do curador antes de ingerir (10 pontos)

1. [ ] Todas as entradas têm `id`, `name_pt`, `axon_type`, `definition_pt` preenchidos.
2. [ ] IDs seguem a convenção `axon-<area-id>-<type>-<slug>` (exceto `exploracao`, legacy).
3. [ ] Cada entrada não-Area tem `parent_id` apontando para um ID existente no mesmo arquivo.
4. [ ] Não há IDs duplicados dentro do arquivo da área.
5. [ ] Não há colisão de ID com glossários de outras áreas já ingeridas (verificar contra `data/axon/*.json`).
6. [ ] `axon_path` é coerente com `parent_id` (caminho hierárquico humano correto).
7. [ ] `definition_pt_canonical` foi revisada pelo curador (não é cópia automática do export, exceto quando original já está bom).
8. [ ] Termos com `links_to_existing` apontam para IDs reais do entity-graph (verificar com `jq '.nodes[].id' data/entity-graph.json`).
9. [ ] `manifest.json` tem `stats.{areas,domains,subjects,subsubjects,terms}` batendo com o conteúdo do arquivo (o loader avisa drift, mas é melhor já estar correto).
10. [ ] `node scripts/generate.js` roda limpo e os tests do entity-graph passam (`node --test tests/`).

## 7. Política de retrocompatibilidade

- **Nunca renomear** IDs já presentes em `data/axon/exploracao.json` — outros arquivos do projeto referenciam-nos (ver [data/well-attributes.json](../data/well-attributes.json) §scope).
- **Nunca alterar** a topologia do entity-graph como efeito colateral de uma mudança Axon — F9 é puro scaffolding e foi verificado byte-a-byte que `data/entity-graph.json` continua com os mesmos node IDs após a refatoração.
- Mudanças no schema acima exigem bump de `version` no arquivo da área e nota no [CHANGELOG.md](../CHANGELOG.md).
