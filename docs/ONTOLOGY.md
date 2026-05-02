# Referencia de Classes e Propriedades — Ontologia Geolytics

> Gerado automaticamente por `scripts/build-ontology-doc.js` em 2026-05-01.
> Nao edite manualmente — execute `node scripts/build-ontology-doc.js` para regenerar.

Este documento lista todas as classes, propriedades, relacoes e instancias formais
dos modulos de ontologia do GeoBrain, extraidas diretamente dos arquivos JSON canonicos.

---

## Indice de modulos

| Modulo | Fonte | Classes | Propriedades | Relacoes | Instancias |
|---|---|---|---|---|---|
| Ontopetro (base) | `data/ontopetro.json` | 20 | 20 | 20 | 10 |
| Geomecanica MEM P2.7 | `data/geomechanics.json` | 26 | 22 | 12 | 6 |
| Sismico Aquisicao P2.8 | `data/seismic-acquisition.json` | 20 | 17 | 9 | 3 |
| Sismico Processamento P2.8 | `data/seismic-processing.json` | 18 | 13 | 7 | 3 |
| Sismico Inversao e Atributos P2.8 | `data/seismic-inversion-attributes.json` | 26 | 15 | 9 | 4 |

---

## Ontopetro — Ontologia Formal de Geociencias de Petroleo

Versao: `1.0.0`. Fontes: GeoCore, PPDM, GDGEO, SPE-PRMS, ANP, OSDU.

**Totais**: 20 classes, 20 propriedades, 20 relacoes, 10 instancias.

### Classes

| ID | Nome PT | Nome EN | Superclasse | Dominio | Descricao (resumo) | Fontes |
|---|---|---|---|---|---|---|
| C001 | BaciaSedimentar | Sedimentary Basin | GeologicalObject | Geologia Estrutural | Depressão crustal onde sedimentos se acumulam ao longo do tempo geológico | GeoCore |
| C002 | FormacaoGeologica | Geological Formation | GeologicalObject | Estratigrafia | Unidade litoestratigráfica nomeada e mapeável | PPDM, GeoCore |
| C003 | RochaReservatorio | Reservoir Rock | FormacaoGeologica | Reservatório | Rocha porosa e permeável capaz de armazenar hidrocarbonetos | GDGEO, GeoCore |
| C004 | RochaCapacitante | Cap Rock | FormacaoGeologica | Reservatório | Rocha de baixa permeabilidade que sela o reservatório (cap rock) | GeoCore |
| C005 | RochaGeneradora | Source Rock | FormacaoGeologica | Geoquímica | Rocha rica em matéria orgânica geradora de HC (source rock) | GeoCore |
| C006 | TrapaPetrolifera | Petroleum Trap | GeologicalObject | Sistemas Petrolíferos | Configuração geológica que permite acúmulo de HC | PPDM |
| C007 | SistemaPetrolifero | Petroleum System | GeologicalSystem | Sistemas Petrolíferos | Conjunto rocha-geradora, migração, reservatório, capa e trapa | PPDM, GeoCore |
| C008 | Acumulacao | Hydrocarbon Accumulation | GeologicalObject | Reservatório | Volume de HC contido em armadilha com dimensões definidas | PPDM |
| C009 | Campo | Field | GeologicalObject | Produção | Área geográfica delimitada contendo uma ou mais acumulações | ANP, PPDM |
| C010 | Bloco | Exploration Block | AdministrativeObject | Regulatório | Área definida em concessão ou partilha para atividade E&P | ANP |
| C011 | Poco | Well | WellObject | Poços | Perfuração realizada para exploração, avaliação ou produção | PPDM, OSDU |
| C012 | Testemunho | Core Sample | SampleObject | Amostragem | Amostra cilíndrica de rocha extraída durante perfuração | GDGEO |
| C013 | PerfilDePoco | Well Log | WellLog | Petrofísica | Medição contínua de propriedades físicas ao longo do poço | PPDM |
| C014 | SismoEstratigrafia | Seismic Stratigraphy | InterpretationObject | Geofísica | Análise estratigráfica baseada em dados sísmicos | Petrolês, GeoCore |
| C015 | Horizonte | Seismic Horizon | SeismicObject | Geofísica | Superfície refletora identificada em dados sísmicos | PPDM |
| C016 | FalhaGeologica | Geological Fault | StructuralObject | Geologia Estrutural | Descontinuidade tectônica com deslocamento relativo das camadas | GeoCore |
| C017 | Play | Play | ExplorationObject | Exploração | Combinação de elementos petrolíferos com potencial exploratório | PPDM |
| C018 | Prospecto | Prospect | ExplorationObject | Exploração | Área estrutural/estratigráfica com potencial para acumulação | PPDM |
| C019 | Recurso | Resource | EconomicObject | Reservas/Recursos | Volume de HC com grau variável de certeza geológica | ANP, SPE-PRMS |
| C020 | Reserva | Reserve | EconomicObject | Reservas/Recursos | Volume de HC tecnicamente recuperável e economicamente viável | ANP, SPE-PRMS |

### Propriedades

| ID | Nome | Tipo | Dominio | Range / Unidade | Obrigatorio |
|---|---|---|---|---|---|
| P001 | nomeFormacao | DatatypeProperty |  | xsd:string | nao |
| P002 | idadeCronoestratigrafica | DatatypeProperty |  | xsd:string | nao |
| P003 | litologia | DatatypeProperty |  | xsd:string | nao |
| P004 | porosidade | DatatypeProperty |  | xsd:float | nao |
| P005 | permeabilidade | DatatypeProperty |  | xsd:float | nao |
| P006 | saturacaoDeOleo | DatatypeProperty |  | xsd:float | nao |
| P007 | profundidadeTopReservatorio | DatatypeProperty |  | xsd:float | nao |
| P008 | contatoOleoAgua | DatatypeProperty |  | xsd:float | nao |
| P009 | volumeOriginalOleo | DatatypeProperty |  | xsd:float | nao |
| P010 | fatorDeRecuperacao | DatatypeProperty |  | xsd:float | nao |
| P011 | coordenadaX | DatatypeProperty |  | xsd:float | nao |
| P012 | coordenadaY | DatatypeProperty |  | xsd:float | nao |
| P013 | datumGeodetico | DatatypeProperty |  | xsd:string | nao |
| P014 | grauAPI | DatatypeProperty |  | xsd:float | nao |
| P015 | teorDeCarbono | DatatypeProperty |  | xsd:float | nao |
| P016 | janelaDeOleo | DatatypeProperty |  | xsd:string | nao |
| P017 | tipoDeTrapa | DatatypeProperty |  | xsd:string | nao |
| P018 | amplitudeSismica | DatatypeProperty |  | xsd:float | nao |
| P019 | nomePoco | DatatypeProperty |  | xsd:string | nao |
| P020 | tipoPoco | DatatypeProperty |  | xsd:string | nao |

### Relacoes

| ID | Nome | Dominio (classe) | Range (classe) | Cardinalidade |
|---|---|---|---|---|
| R001 | pertenceA | FormacaoGeologica | BaciaSedimentar | N:1 |
| R002 | compostoPor | BaciaSedimentar | FormacaoGeologica | 1:N |
| R003 | constitui | RochaReservatorio | TrapaPetrolifera | N:M |
| R004 | selaReservatorio | RochaCapacitante | RochaReservatorio | N:M |
| R005 | geraHidrocarbonetos | RochaGeneradora | Hidrocarboneto | 1:N |
| R006 | contem | TrapaPetrolifera | Acumulacao | 1:N |
| R007 | fazParteDe | Acumulacao | Campo | N:1 |
| R008 | localizadoEm | Campo | BaciaSedimentar | N:1 |
| R009 | associadoA | Prospecto | Play | N:1 |
| R010 | perfuradoEm | Poco | Campo | N:1 |
| R011 | intercepta | Poco | FormacaoGeologica | N:M |
| R012 | amostradoPor | FormacaoGeologica | Testemunho | 1:N |
| R013 | medidoPor | FormacaoGeologica | PerfilDePoco | 1:N |
| R014 | integraA | SistemaPetrolifero | BaciaSedimentar | N:1 |
| R015 | localizadoEmGeo | Poco | Bloco | N:1 |
| R016 | categorizadoEm | Recurso | SPE_PRMS_Categoria | N:1 |
| R017 | derivaDe | Reserva | Recurso | 1:1 |
| R018 | imageadoPor | Horizonte | LevantamentoSismico | N:1 |
| R019 | caracterizadoPor | Acumulacao | FluidoDeReservatorio | 1:N |
| R020 | reguladoPor | Bloco | ANP | N:1 |

### Instancias

| ID | Nome | Tipo (classe) | Descricao |
|---|---|---|---|
| I001 | Bacia de Santos | BaciaSedimentar |  |
| I002 | Bacia de Campos | BaciaSedimentar |  |
| I003 | Bacia do Solimões | BaciaSedimentar |  |
| I004 | Formação Barra Velha | FormacaoGeologica |  |
| I005 | Formação Macabu | FormacaoGeologica |  |
| I006 | Campo de Búzios | Campo |  |
| I007 | Campo de Tupi | Campo |  |
| I008 | Pré-sal da Bacia de Santos | TrapaPetrolifera |  |
| I009 | Play Carbonatos Pré-sal | Play |  |
| I010 | SP Lagoa Feia-Macabu | SistemaPetrolifero |  |


## Geomecanica MEM (P2.7)

Modulo de Mecanica de Rochas e Modelo de Terra Mecanico (MEM 1D). Ver `docs/GEOMECHANICS.md` para documentacao completa.

**Totais**: 26 classes, 22 propriedades, 12 relacoes, 6 instancias.

### Classes

| ID | Nome PT | Nome EN | Superclasse | Dominio | Descricao (resumo) | Fontes |
|---|---|---|---|---|---|---|
| GM001 | TensorDeTensao | StressTensor | MathematicalObject |  | Symmetric 3x3 second-rank tensor describing the state of stress at a point in a ... | Fjaer et al. 2008 Ch.2, Zoback 2010 Ch.1 |
| GM002 | TensaoPrincipal | PrincipalStress | StressTensor |  | One of the three principal (normal) stresses acting on planes where shear stress... | Fjaer et al. 2008 §2.1, Zoback 2010 §1.2 |
| GM003 | TensaoDeCisalhamento | ShearStress | StressTensor |  | Stress component acting parallel to a plane. In the Mohr circle representation, ... | Fjaer et al. 2008 §2.3, Zoback 2010 §4.1 |
| GM004 | PressaoDePoros | PorePressure | FluidPressure |  | Pressure of pore fluid in connected pore space. Controls effective stress via Te... | Fjaer et al. 2008 §2.5, Zoback 2010 §2.1, Eaton B.A. JPT 1975 |
| GM005 | JanelaDeLama | MudWindow | DrillingConstraint |  | Safe drilling mud weight window bounded below by pore pressure (collapse/kick ri... | Fjaer et al. 2008 §10.1, Zoback 2010 §9.1 |
| GM006 | CirculoDeMohr | MohrCircle | GraphicalRepresentation |  | Graphical representation of the stress state on a plane at a given orientation. ... | Fjaer et al. 2008 §3.1, ISRM Suggested Methods 1978 |
| GM007 | CriterioDeRuptura | FailureCriterion | RockMechanicsModel |  | Mathematical condition defining the stress state at which rock fails. Two princi... | Fjaer et al. 2008 §3.3, Hoek & Brown 2019 |
| GM008 | CriterioMohrCoulomb | MohrCoulombCriterion | FailureCriterion |  | Linear shear failure criterion: tau_f = c + sigma_n * tan(phi), where c is cohes... | Fjaer et al. 2008 §3.3, Zoback 2010 §4.2 |
| GM009 | CriterioHoekBrown | HoekBrownCriterion | FailureCriterion |  | Curved empirical criterion for rock masses: sigma_1 = sigma_3 + sigma_ci * (m_b ... | Hoek & Brown 2019, Hoek E. et al. Rock Mechanics and Rock Engineering 2002 |
| GM010 | ModeloMecanicoTerra | MechanicalEarthModel | GeomechanicsModel |  | Integrated quantitative description of the mechanical state of a reservoir and s... | Fjaer et al. 2008 §10.1, Zoback 2010 §9.1, Plumb R. et al. SPE 65118 2000 |
| GM011 | ModeloMecanicoTerra1D | MechanicalEarthModel1D | MechanicalEarthModel |  | One-dimensional MEM built along a wellbore path. Depth functions of pore pressur... | Fjaer et al. 2008 §10.2, Zoback 2010 §9.2 |
| GM012 | ModeloMecanicoTerra3D | MechanicalEarthModel3D | MechanicalEarthModel |  | Three-dimensional MEM integrating seismic, well log, and production data into a ... | Zoback 2010 §12.1, Fjaer et al. 2008 §10.4 |
| GM013 | PropriedadeMecanicaRocha | RockMechProperty | PhysicalProperty |  | Mechanical property of intact rock or rock mass used in geomechanical modelling.... | Fjaer et al. 2008 §2.1, Zoback 2010 §1.3, ISRM Suggested Methods |
| GM014 | ResistenciaCompressaoUniaxial | UCS | RockMechProperty |  | Uniaxial Compressive Strength (UCS) — the maximum axial stress a cylindrical roc... | Fjaer et al. 2008 §4.1, ISRM Suggested Methods 1978, Zoback 2010 §5.1 |
| GM015 | ModuloDeYoung | YoungModulus | RockMechProperty |  | Young's modulus (E) — ratio of axial stress to axial strain in the elastic regim... | Fjaer et al. 2008 §2.2, Zoback 2010 §1.3 |
| GM016 | RazaoDePoisson | PoissonRatio | RockMechProperty |  | Poisson's ratio (nu) — ratio of lateral strain to axial strain under axial loadi... | Fjaer et al. 2008 §2.2, Zoback 2010 §1.3 |
| GM017 | CoeficienteDeBiot | BiotCoefficient | RockMechProperty |  | Biot coefficient (alpha) — poroelastic coupling parameter relating pore pressure... | Biot M.A. Journal of Applied Physics 1941, Fjaer et al. 2008 §2.7 |
| GM018 | ModuloVolumetrico | BulkModulus | RockMechProperty |  | Bulk modulus (K) — resistance of rock to volumetric compression. K = E / (3*(1 -... | Fjaer et al. 2008 §2.2, Zoback 2010 §1.3 |
| GM019 | ModuloDeCisalhamento | ShearModulus | RockMechProperty |  | Shear modulus (G) — resistance of rock to shear deformation. G = E / (2*(1 + nu)... | Fjaer et al. 2008 §2.2, Zoback 2010 §1.3 |
| GM020 | ClassificacaoMacicoRochoso | RockMassRating | RockClassificationScheme |  | Bieniawski (1989) RMR system classifying rock masses on a scale 0-100 based on s... | Bieniawski Z.T. Engineering Rock Mass Classifications 1989, Hoek & Brown 2019 |
| GM021 | IndiceGeologicoDeResistencia | GSI | RockClassificationScheme |  | Geological Strength Index (Hoek 1994) — quantifies rock mass quality for use in ... | Hoek E. Rock Engineering 1994, Hoek & Brown 2019 |
| GM022 | IndiceQualidadeRocha | RQD | RockClassificationScheme |  | Rock Quality Designation (Deere 1963) — percentage of core pieces longer than 10... | Deere D.U. SMFE 1963, ISRM Suggested Methods, Bieniawski 1989 |
| GM023 | Anisotropia | Anisotropy | RockMechProperty |  | Directional dependence of mechanical properties in a rock mass. Transverse isotr... | Fjaer et al. 2008 §6.1, Thomsen L. Geophysics 1986, Zoback 2010 §1.3 |
| GM024 | Fragilidade | Brittleness | RockMechProperty |  | Tendency of rock to fail suddenly without significant plastic deformation. High ... | Rickman R. et al. SPE 115258 2008, Fjaer et al. 2008 §4.2, Zoback 2010 §7.1 |
| GM025 | RegimeTensionalDeAnderson | AndersonStressRegime | GeomechanicsClassification |  | Anderson (1951) classification of tectonic stress regimes based on the relative ... | Anderson E.M. 1951, Zoback 2010 §1.2, Fjaer et al. 2008 §2.4 |
| GM026 | PocoGeomecanico | Wellbore | DrillHole |  | Cylindrical cavity in rock mass whose stability is governed by the stress concen... | Fjaer et al. 2008 §9.1, Zoback 2010 §8.1 |

### Propriedades

| ID | Nome | Tipo | Dominio | Range / Unidade | Obrigatorio |
|---|---|---|---|---|---|
| GP001 | youngModulus |  | RockMechProperty | xsd:decimal | nao |
| GP002 | ucs |  | UCS | xsd:decimal | nao |
| GP003 | poissonRatio |  | RockMechProperty | xsd:decimal | nao |
| GP004 | porePressureGradient |  | PorePressure | xsd:decimal | nao |
| GP005 | biotCoefficient |  | BiotCoefficient | xsd:decimal | nao |
| GP006 | bulkModulus |  | RockMechProperty | xsd:decimal | nao |
| GP007 | shearModulus |  | RockMechProperty | xsd:decimal | nao |
| GP008 | sigma1 |  | StressTensor | xsd:decimal | nao |
| GP009 | sigma2 |  | StressTensor | xsd:decimal | nao |
| GP010 | sigma3 |  | StressTensor | xsd:decimal | nao |
| GP011 | sv |  | PrincipalStress | xsd:decimal | nao |
| GP012 | sHmax |  | PrincipalStress | xsd:decimal | nao |
| GP013 | shmin |  | PrincipalStress | xsd:decimal | nao |
| GP014 | cohesion |  | MohrCoulombCriterion | xsd:decimal | nao |
| GP015 | frictionAngle |  | MohrCoulombCriterion | xsd:decimal | nao |
| GP016 | rmrScore |  | RockMassRating | xsd:decimal | nao |
| GP017 | gsiValue |  | GSI | xsd:decimal | nao |
| GP018 | rqdValue |  | RQD | xsd:decimal | nao |
| GP019 | brittlenessIndex |  | Brittleness | xsd:decimal | nao |
| GP020 | mudWeightLower |  | MudWindow | xsd:decimal | nao |
| GP021 | mudWeightUpper |  | MudWindow | xsd:decimal | nao |
| GP022 | stressRegime |  | AndersonStressRegime | xsd:string | nao |

### Relacoes

| ID | Nome | Dominio (classe) | Range (classe) | Cardinalidade |
|---|---|---|---|---|
| GR001 | induces_failure | StressTensor | RockMechProperty |  |
| GR002 | controls_mud_window | PorePressure | MudWindow |  |
| GR003 | triggers_sand_production | StressTensor | RockMechProperty |  |
| GR004 | affects_wellbore_stability | MechanicalEarthModel | Wellbore |  |
| GR005 | caused_by | MudWindow | AndersonStressRegime |  |
| GR006 | derivative_with_respect_to | RockMechProperty | RockMechProperty |  |
| GR007 | bounds_drilling_window | PorePressure | MudWindow |  |
| GR008 | calibrated_by | MechanicalEarthModel1D | Wellbore |  |
| GR009 | constrained_by | PrincipalStress | FailureCriterion |  |
| GR010 | derived_from_sonic | RockMechProperty | RockMechProperty |  |
| GR011 | input_to_mem | RockMechProperty | MechanicalEarthModel |  |
| GR012 | governs_fracture_propagation | PrincipalStress | MudWindow |  |

### Instancias

| ID | Nome | Tipo (classe) | Descricao |
|---|---|---|---|
| mem-buzios-1d | Buzios Field 1D MEM — Conceptual Example | MechanicalEarthModel1D | Illustrative 1D MEM for a pre-salt carbonate well in the Santos Basin, offshore  |
| failure-mohr-coulomb | Mohr-Coulomb Failure — Sandstone Example | MohrCoulombCriterion | Example application of Mohr-Coulomb to a typical shallow-marine sandstone. Cohes |
| hoek-brown-carbonate | Hoek-Brown — Fractured Carbonate Example | HoekBrownCriterion | Hoek-Brown criterion applied to a fractured carbonate reservoir with moderate GS |
| normal-faulting-regime | Normal Faulting Regime — Santos Basin | AndersonStressRegime | Typical extensional tectonic setting of the Santos Basin passive margin. Vertica |
| mud-window-depleted-reservoir | Narrow Mud Window — Depleted Reservoir Example | MudWindow | A depleted reservoir (Pp reduced by 20-30% of initial pressure) causes Shmin to  |
| rqd-gsi-rock-mass | Rock Mass Classification Chain — GSI from RQD and RMR | GSI | Demonstration of the classification chain: RQD -> RMR -> GSI -> Hoek-Brown param |


## Sismico — Aquisicao (P2.8)

Referencias: Yilmaz (2001), Sheriff & Geldart (1995). Ver `docs/SEISMIC.md` para documentacao completa.

**Totais**: 20 classes, 17 propriedades, 9 relacoes, 3 instancias.

### Classes

| ID | Nome PT | Nome EN | Superclasse | Dominio | Descricao (resumo) | Fontes |
|---|---|---|---|---|---|---|
| SeismicSurvey | Levantamento Sismico | SeismicSurvey | owl:Thing | seismic_acquisition | A controlled experiment in which seismic energy is injected into the Earth and t... | Yilmaz 2001, Sheriff & Geldart 1995, OSDU |
| LandSurvey | Levantamento Terrestre | LandSurvey | SeismicSurvey | seismic_acquisition | Onshore seismic survey in which sources (vibroseis, dynamite) and receivers (geo... | Yilmaz 2001, Sheriff & Geldart 1995 |
| MarineSurvey | Levantamento Marinho | MarineSurvey | SeismicSurvey | seismic_acquisition | Offshore towed-streamer survey in which a vessel tows one or more hydrophone cab... | Yilmaz 2001, Sheriff & Geldart 1995 |
| OBNSurvey | Levantamento Sismico de Fundo Oceanico (No) | OBNSurvey | SeismicSurvey | seismic_acquisition | Ocean-Bottom Node survey: autonomous 4C (Vx, Vy, Vz + hydrophone) sensor package... | Sheriff & Geldart 1995 |
| OBSSurvey | Levantamento Sismica de Fundo Oceanico (cabo) | OBSSurvey | SeismicSurvey | seismic_acquisition | Ocean-Bottom Seismometer/Cable survey: 4C sensors deployed on cables laid on the... | Sheriff & Geldart 1995 |
| Source | Fonte Sismica | Source | owl:Thing | seismic_acquisition | Device or process that generates seismic energy and injects it into the ground o... | Yilmaz 2001, Sheriff & Geldart 1995 |
| Airgun | Pistola de Ar | Airgun | Source | seismic_acquisition | Marine seismic source that releases compressed air (typically 2000 psi) into the... | Sheriff & Geldart 1995 |
| Vibroseis | Vibrosseis | Vibroseis | Source | seismic_acquisition | Land seismic source that emits a swept-frequency (chirp) signal via a vibrating ... | Yilmaz 2001 |
| Dynamite | Explosivo | Dynamite | Source | seismic_acquisition | Explosive seismic source detonated in a shallow drill hole to generate a broad-b... | Sheriff & Geldart 1995 |
| SparkerArray | Array de Sparker | SparkerArray | Source | seismic_acquisition | High-resolution marine source using electrical discharge to vaporise water and g... | Sheriff & Geldart 1995 |
| Receiver | Receptor Sismico | Receiver | owl:Thing | seismic_acquisition | Sensor that converts mechanical ground or water motion into an electrical signal... | Yilmaz 2001 |
| Hydrophone | Hidrofone | Hydrophone | Receiver | seismic_acquisition | Pressure-sensitive piezoelectric sensor towed in marine streamers. Records scala... | Sheriff & Geldart 1995 |
| Geophone | Geofone | Geophone | Receiver | seismic_acquisition | Velocity-sensitive electromagnetic sensor planted on the ground surface. Natural... | Yilmaz 2001 |
| AccelerometerMEMS | Acelerometro MEMS | AccelerometerMEMS | Receiver | seismic_acquisition | Micro-Electro-Mechanical System accelerometer used in nodal acquisition systems.... | Sheriff & Geldart 1995 |
| OBC | Cabo de Fundo Oceanico | OBC | Receiver | seismic_acquisition | Ocean-Bottom Cable: multi-component cable laid on the sea floor carrying colloca... | Sheriff & Geldart 1995 |
| AcquisitionGeometry | Geometria de Aquisicao | AcquisitionGeometry | owl:Thing | seismic_acquisition | Spatial arrangement of sources and receivers defining illumination, fold, offset... | Yilmaz 2001 |
| StreamerLayout | Configuracao de Streamer | StreamerLayout | AcquisitionGeometry | seismic_acquisition | Marine geometry in which one or more hydrophone cables (streamers) are towed beh... | Yilmaz 2001 |
| NodalLayout | Configuracao Nodal | NodalLayout | AcquisitionGeometry | seismic_acquisition | Land or OBN geometry employing autonomous wireless nodes deployed in a regular o... | Sheriff & Geldart 1995 |
| SamplingParameters | Parametros de Amostragem | SamplingParameters | owl:Thing | seismic_acquisition | Temporal and spatial sampling parameters that define the recorded wavefield fide... | Yilmaz 2001, Sheriff & Geldart 1995 |
| Aliasing | Aliasing / Dobramento Espectral | Aliasing | owl:Thing | seismic_acquisition | Artifact arising when the sampling interval violates the Nyquist criterion, caus... | Yilmaz 2001 |

### Propriedades

| ID | Nome | Tipo | Dominio | Range / Unidade | Obrigatorio |
|---|---|---|---|---|---|
| samplingInterval | samplingInterval |  |  | xsd:decimal | nao |
| recordLength | recordLength |  |  | xsd:decimal | nao |
| fold | fold |  |  | xsd:integer | nao |
| offset | offset |  |  | xsd:decimal | nao |
| NyquistFrequency | NyquistFrequency |  |  | xsd:decimal | nao |
| signalBandwidth | signalBandwidth |  |  | xsd:string | nao |
| peakFrequency | peakFrequency |  |  | xsd:decimal | nao |
| operatingPressure | operatingPressure |  |  | xsd:decimal | nao |
| sweepFrequencyMin | sweepFrequencyMin |  |  | xsd:decimal | nao |
| sweepFrequencyMax | sweepFrequencyMax |  |  | xsd:decimal | nao |
| sweepLength | sweepLength |  |  | xsd:decimal | nao |
| streamerLength | streamerLength |  |  | xsd:decimal | nao |
| numberOfStreamers | numberOfStreamers |  |  | xsd:integer | nao |
| gridSpacing | gridSpacing |  |  | xsd:string | nao |
| waterDepth | waterDepth |  |  | xsd:decimal | nao |
| receiverSensitivity | receiverSensitivity |  |  | xsd:decimal | nao |
| surveyArea | surveyArea |  |  | xsd:decimal | nao |

### Relacoes

| ID | Nome | Dominio (classe) | Range (classe) | Cardinalidade |
|---|---|---|---|---|
| uses_source | uses_source | SeismicSurvey | Source | 1..n |
| deploys_receiver | deploys_receiver | SeismicSurvey | Receiver | 1..n |
| applies_geometry | applies_geometry | SeismicSurvey | AcquisitionGeometry | 1..1 |
| respects_nyquist | respects_nyquist | SamplingParameters | Aliasing | 0..1 |
| characterised_by | characterised_by | SeismicSurvey | SamplingParameters | 1..1 |
| has_subclass | has_subclass | SeismicSurvey | SeismicSurvey | 0..n |
| produces_aliasing | produces_aliasing | SamplingParameters | Aliasing | 0..1 |
| is_part_of_survey | is_part_of_survey | AcquisitionGeometry | SeismicSurvey | 1..1 |
| collocated_with | collocated_with | Hydrophone | Geophone | 0..1 |

### Instancias

| ID | Nome | Tipo (classe) | Descricao |
|---|---|---|---|
| I_BUZ3D_2022 | Buzios 3D Wide-Azimuth Streamer Survey 2022 | MarineSurvey | Broadband wide-azimuth 3D towed-streamer survey over the Buzios carbonate pre-sa |
| I_LAND_VIB_2021 | Parnaiba Basin Vibroseis Land Survey 2021 | LandSurvey | Orthogonal-template 3D vibroseis survey in the Parnaiba Basin, northeastern Braz |
| I_OBN_LULA_2023 | Lula OBN 4C Full-Azimuth Survey 2023 | OBNSurvey | Ocean-Bottom Node full-azimuth 4C survey over the Lula giant pre-salt field, San |


## Sismico — Processamento (P2.8)

Referencias: Yilmaz (2001). Ver `docs/SEISMIC.md` para documentacao completa.

**Totais**: 18 classes, 13 propriedades, 7 relacoes, 3 instancias.

### Classes

| ID | Nome PT | Nome EN | Superclasse | Dominio | Descricao (resumo) | Fontes |
|---|---|---|---|---|---|---|
| ProcessingFlow | Fluxo de Processamento | ProcessingFlow | owl:Thing | seismic_processing | Ordered sequence of processing steps applied to raw seismic data to produce an i... | Yilmaz 2001, Sheriff & Geldart 1995 |
| NoiseSuppressionFilter | Filtro de Supressao de Ruido | NoiseSuppressionFilter | owl:Thing | seismic_processing | Generic category of operations that attenuate coherent or incoherent noise in se... | Yilmaz 2001 |
| DATVF | DATVF — Denoising Adaptativo no Dominio T-V-F | DATVF | NoiseSuppressionFilter | seismic_processing | Data-Adaptive Time-Variant Frequency filter that applies a spatially and tempora... | Yilmaz 2001 |
| FXEdit | FX Edit — Edicao no Dominio F-X | FXEdit | NoiseSuppressionFilter | seismic_processing | Coherent noise attenuation in the frequency-wavenumber (f-x) domain. Random nois... | Yilmaz 2001 |
| DenoiseFK | Denoising FK — Filtragem F-K | DenoiseFK | NoiseSuppressionFilter | seismic_processing | Frequency-wavenumber (f-k) fan filter that attenuates noise with apparent veloci... | Yilmaz 2001 |
| Deconvolution | Deconvolucao | Deconvolution | owl:Thing | seismic_processing | Inverse filtering operation that compresses the source wavelet toward a spike (s... | Yilmaz 2001, Sheriff & Geldart 1995 |
| PredictiveDeconvolution | Deconvolucao Preditiva | PredictiveDeconvolution | Deconvolution | seismic_processing | Deconvolution in which a prediction distance (lag) greater than one sample is us... | Yilmaz 2001 |
| SpikingDeconvolution | Deconvolucao por Espicamento | SpikingDeconvolution | Deconvolution | seismic_processing | Wiener least-squares deconvolution with prediction lag=1 sample, aiming to colla... | Yilmaz 2001 |
| NMO | NMO — Correcao Normal Moveout | NMO | owl:Thing | seismic_processing | Normal Moveout correction: time-shift applied to each trace to remove the hyperb... | Yilmaz 2001 |
| DMO | DMO — Correcao Dip Moveout | DMO | owl:Thing | seismic_processing | Dip Moveout correction applied after NMO to remove the dip-dependent component o... | Yilmaz 2001 |
| Stacking | Empilhamento | Stacking | owl:Thing | seismic_processing | Summation of NMO-corrected CMP traces to produce a single stacked trace with imp... | Yilmaz 2001 |
| StaticCorrection | Correcao Estatica | StaticCorrection | owl:Thing | seismic_processing | Time-shift applied to land seismic traces to compensate for near-surface weather... | Yilmaz 2001 |
| AmplitudeCompensation | Compensacao de Amplitude | AmplitudeCompensation | owl:Thing | seismic_processing | Amplitude restoration to compensate for geometrical spreading loss and anelastic... | Yilmaz 2001 |
| SphericalDivergenceCorrection | Correcao de Divergencia Esferica | SphericalDivergenceCorrection | AmplitudeCompensation | seismic_processing | Gain function proportional to t^2 * v^2(t) that compensates for amplitude decay ... | Yilmaz 2001 |
| QCompensation | Compensacao-Q (Atenuacao Anelastica) | QCompensation | AmplitudeCompensation | seismic_processing | Inverse-Q filter that restores high-frequency amplitude and phase loss caused by... | Yilmaz 2001 |
| Migration | Migracao Sismica | Migration | owl:Thing | seismic_processing | Wave-equation-based imaging operator that collapses diffractions and repositions... | Yilmaz 2001, Sheriff & Geldart 1995 |
| KirchhoffMigration | Migracao de Kirchhoff | KirchhoffMigration | Migration | seismic_processing | Asymptotic migration based on the Kirchhoff integral of the scalar wave equation... | Yilmaz 2001 |
| RTM | RTM — Migracao Reversa no Tempo | RTM | Migration | seismic_processing | Reverse Time Migration: two-way wave equation migration that propagates the sour... | Yilmaz 2001 |

### Propriedades

| ID | Nome | Tipo | Dominio | Range / Unidade | Obrigatorio |
|---|---|---|---|---|---|
| processingStep | processingStep |  |  | xsd:string | nao |
| stepOrder | stepOrder |  |  | xsd:integer | nao |
| operatorLength | operatorLength |  |  | xsd:integer | nao |
| predictionLag | predictionLag |  |  | xsd:integer | nao |
| velocityFieldType | velocityFieldType |  |  | xsd:string | nao |
| stretchMute | stretchMute |  |  | xsd:decimal | nao |
| qFactor | qFactor |  |  | xsd:decimal | nao |
| migrationAlgorithm | migrationAlgorithm |  |  | xsd:string | nao |
| migrationDomain | migrationDomain |  |  | xsd:string | nao |
| bandpassFilterLow | bandpassFilterLow |  |  | xsd:decimal | nao |
| bandpassFilterHigh | bandpassFilterHigh |  |  | xsd:decimal | nao |
| gainFunction | gainFunction |  |  | xsd:string | nao |
| staticShift | staticShift |  |  | xsd:decimal | nao |

### Relacoes

| ID | Nome | Dominio (classe) | Range (classe) | Cardinalidade |
|---|---|---|---|---|
| precedes | precedes | owl:Thing | owl:Thing | 0..n |
| follows | follows | owl:Thing | owl:Thing | 0..n |
| part_of_flow | part_of_flow | owl:Thing | ProcessingFlow | 1..1 |
| applies_filter | applies_filter | ProcessingFlow | NoiseSuppressionFilter | 0..n |
| uses_deconvolution | uses_deconvolution | ProcessingFlow | Deconvolution | 0..1 |
| uses_migration | uses_migration | ProcessingFlow | Migration | 1..1 |
| compensates_amplitude | compensates_amplitude | ProcessingFlow | AmplitudeCompensation | 1..1 |

### Instancias

| ID | Nome | Tipo (classe) | Descricao |
|---|---|---|---|
| PF_MARINE_RTM | Deep-Water Pre-Stack RTM Processing Flow | ProcessingFlow | Typical pre-stack depth migration processing flow for deep-water broadband 3D ma |
| PF_LAND_KIRCHHOFF | Land Vibroseis Kirchhoff Time Migration Flow | ProcessingFlow | Standard processing flow for land vibroseis 3D: cross-correlation, statics, band |
| PF_OBN_PS | OBN 4C PP/PS Joint Processing Flow | ProcessingFlow | Processing flow for OBN 4C ocean-bottom data including dual-sensor summation, P- |


## Sismico — Inversao e Atributos (P2.8)

Referencias: Russell (1988), Connolly (1999), Chopra & Marfurt (2007), Coleou et al. (2003). Ver `docs/SEISMIC.md` para documentacao completa.

**Totais**: 26 classes, 15 propriedades, 9 relacoes, 4 instancias.

### Classes

| ID | Nome PT | Nome EN | Superclasse | Dominio | Descricao (resumo) | Fontes |
|---|---|---|---|---|---|---|
| SeismicInversion | Inversao Sismica | SeismicInversion | owl:Thing | seismic_inversion | Process of transforming seismic reflection data into quantitative rock property ... | Russell 1988, Yilmaz 2001 |
| PostStackInversion | Inversao Pos-Empilhamento | PostStackInversion | SeismicInversion | seismic_inversion | Inversion applied to stacked (zero-offset equivalent) seismic data to estimate a... | Russell 1988 |
| PreStackInversion | Inversao Pre-Empilhamento | PreStackInversion | SeismicInversion | seismic_inversion | Simultaneous inversion of partial-angle stacks to estimate Vp, Vs and density us... | Russell 1988, Connolly 1999 |
| AVOInversion | Inversao AVO | AVOInversion | SeismicInversion | seismic_inversion | Amplitude Versus Offset inversion that extracts AVO intercept (A) and gradient (... | Yilmaz 2001 |
| ElasticImpedanceInversion | Inversao de Impedancia Elastica | ElasticImpedanceInversion | PreStackInversion | seismic_inversion | Inversion of angle-dependent seismic data to Elastic Impedance (EI), the far-off... | Connolly 1999 |
| FullWaveformInversion | Inversao de Forma de Onda Completa (FWI) | FullWaveformInversion | SeismicInversion | seismic_inversion | Iterative inversion that minimises the misfit between observed and modelled wave... | Yilmaz 2001 |
| AcousticImpedance | Impedancia Acustica | AcousticImpedance | owl:Thing | seismic_inversion | Product of P-wave velocity and bulk density: Ip = Vp * rho. Primary output of po... | Russell 1988 |
| ElasticImpedance | Impedancia Elastica | ElasticImpedance | owl:Thing | seismic_inversion | Angle-dependent impedance generalisation of acoustic impedance for non-zero inci... | Connolly 1999 |
| RockProperty | Propriedade de Rocha | RockProperty | owl:Thing | seismic_inversion | Quantitative petrophysical or rock-physics parameter derived from seismic invers... | Russell 1988 |
| VpVsRatio | Razao Vp/Vs | VpVsRatio | RockProperty | seismic_inversion | Ratio of P-wave to S-wave velocity. Sensitive to fluid saturation: brine-saturat... | Russell 1988 |
| LambdaRho | Lambda-Rho | LambdaRho | RockProperty | seismic_inversion | Product of Lame parameter lambda and density: lambda*rho. Highly sensitive to po... | Russell 1988 |
| MuRho | Mu-Rho | MuRho | RockProperty | seismic_inversion | Product of shear modulus mu and density. Relatively insensitive to pore fluid bu... | Russell 1988 |
| SeismicAttribute | Atributo Sismico | SeismicAttribute | owl:Thing | seismic_attributes | Quantitative measure derived from seismic data through mathematical transformati... | Chopra & Marfurt 2007 |
| Coherence | Coerencia | Coherence | SeismicAttribute | seismic_attributes | Measure of lateral similarity of seismic traces. Low coherence indicates faults,... | Chopra & Marfurt 2007 |
| Curvature | Curvatura | Curvature | SeismicAttribute | seismic_attributes | Second spatial derivative of the seismic horizon. Most-positive and most-negativ... | Chopra & Marfurt 2007 |
| RMS | Amplitude RMS | RMS | SeismicAttribute | seismic_attributes | Root Mean Square amplitude computed over a time window. Sensitive to reflectivit... | Chopra & Marfurt 2007 |
| SpectralDecomposition | Decomposicao Espectral | SpectralDecomposition | SeismicAttribute | seismic_attributes | Time-frequency analysis (short-window DFT, CWT or MP) that extracts amplitude an... | Chopra & Marfurt 2007 |
| InstantaneousPhase | Fase Instantanea | InstantaneousPhase | SeismicAttribute | seismic_attributes | Phase of the analytic signal derived via Hilbert transform. Highlights reflector... | Chopra & Marfurt 2007 |
| Dip | Mergulho Sismico | Dip | SeismicAttribute | seismic_attributes | Inline and crossline apparent dip of the seismic event derived from the gradient... | Chopra & Marfurt 2007 |
| Azimuth | Azimute Sismico | Azimuth | SeismicAttribute | seismic_attributes | Compass direction of the steepest dip of a reflector, derived jointly with the D... | Chopra & Marfurt 2007 |
| DHI | DHI — Indicador Direto de Hidrocarboneto | DHI | SeismicAttribute | seismic_attributes | Direct Hydrocarbon Indicator: seismic anomaly whose character is directly contro... | Yilmaz 2001 |
| AVOAnomaly | Anomalia AVO | AVOAnomaly | DHI | seismic_attributes | Offset-dependent amplitude anomaly at a reservoir interface classified into four... | Yilmaz 2001 |
| SOM | SOM — Mapa Auto-Organizavel | SOM | owl:Thing | seismic_ml | Self-Organising Map: unsupervised neural network that projects a multi-attribute... | Coleou et al. 2003 |
| PCA | PCA — Analise de Componentes Principais | PCA | owl:Thing | seismic_ml | Principal Component Analysis applied to a multi-attribute seismic dataset to red... | Coleou et al. 2003 |
| FaciesClassification | Classificacao de Facies Sismicas | FaciesClassification | owl:Thing | seismic_ml | Assignment of seismic volumes or attribute maps to discrete facies classes that ... | Coleou et al. 2003, Chopra & Marfurt 2007 |
| SweetSpot | Sweet Spot | SweetSpot | owl:Thing | seismic_attributes | Geospatially bounded zone identified by the intersection of favourable seismic a... | Chopra & Marfurt 2007 |

### Propriedades

| ID | Nome | Tipo | Dominio | Range / Unidade | Obrigatorio |
|---|---|---|---|---|---|
| acousticImpedance_value | acousticImpedance_value |  |  | xsd:decimal | nao |
| elasticImpedance_angle | elasticImpedance_angle |  |  | xsd:decimal | nao |
| vpVsRatio_value | vpVsRatio_value |  |  | xsd:decimal | nao |
| lambdaRho_value | lambdaRho_value |  |  | xsd:decimal | nao |
| muRho_value | muRho_value |  |  | xsd:decimal | nao |
| avoIntercept | avoIntercept |  |  | xsd:decimal | nao |
| avoGradient | avoGradient |  |  | xsd:decimal | nao |
| avoClass | avoClass |  |  | xsd:string | nao |
| coherenceValue | coherenceValue |  |  | xsd:decimal | nao |
| curvatureType | curvatureType |  |  | xsd:string | nao |
| spectralFrequency | spectralFrequency |  |  | xsd:decimal | nao |
| somNeuronCount | somNeuronCount |  |  | xsd:integer | nao |
| pcaVarianceExplained | pcaVarianceExplained |  |  | xsd:decimal | nao |
| inversionMethod | inversionMethod |  |  | xsd:string | nao |
| wellCount | wellCount |  |  | xsd:integer | nao |

### Relacoes

| ID | Nome | Dominio (classe) | Range (classe) | Cardinalidade |
|---|---|---|---|---|
| derived_from | derived_from | RockProperty | SeismicInversion | 1..n |
| correlates_with | correlates_with | SeismicAttribute | RockProperty | 0..n |
| indicates | indicates | DHI | SweetSpot | 0..n |
| classified_by | classified_by | FaciesClassification | SOM | 0..1 |
| uses_pca | uses_pca | FaciesClassification | PCA | 0..1 |
| input_to_inversion | input_to_inversion | owl:Thing | SeismicInversion | 1..n |
| yields | yields | SeismicInversion | RockProperty | 1..n |
| combined_in | combined_in | SeismicAttribute | SweetSpot | 0..n |
| constrained_by_well | constrained_by_well | SeismicInversion | geo:Poco | 1..n |

### Instancias

| ID | Nome | Tipo (classe) | Descricao |
|---|---|---|---|
| INV_BUZ_POSTSTACK | Buzios Pre-Salt Post-Stack Acoustic Impedance Inversion | PostStackInversion | Model-based post-stack inversion of the Buzios 3D seismic volume to acoustic imp |
| INV_LULA_PRESTACK | Lula Simultaneous Pre-Stack Elastic Inversion | PreStackInversion | Simultaneous pre-stack inversion of near, mid and far angle stacks to extract Ip |
| ATTR_COHERENCE_BUZ | Buzios Coherence Fault/Fracture Volume | Coherence | Semblance-based coherence attribute extracted from the Buzios RTM migrated volum |
| INST_AVO_CLASS3 | Parnaiba Basin Class III AVO Gas Sand Anomaly | AVOAnomaly | Class III AVO anomaly at the Devonian Cabecas Formation top: negative intercept  |


---

## Como regenerar

```bash
node scripts/build-ontology-doc.js
```

Para especificar destino:

```bash
node scripts/build-ontology-doc.js --out docs/ONTOLOGY.md
```
