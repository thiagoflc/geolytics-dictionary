// ============================================================
// Enriquecimento semântico de DrillingPhase — roles 3W + IADC
// Projeto: SPE Volve Operational Intelligence
// Fonte: Petrobras 3W v2.0.0 (Vargas et al. 2019) + IADC Drilling
//         Manual Classification System
// Nós alvo: 599 DrillingPhase (Volve wellbores 15/9-F-*)
//
// Propriedades adicionadas:
//   role_3w          — 'event_observation' | 'signal_concept'
//   iadc_activity_class — código IADC canônico
//   time_category    — 'productive_time' | 'non_productive_time' |
//                      'invisible_lost_time'
//   npt_severity     — null | 'low' | 'medium' | 'high' | 'critical'
//   enriched         — true (flag de auditoria)
// ============================================================

// ------------------------------------------------------------
// 1. PRODUCTIVE TIME — event_observation: atividades de perfuração
//    direta (avanço de profundidade)
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.name IN [
    'drilling',
    'rotary_drilling',
    'slide_drilling',
    'directional_drilling',
    'motor_drilling',
    'rotary_steerable',
    'wob_optimization'
]
SET p.role_3w           = 'event_observation',
    p.iadc_activity_class = CASE p.name
        WHEN 'drilling'            THEN 'rotary_drilling'
        WHEN 'rotary_drilling'     THEN 'rotary_drilling'
        WHEN 'slide_drilling'      THEN 'slide_drilling'
        WHEN 'directional_drilling' THEN 'directional_drilling'
        WHEN 'motor_drilling'      THEN 'motor_drilling'
        WHEN 'rotary_steerable'    THEN 'rotary_steerable_drilling'
        WHEN 'wob_optimization'    THEN 'rotary_drilling'
        ELSE 'rotary_drilling'
    END,
    p.time_category      = 'productive_time',
    p.npt_severity       = null,
    p.enriched           = true;

// ------------------------------------------------------------
// 2. PRODUCTIVE TIME — event_observation: manobras (tripping)
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.name IN [
    'tripping',
    'tripping_in',
    'tripping_out',
    'rih',
    'pooh',
    'wiper_trip',
    'short_trip',
    'slug_trip'
]
SET p.role_3w           = 'event_observation',
    p.iadc_activity_class = CASE p.name
        WHEN 'tripping'     THEN 'tripping'
        WHEN 'tripping_in'  THEN 'tripping_in_hole'
        WHEN 'tripping_out' THEN 'pulling_out_of_hole'
        WHEN 'rih'          THEN 'tripping_in_hole'
        WHEN 'pooh'         THEN 'pulling_out_of_hole'
        WHEN 'wiper_trip'   THEN 'wiper_trip'
        WHEN 'short_trip'   THEN 'short_trip'
        WHEN 'slug_trip'    THEN 'tripping'
        ELSE 'tripping'
    END,
    p.time_category      = 'productive_time',
    p.npt_severity       = null,
    p.enriched           = true;

// ------------------------------------------------------------
// 3. PRODUCTIVE TIME — event_observation: completação mecânica
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.name IN [
    'casing',
    'casing_running',
    'liner_running',
    'tubing_running',
    'cementing',
    'squeeze_cementing',
    'completions',
    'perforation',
    'gravel_packing',
    'screen_running'
]
SET p.role_3w           = 'event_observation',
    p.iadc_activity_class = CASE p.name
        WHEN 'casing'            THEN 'casing_running'
        WHEN 'casing_running'    THEN 'casing_running'
        WHEN 'liner_running'     THEN 'liner_running'
        WHEN 'tubing_running'    THEN 'tubing_running'
        WHEN 'cementing'         THEN 'cementing'
        WHEN 'squeeze_cementing' THEN 'squeeze_cementing'
        WHEN 'completions'       THEN 'completion_operations'
        WHEN 'perforation'       THEN 'perforating'
        WHEN 'gravel_packing'    THEN 'gravel_pack'
        WHEN 'screen_running'    THEN 'screen_running'
        ELSE 'casing_running'
    END,
    p.time_category      = 'productive_time',
    p.npt_severity       = null,
    p.enriched           = true;

// ------------------------------------------------------------
// 4. PRODUCTIVE TIME — event_observation: avaliação e perfilagem
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.name IN [
    'logging',
    'wireline_logging',
    'lwd_logging',
    'mwd_logging',
    'testing',
    'dst',
    'formation_test',
    'sampling',
    'survey',
    'directional_survey',
    'gyro_survey'
]
SET p.role_3w           = 'event_observation',
    p.iadc_activity_class = CASE p.name
        WHEN 'logging'          THEN 'wireline_logging'
        WHEN 'wireline_logging' THEN 'wireline_logging'
        WHEN 'lwd_logging'      THEN 'lwd_mwd'
        WHEN 'mwd_logging'      THEN 'lwd_mwd'
        WHEN 'testing'          THEN 'formation_testing'
        WHEN 'dst'              THEN 'drill_stem_test'
        WHEN 'formation_test'   THEN 'formation_testing'
        WHEN 'sampling'         THEN 'formation_testing'
        WHEN 'survey'           THEN 'directional_survey'
        WHEN 'directional_survey' THEN 'directional_survey'
        WHEN 'gyro_survey'      THEN 'directional_survey'
        ELSE 'wireline_logging'
    END,
    p.time_category      = 'productive_time',
    p.npt_severity       = null,
    p.enriched           = true;

// ------------------------------------------------------------
// 5. PRODUCTIVE TIME — event_observation: operações de suporte
//    (circulação, reaming, pesca, etc.)
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.name IN [
    'circulating',
    'conditioning',
    'reaming',
    'backreaming',
    'washing',
    'milling',
    'fishing',
    'jarring',
    'coring',
    'underreaming',
    'hole_opening',
    'displacement'
]
SET p.role_3w           = 'event_observation',
    p.iadc_activity_class = CASE p.name
        WHEN 'circulating'   THEN 'circulating'
        WHEN 'conditioning'  THEN 'mud_conditioning'
        WHEN 'reaming'       THEN 'reaming'
        WHEN 'backreaming'   THEN 'back_reaming'
        WHEN 'washing'       THEN 'washing_down'
        WHEN 'milling'       THEN 'milling'
        WHEN 'fishing'       THEN 'fishing'
        WHEN 'jarring'       THEN 'jarring'
        WHEN 'coring'        THEN 'coring'
        WHEN 'underreaming'  THEN 'underreaming'
        WHEN 'hole_opening'  THEN 'hole_opening'
        WHEN 'displacement'  THEN 'fluid_displacement'
        ELSE 'circulating'
    END,
    p.time_category      = 'productive_time',
    p.npt_severity       = null,
    p.enriched           = true;

// ------------------------------------------------------------
// 6. NON-PRODUCTIVE TIME — event_observation: incidentes mecânicos
//    (NPT direto — o que ACONTECEU)
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.name IN [
    'stuck_pipe',
    'pipe_stuck',
    'mechanical_stuck',
    'differential_sticking',
    'twist_off',
    'washout',
    'bit_balling',
    'bha_failure',
    'equipment_failure',
    'pump_failure',
    'rig_repair',
    'top_drive_failure',
    'rotary_failure',
    'bop_test',
    'bop_repair',
    'wellhead_repair',
    'surface_equipment_failure'
]
SET p.role_3w           = 'event_observation',
    p.iadc_activity_class = CASE p.name
        WHEN 'stuck_pipe'               THEN 'stuck_pipe'
        WHEN 'pipe_stuck'               THEN 'stuck_pipe'
        WHEN 'mechanical_stuck'         THEN 'stuck_pipe_mechanical'
        WHEN 'differential_sticking'    THEN 'stuck_pipe_differential'
        WHEN 'twist_off'                THEN 'twist_off'
        WHEN 'washout'                  THEN 'washout'
        WHEN 'bit_balling'              THEN 'bit_balling'
        WHEN 'bha_failure'              THEN 'bha_failure'
        WHEN 'equipment_failure'        THEN 'equipment_failure'
        WHEN 'pump_failure'             THEN 'pump_failure'
        WHEN 'rig_repair'               THEN 'rig_repair'
        WHEN 'top_drive_failure'        THEN 'top_drive_failure'
        WHEN 'rotary_failure'           THEN 'rotary_failure'
        WHEN 'bop_test'                 THEN 'bop_test'
        WHEN 'bop_repair'               THEN 'bop_repair'
        WHEN 'wellhead_repair'          THEN 'wellhead_repair'
        WHEN 'surface_equipment_failure' THEN 'equipment_failure'
        ELSE 'equipment_failure'
    END,
    p.time_category      = 'non_productive_time',
    p.npt_severity       = CASE p.name
        WHEN 'stuck_pipe'            THEN 'high'
        WHEN 'pipe_stuck'            THEN 'high'
        WHEN 'mechanical_stuck'      THEN 'high'
        WHEN 'differential_sticking' THEN 'high'
        WHEN 'twist_off'             THEN 'critical'
        WHEN 'washout'               THEN 'medium'
        WHEN 'bit_balling'           THEN 'low'
        WHEN 'bha_failure'           THEN 'high'
        WHEN 'equipment_failure'     THEN 'medium'
        WHEN 'pump_failure'          THEN 'medium'
        WHEN 'rig_repair'            THEN 'medium'
        WHEN 'top_drive_failure'     THEN 'medium'
        WHEN 'rotary_failure'        THEN 'medium'
        WHEN 'bop_test'              THEN 'low'
        WHEN 'bop_repair'            THEN 'high'
        WHEN 'wellhead_repair'       THEN 'medium'
        ELSE 'medium'
    END,
    p.enriched           = true;

// ------------------------------------------------------------
// 7. NON-PRODUCTIVE TIME — event_observation: problemas de fluido
//    e controle de poço
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.name IN [
    'lost_circulation',
    'partial_losses',
    'total_losses',
    'kick',
    'well_control',
    'influx',
    'baryte_plug',
    'lostcirc_treatment',
    'mud_losses',
    'gas_cut_mud',
    'h2s_event',
    'fluid_loss'
]
SET p.role_3w           = 'event_observation',
    p.iadc_activity_class = CASE p.name
        WHEN 'lost_circulation'    THEN 'lost_circulation'
        WHEN 'partial_losses'      THEN 'lost_circulation_partial'
        WHEN 'total_losses'        THEN 'lost_circulation_total'
        WHEN 'kick'                THEN 'well_control_kick'
        WHEN 'well_control'        THEN 'well_control'
        WHEN 'influx'              THEN 'well_control_kick'
        WHEN 'baryte_plug'         THEN 'lost_circulation_treatment'
        WHEN 'lostcirc_treatment'  THEN 'lost_circulation_treatment'
        WHEN 'mud_losses'          THEN 'lost_circulation'
        WHEN 'gas_cut_mud'         THEN 'well_control'
        WHEN 'h2s_event'           THEN 'well_control_h2s'
        WHEN 'fluid_loss'          THEN 'lost_circulation'
        ELSE 'lost_circulation'
    END,
    p.time_category      = 'non_productive_time',
    p.npt_severity       = CASE p.name
        WHEN 'lost_circulation'   THEN 'high'
        WHEN 'partial_losses'     THEN 'medium'
        WHEN 'total_losses'       THEN 'critical'
        WHEN 'kick'               THEN 'critical'
        WHEN 'well_control'       THEN 'critical'
        WHEN 'influx'             THEN 'high'
        WHEN 'baryte_plug'        THEN 'high'
        WHEN 'lostcirc_treatment' THEN 'medium'
        WHEN 'mud_losses'         THEN 'medium'
        WHEN 'gas_cut_mud'        THEN 'high'
        WHEN 'h2s_event'          THEN 'critical'
        WHEN 'fluid_loss'         THEN 'medium'
        ELSE 'high'
    END,
    p.enriched           = true;

// ------------------------------------------------------------
// 8. NON-PRODUCTIVE TIME — event_observation: wellbore integrity
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.name IN [
    'wellbore_collapse',
    'tight_hole',
    'pack_off',
    'sloughing',
    'cavings',
    'hole_problems',
    'overpull',
    'torque_drag',
    'keyseating',
    'ledge'
]
SET p.role_3w           = 'event_observation',
    p.iadc_activity_class = CASE p.name
        WHEN 'wellbore_collapse' THEN 'wellbore_collapse'
        WHEN 'tight_hole'        THEN 'tight_hole'
        WHEN 'pack_off'          THEN 'pack_off'
        WHEN 'sloughing'         THEN 'sloughing_shale'
        WHEN 'cavings'           THEN 'sloughing_shale'
        WHEN 'hole_problems'     THEN 'hole_problems'
        WHEN 'overpull'          THEN 'overpull'
        WHEN 'torque_drag'       THEN 'torque_drag'
        WHEN 'keyseating'        THEN 'key_seating'
        WHEN 'ledge'             THEN 'ledge_formation'
        ELSE 'hole_problems'
    END,
    p.time_category      = 'non_productive_time',
    p.npt_severity       = CASE p.name
        WHEN 'wellbore_collapse' THEN 'critical'
        WHEN 'tight_hole'        THEN 'medium'
        WHEN 'pack_off'          THEN 'high'
        WHEN 'sloughing'         THEN 'medium'
        WHEN 'cavings'           THEN 'medium'
        WHEN 'hole_problems'     THEN 'medium'
        WHEN 'overpull'          THEN 'medium'
        WHEN 'torque_drag'       THEN 'low'
        WHEN 'keyseating'        THEN 'high'
        WHEN 'ledge'             THEN 'low'
        ELSE 'medium'
    END,
    p.enriched           = true;

// ------------------------------------------------------------
// 9. NON-PRODUCTIVE TIME — event_observation: espera e logística
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.name IN [
    'waiting',
    'waiting_on_weather',
    'waiting_on_cement',
    'waiting_on_orders',
    'waiting_on_equipment',
    'waiting_on_logging',
    'standby',
    'rig_move',
    'rig_up',
    'rig_down',
    'hse_stop',
    'safety_meeting',
    'crew_change'
]
SET p.role_3w           = 'event_observation',
    p.iadc_activity_class = CASE p.name
        WHEN 'waiting'               THEN 'waiting'
        WHEN 'waiting_on_weather'    THEN 'waiting_on_weather'
        WHEN 'waiting_on_cement'     THEN 'waiting_on_cement'
        WHEN 'waiting_on_orders'     THEN 'waiting_on_orders'
        WHEN 'waiting_on_equipment'  THEN 'waiting_on_equipment'
        WHEN 'waiting_on_logging'    THEN 'waiting_on_logging'
        WHEN 'standby'               THEN 'standby'
        WHEN 'rig_move'              THEN 'rig_move'
        WHEN 'rig_up'                THEN 'rig_up'
        WHEN 'rig_down'              THEN 'rig_down'
        WHEN 'hse_stop'              THEN 'hse_incident'
        WHEN 'safety_meeting'        THEN 'safety_meeting'
        WHEN 'crew_change'           THEN 'crew_change'
        ELSE 'waiting'
    END,
    p.time_category      = 'non_productive_time',
    p.npt_severity       = CASE p.name
        WHEN 'waiting'               THEN 'low'
        WHEN 'waiting_on_weather'    THEN 'low'
        WHEN 'waiting_on_cement'     THEN 'low'
        WHEN 'waiting_on_orders'     THEN 'low'
        WHEN 'waiting_on_equipment'  THEN 'medium'
        WHEN 'waiting_on_logging'    THEN 'low'
        WHEN 'standby'               THEN 'low'
        WHEN 'rig_move'              THEN 'low'
        WHEN 'rig_up'                THEN 'low'
        WHEN 'rig_down'              THEN 'low'
        WHEN 'hse_stop'              THEN 'medium'
        WHEN 'safety_meeting'        THEN 'low'
        WHEN 'crew_change'           THEN 'low'
        ELSE 'low'
    END,
    p.enriched           = true;

// ------------------------------------------------------------
// 10. SIGNAL CONCEPT — indicadores de condição do subsolo
//     (o que o evento INDICA, não o que foi feito)
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.name IN [
    'overpressure_zone',
    'underpressure_zone',
    'wellbore_instability',
    'formation_damage',
    'differential_pressure',
    'formation_fracture',
    'natural_fracture',
    'depleted_zone',
    'thief_zone',
    'shallow_gas',
    'gas_hydrate_zone',
    'salt_section',
    'anhydrite_section',
    'reactive_shale',
    'swelling_shale',
    'unconsolidated_formation',
    'high_permeability_zone',
    'low_permeability_zone',
    'transition_zone',
    'abnormal_pressure'
]
SET p.role_3w           = 'signal_concept',
    p.iadc_activity_class = CASE p.name
        WHEN 'overpressure_zone'         THEN 'abnormal_pressure_indicator'
        WHEN 'underpressure_zone'        THEN 'sub_normal_pressure_indicator'
        WHEN 'wellbore_instability'      THEN 'formation_instability_indicator'
        WHEN 'formation_damage'          THEN 'formation_damage_indicator'
        WHEN 'differential_pressure'     THEN 'pressure_differential_indicator'
        WHEN 'formation_fracture'        THEN 'induced_fracture_indicator'
        WHEN 'natural_fracture'          THEN 'natural_fracture_indicator'
        WHEN 'depleted_zone'             THEN 'depleted_reservoir_indicator'
        WHEN 'thief_zone'                THEN 'thief_zone_indicator'
        WHEN 'shallow_gas'               THEN 'shallow_gas_indicator'
        WHEN 'gas_hydrate_zone'          THEN 'hydrate_risk_indicator'
        WHEN 'salt_section'              THEN 'evaporite_indicator'
        WHEN 'anhydrite_section'         THEN 'evaporite_indicator'
        WHEN 'reactive_shale'            THEN 'shale_reactivity_indicator'
        WHEN 'swelling_shale'            THEN 'shale_swelling_indicator'
        WHEN 'unconsolidated_formation'  THEN 'weak_formation_indicator'
        WHEN 'high_permeability_zone'    THEN 'permeability_indicator'
        WHEN 'low_permeability_zone'     THEN 'permeability_indicator'
        WHEN 'transition_zone'           THEN 'pressure_transition_indicator'
        WHEN 'abnormal_pressure'         THEN 'abnormal_pressure_indicator'
        ELSE 'formation_condition_indicator'
    END,
    p.time_category      = 'non_productive_time',
    p.npt_severity       = CASE p.name
        WHEN 'overpressure_zone'     THEN 'high'
        WHEN 'underpressure_zone'    THEN 'medium'
        WHEN 'wellbore_instability'  THEN 'high'
        WHEN 'formation_damage'      THEN 'medium'
        WHEN 'shallow_gas'           THEN 'critical'
        WHEN 'gas_hydrate_zone'      THEN 'high'
        WHEN 'reactive_shale'        THEN 'high'
        WHEN 'swelling_shale'        THEN 'high'
        WHEN 'depleted_zone'         THEN 'medium'
        WHEN 'abnormal_pressure'     THEN 'high'
        ELSE 'low'
    END,
    p.enriched           = true;

// ------------------------------------------------------------
// 11. INVISIBLE LOST TIME — entre event_observation e signal_concept
//     (ineficiências que não aparecem no relatório como NPT)
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.name IN [
    'invisible_lost_time',
    'ilt',
    'flat_time',
    'connection_time',
    'slow_drilling',
    'conservative_drilling',
    'rop_optimization',
    'mud_logging',
    'gas_monitoring',
    'pit_watch'
]
SET p.role_3w           = 'event_observation',
    p.iadc_activity_class = CASE p.name
        WHEN 'invisible_lost_time'    THEN 'invisible_lost_time'
        WHEN 'ilt'                    THEN 'invisible_lost_time'
        WHEN 'flat_time'              THEN 'flat_time'
        WHEN 'connection_time'        THEN 'connection_time'
        WHEN 'slow_drilling'          THEN 'reduced_rop_drilling'
        WHEN 'conservative_drilling'  THEN 'reduced_rop_drilling'
        WHEN 'rop_optimization'       THEN 'rop_optimization'
        WHEN 'mud_logging'            THEN 'mud_logging'
        WHEN 'gas_monitoring'         THEN 'gas_monitoring'
        WHEN 'pit_watch'              THEN 'well_monitoring'
        ELSE 'invisible_lost_time'
    END,
    p.time_category      = 'invisible_lost_time',
    p.npt_severity       = null,
    p.enriched           = true;

// ------------------------------------------------------------
// 12. FALLBACK — fases não mapeadas (detection_method = 'keyword_inference')
//     Marca como 'event_observation' genérico para não deixar nós sem role
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.enriched IS NULL
  AND p.detection_method = 'keyword_inference'
SET p.role_3w           = 'event_observation',
    p.iadc_activity_class = 'unclassified_operation',
    p.time_category      = 'productive_time',
    p.npt_severity       = null,
    p.enriched           = true;

// ------------------------------------------------------------
// 13. FALLBACK — section boundaries sem nome reconhecido
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.enriched IS NULL
  AND p.detection_method = 'section_boundary'
SET p.role_3w           = 'event_observation',
    p.iadc_activity_class = 'section_boundary',
    p.time_category      = 'productive_time',
    p.npt_severity       = null,
    p.enriched           = true;

// ------------------------------------------------------------
// 14. FALLBACK FINAL — qualquer DrillingPhase ainda sem enriched
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
WHERE p.enriched IS NULL
SET p.role_3w           = 'event_observation',
    p.iadc_activity_class = 'unknown',
    p.time_category      = 'productive_time',
    p.npt_severity       = null,
    p.enriched           = true;

// ------------------------------------------------------------
// VERIFICAÇÃO — retorna contagem por role_3w e time_category
// ------------------------------------------------------------
MATCH (p:DrillingPhase)
RETURN
  p.role_3w          AS role_3w,
  p.time_category    AS time_category,
  p.npt_severity     AS npt_severity,
  count(p)           AS total
ORDER BY role_3w, time_category, npt_severity;
