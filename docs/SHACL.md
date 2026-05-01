# SHACL Formal Validation — Geolytics Dictionary

## O que e SHACL

**SHACL** (Shapes Constraint Language, W3C Recommendation 2017) e a linguagem padrao para descrever e validar a estrutura de grafos RDF. Funciona como um "schema" para dados Linked Data: define o que e obrigatorio, quais valores sao permitidos e quais restricoes de cardinalidade devem ser satisfeitas.

SHACL complementa OWL (que descreve _o que existe_) com restricoes _operacionais_ (o que _deve_ existir em cada instancia para os dados serem validos). A diferenca principal:

| OWL | SHACL |
|---|---|
| Descreve o modelo conceitual | Valida instancias contra restricoes |
| Raciocinio (inferencia) | Validacao (conformidade) |
| Open World Assumption | Closed World Assumption (por padrao) |
| Axiomas e hierarquias | Shapes e constraints |

## Por que usamos SHACL neste projeto

O dicionario Geolytics serializa seu grafo de entidades em `data/geolytics.ttl` e serve os dados via `api/v1/`. As restricoes SHACL em `data/geolytics-shapes.ttl` garantem:

1. **Consistencia de vocabulario controlado** — `geo:tipoPoco` so pode ter valores ANP canonicos; `geo:regimeContratual` so pode ser Concessao, Partilha ou CessaoOnerosa.
2. **Cardinalidade** — todo poço (`geo:Poco`) deve ter exactamente um operador e um bloco associado.
3. **Desambiguacao critica** — `geo:Reserva` (SPE-PRMS: 1P/2P/3P) e `geo:ReservaAmbiental` (REBIO/RPPN) sao declaradas **disjuntas**; o validador rejeita qualquer instancia que pertenca a ambas.
4. **Padroes de URI e literal** — o `osduKind` segue o formato `opendes:osdu:master-data--TypeName:major.minor.patch`; URIs OSDU usam o namespace canonico `https://w3id.org/osdu#`.
5. **Cobertura semantica** — `geo:geocoverage` so aceita valores da lista de 8 camadas documentadas.

## Arquivos

| Arquivo | Descricao |
|---|---|
| `data/geolytics-shapes.ttl` | 16 NodeShapes SHACL |
| `data/geolytics-vocab.ttl` | Vocabulario OWL minimo de apoio (classes + propriedades) |
| `scripts/validate-shacl.py` | Validador Python (pyshacl) — recomendado |
| `scripts/validate-shacl.js` | Wrapper Node.js (rdf-validate-shacl ou delega ao Python) |
| `scripts/requirements.txt` | Dependencias Python (`pyshacl>=0.25.0`, `rdflib>=7.0.0`) |

## Como rodar

### Python (recomendado)

```bash
# Instalar dependencias (uma vez)
pip install -r scripts/requirements.txt
# ou
python3 -m pip install --user pyshacl rdflib

# Validar
python scripts/validate-shacl.py

# Opcoes adicionais
python scripts/validate-shacl.py --verbose          # relatorio SHACL completo (ingles)
python scripts/validate-shacl.py --no-ontology      # sem vocabulario OWL de apoio
python scripts/validate-shacl.py --data path.ttl    # dados alternativos
python scripts/validate-shacl.py --shapes path.ttl  # shapes alternativas
```

### Node.js

```bash
# Instalar rdf-validate-shacl (opcional)
npm install rdf-validate-shacl n3

# Executar
node scripts/validate-shacl.js
```

Se `rdf-validate-shacl` nao estiver instalado, o script Node.js delega automaticamente para `python scripts/validate-shacl.py`.

## Relatorio de saida

O validador Python emite um relatorio em PT-BR. Exemplo de saida conforme:

```
======================================================================
Validador SHACL — Geolytics Dictionary
======================================================================
  Dados   : data/geolytics.ttl
  Shapes  : data/geolytics-shapes.ttl
  Vocabulario OWL : data/geolytics-vocab.ttl (142 triplas)
  Triplas no grafo de dados: 1836

----------------------------------------------------------------------
RESULTADO: CONFORME
O grafo de dados esta em conformidade com todos os shapes SHACL.
----------------------------------------------------------------------
```

Saida nao conforme lista cada violacao com: no foco, propriedade, valor invalido e mensagem em PT-BR.

O script retorna **codigo de saida 0** se conforme, **1** se houver violacoes.

## Shapes disponiveis

| Shape | Alvo | Restricoes principais |
|---|---|---|
| `geo:WellShape` | `geo:Poco` | `tipoPoco` enum ANP, `operador` 1..1, `bloco` 1..1 |
| `geo:BlocoShape` | `geo:Bloco` | `regimeContratual` enum 3 valores, `bacia` 1..1 |
| `geo:ReservaShape` | `geo:Reserva` | `categoriaSPEPRMS` in {1P,2P,3P,C1C,C2C,C3C}, disjunto de `ReservaAmbiental` |
| `geo:OSDUKindShape` | subjects de `geo:osduKind` | padrao `^opendes:osdu:master-data--[A-Z]...` |
| `geo:AcronymShape` | `geo:Acronym` | `sigla` obrigatorio, ao menos `expansion_pt` ou `expansion_en`, `category` enum |
| `geo:GSOClassShape` | `geo:GSOClass` | `owlUri` IRI com dominio `loop3d.org` |
| `geo:GeocoverageShape` | subjects de `geo:geocoverage` | valores in {layer1, layer1b, ..., layer7} |
| `geo:OntopetroClassShape` | `geo:OntopetroClass` | `classId` padrao `^C[0-9]{3}$`, ao menos um `source` |
| `geo:EntityClassShape` | `owl:Class` com `geo:entityType` | `skos:prefLabel` >= 2, `skos:definition` >= 1, `entityType` enum 7 valores |
| `geo:ObjectPropertyShape` | `owl:ObjectProperty` | `rdfs:label` >= 2, `domain` obrigatorio, `range` obrigatorio |
| `geo:SameAsLinkShape` | subjects de `owl:sameAs` | objeto deve ser IRI (nao literal) |
| `geo:PrefLabelUniquenessShape` | subjects de `skos:prefLabel` | no maximo 4 prefLabels |
| `geo:OperadorShape` | `geo:Operador` | `skos:prefLabel` obrigatorio |
| `geo:BaciaSedimentarShape` | `geo:BaciaSedimentar` | `skos:prefLabel` e `skos:definition` obrigatorios |
| `geo:OsduUriPatternShape` | subjects de `owl:sameAs` | links OSDU usam `https://w3id.org/osdu#` |
| `geo:ContratacaoShape` | `geo:ContratoEP` | `skos:prefLabel` e `skos:definition` obrigatorios |

## Como adicionar uma nova shape

### Recipe com diff

Suponha que voce quer adicionar uma shape para validar instancias de `geo:Formacao`:

**1. Declare a classe no vocabulario OWL** (se nao existir):

```diff
--- a/data/geolytics-vocab.ttl
+++ b/data/geolytics-vocab.ttl
+geo:Formacao a owl:Class ;
+    rdfs:label "Formacao Geologica"@pt ;
+    rdfs:label "Geological Formation"@en ;
+    rdfs:comment "Unidade litoestratigrafica formal." @pt ;
+    owl:sameAs osdu:GeologicalFormation .
```

**2. Adicione a shape em `data/geolytics-shapes.ttl`**:

```diff
--- a/data/geolytics-shapes.ttl
+++ b/data/geolytics-shapes.ttl
+geo:FormacaoShape a sh:NodeShape ;
+    rdfs:label "Forma de Formacao Geologica"@pt ;
+    rdfs:label "Geological Formation Shape"@en ;
+    sh:targetClass geo:Formacao ;
+    sh:property [
+        sh:path skos:prefLabel ;
+        sh:minCount 1 ;
+        sh:message "Formacao deve ter ao menos um skos:prefLabel."@pt ;
+    ] ;
+    sh:property [
+        sh:path geo:geocoverage ;
+        sh:minCount 1 ;
+        sh:message "Formacao deve ter geo:geocoverage declarado."@pt ;
+    ] .
```

**3. Valide** para confirmar que a shape e valida Turtle e que o grafo atual nao viola a nova restricao:

```bash
python scripts/validate-shacl.py
```

**4. Incremente o contador de shapes** no comentario do cabecalho do arquivo se quiser manter documentacao inline.

### Regras de boas praticas

- Use `sh:message` sempre em PT-BR com `@pt`. Facilita a leitura do relatorio.
- Para enums use `sh:in (...)` com literais `xsd:string` — nao use IRIs como valores de enum.
- Para cardinalidade de instancias use `sh:minCount` / `sh:maxCount` dentro de `sh:property`.
- Para disjuncao use `sh:not [ sh:class ... ]` no NodeShape (nao em sh:property).
- Para padroes de string use `sh:pattern` com expressao regular PCRE — teste o regex antes.
- Nao use `sh:closed true` em shapes que targetam `owl:Class` schema — isso geraria falsos positivos nas declaracoes de classe do TTL.

## Relacao com o validador JavaScript existente

O projeto ja possui `scripts/gso-extract.js` e outros scripts de processamento. O validador SHACL e **complementar**, nao substituto:

- Os scripts JS geram os arquivos `.ttl` e `.json`.
- O validador SHACL verifica a **conformidade** dos arquivos `.ttl` gerados contra as restricoes formais.

O fluxo recomendado no pipeline de CI e:

```
node scripts/generate.js
python scripts/validate-shacl.py  # ou: node scripts/validate-shacl.js
```

Se o validador retornar codigo 1, o pipeline deve falhar e o artefato nao deve ser publicado.

## Referencia

- W3C SHACL Spec: https://www.w3.org/TR/shacl/
- pyshacl: https://github.com/RDFLib/pySHACL
- rdf-validate-shacl: https://github.com/zazuko/rdf-validate-shacl
- SKOS Reference: https://www.w3.org/TR/skos-reference/
