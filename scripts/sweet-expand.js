#!/usr/bin/env node
/**
 * sweet-expand.js — Semantic expansion helper using SWEET ontology alignments.
 *
 * Given a Geolytics term id, returns all aligned SWEET URIs and — for the most
 * commonly used SWEET modules — a small embedded hierarchy snippet so that
 * agents can broaden or narrow a query without hitting the network.
 *
 * Usage (module):
 *   import { expand } from './sweet-expand.js';
 *   const result = expand('hidrocarboneto');
 *   // { termId, sweetUris, hierarchy, modules }
 *
 * Usage (CLI):
 *   node scripts/sweet-expand.js hidrocarboneto
 *   node scripts/sweet-expand.js reservatorio --include-hierarchy
 *   node scripts/sweet-expand.js diagenese --json
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, "..", "data");

// ---------------------------------------------------------------------------
// Embedded SWEET hierarchy snippet for the most-used modules.
// Each entry: { uri, parent, module, label }
// This small in-process tree lets agents walk up/down without network calls.
// Only the nodes actually used in alignments (plus their parents) are included.
// ---------------------------------------------------------------------------
const SWEET_HIERARCHY = [
  // matr (base material)
  { uri: "http://sweetontology.net/matr/Matter", parent: null, module: "matr", label: "Matter" },
  {
    uri: "http://sweetontology.net/matr/Substance",
    parent: "http://sweetontology.net/matr/Matter",
    module: "matr",
    label: "Substance",
  },
  {
    uri: "http://sweetontology.net/matr/Water",
    parent: "http://sweetontology.net/matr/Substance",
    module: "matr",
    label: "Water",
  },
  {
    uri: "http://sweetontology.net/matr/Brine",
    parent: "http://sweetontology.net/matr/Water",
    module: "matr",
    label: "Brine",
  },
  {
    uri: "http://sweetontology.net/matr/SalineWater",
    parent: "http://sweetontology.net/matr/Water",
    module: "matr",
    label: "SalineWater",
  },

  // matrOrganics
  {
    uri: "http://sweetontology.net/matrOrganics/OrganicCompound",
    parent: "http://sweetontology.net/matr/Substance",
    module: "matrOrganics",
    label: "OrganicCompound",
  },
  {
    uri: "http://sweetontology.net/matrOrganics/Hydrocarbon",
    parent: "http://sweetontology.net/matrOrganics/OrganicCompound",
    module: "matrOrganics",
    label: "Hydrocarbon",
  },
  {
    uri: "http://sweetontology.net/matrOrganics/Oil",
    parent: "http://sweetontology.net/matrOrganics/Hydrocarbon",
    module: "matrOrganics",
    label: "Oil",
  },
  {
    uri: "http://sweetontology.net/matrOrganics/NaturalGas",
    parent: "http://sweetontology.net/matrOrganics/Hydrocarbon",
    module: "matrOrganics",
    label: "NaturalGas",
  },
  {
    uri: "http://sweetontology.net/matrOrganics/Condensate",
    parent: "http://sweetontology.net/matrOrganics/Hydrocarbon",
    module: "matrOrganics",
    label: "Condensate",
  },
  {
    uri: "http://sweetontology.net/matrOrganics/Methane",
    parent: "http://sweetontology.net/matrOrganics/NaturalGas",
    module: "matrOrganics",
    label: "Methane",
  },
  {
    uri: "http://sweetontology.net/matrOrganics/Kerogen",
    parent: "http://sweetontology.net/matrOrganics/OrganicCompound",
    module: "matrOrganics",
    label: "Kerogen",
  },

  // matrRock
  {
    uri: "http://sweetontology.net/matrRock/Rock",
    parent: "http://sweetontology.net/matr/Substance",
    module: "matrRock",
    label: "Rock",
  },

  // matrRockIgneous
  {
    uri: "http://sweetontology.net/matrRockIgneous/IgneousRock",
    parent: "http://sweetontology.net/matrRock/Rock",
    module: "matrRockIgneous",
    label: "IgneousRock",
  },
  {
    uri: "http://sweetontology.net/matrRockIgneous/IntrusiveRock",
    parent: "http://sweetontology.net/matrRockIgneous/IgneousRock",
    module: "matrRockIgneous",
    label: "IntrusiveRock",
  },
  {
    uri: "http://sweetontology.net/matrRockIgneous/ExtrusiveRock",
    parent: "http://sweetontology.net/matrRockIgneous/IgneousRock",
    module: "matrRockIgneous",
    label: "ExtrusiveRock",
  },
  {
    uri: "http://sweetontology.net/matrRockIgneous/Granite",
    parent: "http://sweetontology.net/matrRockIgneous/IntrusiveRock",
    module: "matrRockIgneous",
    label: "Granite",
  },
  {
    uri: "http://sweetontology.net/matrRockIgneous/Basalt",
    parent: "http://sweetontology.net/matrRockIgneous/ExtrusiveRock",
    module: "matrRockIgneous",
    label: "Basalt",
  },

  // matrRockSedimentary
  {
    uri: "http://sweetontology.net/matrRockSedimentary/SedimentaryRock",
    parent: "http://sweetontology.net/matrRock/Rock",
    module: "matrRockSedimentary",
    label: "SedimentaryRock",
  },
  {
    uri: "http://sweetontology.net/matrRockSedimentary/Sandstone",
    parent: "http://sweetontology.net/matrRockSedimentary/SedimentaryRock",
    module: "matrRockSedimentary",
    label: "Sandstone",
  },
  {
    uri: "http://sweetontology.net/matrRockSedimentary/Limestone",
    parent: "http://sweetontology.net/matrRockSedimentary/SedimentaryRock",
    module: "matrRockSedimentary",
    label: "Limestone",
  },
  {
    uri: "http://sweetontology.net/matrRockSedimentary/Shale",
    parent: "http://sweetontology.net/matrRockSedimentary/SedimentaryRock",
    module: "matrRockSedimentary",
    label: "Shale",
  },
  {
    uri: "http://sweetontology.net/matrRockSedimentary/Dolostone",
    parent: "http://sweetontology.net/matrRockSedimentary/SedimentaryRock",
    module: "matrRockSedimentary",
    label: "Dolostone",
  },
  {
    uri: "http://sweetontology.net/matrRockSedimentary/EvaporiteRock",
    parent: "http://sweetontology.net/matrRockSedimentary/SedimentaryRock",
    module: "matrRockSedimentary",
    label: "EvaporiteRock",
  },
  {
    uri: "http://sweetontology.net/matrRockSedimentary/SaltRock",
    parent: "http://sweetontology.net/matrRockSedimentary/EvaporiteRock",
    module: "matrRockSedimentary",
    label: "SaltRock",
  },
  {
    uri: "http://sweetontology.net/matrRockSedimentary/CarbonatiteRock",
    parent: "http://sweetontology.net/matrRockSedimentary/SedimentaryRock",
    module: "matrRockSedimentary",
    label: "CarbonatiteRock",
  },

  // matrRockMetamorphic
  {
    uri: "http://sweetontology.net/matrRockMetamorphic/MetamorphicRock",
    parent: "http://sweetontology.net/matrRock/Rock",
    module: "matrRockMetamorphic",
    label: "MetamorphicRock",
  },

  // matrMineral
  {
    uri: "http://sweetontology.net/matrMineral/Mineral",
    parent: "http://sweetontology.net/matr/Substance",
    module: "matrMineral",
    label: "Mineral",
  },
  {
    uri: "http://sweetontology.net/matrMineral/Quartz",
    parent: "http://sweetontology.net/matrMineral/Mineral",
    module: "matrMineral",
    label: "Quartz",
  },
  {
    uri: "http://sweetontology.net/matrMineral/Calcite",
    parent: "http://sweetontology.net/matrMineral/Mineral",
    module: "matrMineral",
    label: "Calcite",
  },
  {
    uri: "http://sweetontology.net/matrMineral/Dolomite",
    parent: "http://sweetontology.net/matrMineral/Mineral",
    module: "matrMineral",
    label: "Dolomite",
  },
  {
    uri: "http://sweetontology.net/matrMineral/Pyrite",
    parent: "http://sweetontology.net/matrMineral/Mineral",
    module: "matrMineral",
    label: "Pyrite",
  },
  {
    uri: "http://sweetontology.net/matrMineral/Magnetite",
    parent: "http://sweetontology.net/matrMineral/Mineral",
    module: "matrMineral",
    label: "Magnetite",
  },

  // procGeo
  { uri: "http://sweetontology.net/proc/Process", parent: null, module: "proc", label: "Process" },
  {
    uri: "http://sweetontology.net/procGeo/GeologicProcess",
    parent: "http://sweetontology.net/proc/Process",
    module: "procGeo",
    label: "GeologicProcess",
  },
  {
    uri: "http://sweetontology.net/procGeo/TectonicProcess",
    parent: "http://sweetontology.net/procGeo/GeologicProcess",
    module: "procGeo",
    label: "TectonicProcess",
  },
  {
    uri: "http://sweetontology.net/procGeo/Sedimentation",
    parent: "http://sweetontology.net/procGeo/GeologicProcess",
    module: "procGeo",
    label: "Sedimentation",
  },
  {
    uri: "http://sweetontology.net/procGeo/Diagenesis",
    parent: "http://sweetontology.net/procGeo/GeologicProcess",
    module: "procGeo",
    label: "Diagenesis",
  },
  {
    uri: "http://sweetontology.net/procGeo/Erosion",
    parent: "http://sweetontology.net/procGeo/GeologicProcess",
    module: "procGeo",
    label: "Erosion",
  },
  {
    uri: "http://sweetontology.net/procGeo/Faulting",
    parent: "http://sweetontology.net/procGeo/TectonicProcess",
    module: "procGeo",
    label: "Faulting",
  },
  {
    uri: "http://sweetontology.net/procGeo/Folding",
    parent: "http://sweetontology.net/procGeo/TectonicProcess",
    module: "procGeo",
    label: "Folding",
  },
  {
    uri: "http://sweetontology.net/procGeo/Rifting",
    parent: "http://sweetontology.net/procGeo/TectonicProcess",
    module: "procGeo",
    label: "Rifting",
  },
  {
    uri: "http://sweetontology.net/procGeo/Metamorphism",
    parent: "http://sweetontology.net/procGeo/GeologicProcess",
    module: "procGeo",
    label: "Metamorphism",
  },
  {
    uri: "http://sweetontology.net/procGeo/Magmatism",
    parent: "http://sweetontology.net/procGeo/GeologicProcess",
    module: "procGeo",
    label: "Magmatism",
  },
  {
    uri: "http://sweetontology.net/procGeo/FluidMigration",
    parent: "http://sweetontology.net/procGeo/GeologicProcess",
    module: "procGeo",
    label: "FluidMigration",
  },
  {
    uri: "http://sweetontology.net/procGeo/Deformation",
    parent: "http://sweetontology.net/procGeo/TectonicProcess",
    module: "procGeo",
    label: "Deformation",
  },

  // realmGeol
  {
    uri: "http://sweetontology.net/realm/PlanetaryRealm",
    parent: null,
    module: "realm",
    label: "PlanetaryRealm",
  },
  {
    uri: "http://sweetontology.net/realmGeol/Lithosphere",
    parent: "http://sweetontology.net/realm/PlanetaryRealm",
    module: "realmGeol",
    label: "Lithosphere",
  },
  {
    uri: "http://sweetontology.net/realmGeol/Crust",
    parent: "http://sweetontology.net/realmGeol/Lithosphere",
    module: "realmGeol",
    label: "Crust",
  },
  {
    uri: "http://sweetontology.net/realmGeol/Mantle",
    parent: "http://sweetontology.net/realmGeol/Lithosphere",
    module: "realmGeol",
    label: "Mantle",
  },
  {
    uri: "http://sweetontology.net/realmGeol/GeologicFeature",
    parent: null,
    module: "realmGeol",
    label: "GeologicFeature",
  },
  {
    uri: "http://sweetontology.net/realmGeol/Unconformity",
    parent: "http://sweetontology.net/realmGeol/GeologicFeature",
    module: "realmGeol",
    label: "Unconformity",
  },
  {
    uri: "http://sweetontology.net/realmGeol/GeologicContact",
    parent: "http://sweetontology.net/realmGeol/GeologicFeature",
    module: "realmGeol",
    label: "GeologicContact",
  },
  {
    uri: "http://sweetontology.net/realmGeol/Borehole",
    parent: "http://sweetontology.net/realmGeol/GeologicFeature",
    module: "realmGeol",
    label: "Borehole",
  },

  // realmGeolTectonic
  {
    uri: "http://sweetontology.net/realmGeolTectonic/Fault",
    parent: "http://sweetontology.net/realmGeol/GeologicFeature",
    module: "realmGeolTectonic",
    label: "Fault",
  },
  {
    uri: "http://sweetontology.net/realmGeolTectonic/FaultZone",
    parent: "http://sweetontology.net/realmGeolTectonic/Fault",
    module: "realmGeolTectonic",
    label: "FaultZone",
  },
  {
    uri: "http://sweetontology.net/realmGeolTectonic/Fold",
    parent: "http://sweetontology.net/realmGeol/GeologicFeature",
    module: "realmGeolTectonic",
    label: "Fold",
  },
  {
    uri: "http://sweetontology.net/realmGeolTectonic/Anticline",
    parent: "http://sweetontology.net/realmGeolTectonic/Fold",
    module: "realmGeolTectonic",
    label: "Anticline",
  },
  {
    uri: "http://sweetontology.net/realmGeolTectonic/Syncline",
    parent: "http://sweetontology.net/realmGeolTectonic/Fold",
    module: "realmGeolTectonic",
    label: "Syncline",
  },
  {
    uri: "http://sweetontology.net/realmGeolTectonic/Foliation",
    parent: "http://sweetontology.net/realmGeol/GeologicFeature",
    module: "realmGeolTectonic",
    label: "Foliation",
  },

  // realmGeolBasin
  {
    uri: "http://sweetontology.net/realmGeolBasin/SedimentaryBasin",
    parent: "http://sweetontology.net/realmGeol/GeologicFeature",
    module: "realmGeolBasin",
    label: "SedimentaryBasin",
  },
  {
    uri: "http://sweetontology.net/realmGeolBasin/RiftBasin",
    parent: "http://sweetontology.net/realmGeolBasin/SedimentaryBasin",
    module: "realmGeolBasin",
    label: "RiftBasin",
  },

  // realmHydro
  {
    uri: "http://sweetontology.net/realmHydro/Hydrosphere",
    parent: "http://sweetontology.net/realm/PlanetaryRealm",
    module: "realmHydro",
    label: "Hydrosphere",
  },
  {
    uri: "http://sweetontology.net/realmHydro/Ocean",
    parent: "http://sweetontology.net/realmHydro/Hydrosphere",
    module: "realmHydro",
    label: "Ocean",
  },
  {
    uri: "http://sweetontology.net/realmHydro/HydrospherePart",
    parent: "http://sweetontology.net/realmHydro/Hydrosphere",
    module: "realmHydro",
    label: "HydrospherePart",
  },

  // prop classes
  {
    uri: "http://sweetontology.net/prop/PhysicalProperty",
    parent: null,
    module: "prop",
    label: "PhysicalProperty",
  },
  {
    uri: "http://sweetontology.net/propPressure/Pressure",
    parent: "http://sweetontology.net/prop/PhysicalProperty",
    module: "propPressure",
    label: "Pressure",
  },
  {
    uri: "http://sweetontology.net/propTemperature/Temperature",
    parent: "http://sweetontology.net/prop/PhysicalProperty",
    module: "propTemperature",
    label: "Temperature",
  },
  {
    uri: "http://sweetontology.net/propMass/Density",
    parent: "http://sweetontology.net/prop/PhysicalProperty",
    module: "propMass",
    label: "Density",
  },
  {
    uri: "http://sweetontology.net/propFluidTransport/Viscosity",
    parent: "http://sweetontology.net/prop/PhysicalProperty",
    module: "propFluidTransport",
    label: "Viscosity",
  },
  {
    uri: "http://sweetontology.net/propFluidTransport/Permeability",
    parent: "http://sweetontology.net/prop/PhysicalProperty",
    module: "propFluidTransport",
    label: "Permeability",
  },
  {
    uri: "http://sweetontology.net/propSpaceMultidimensional/Porosity",
    parent: "http://sweetontology.net/prop/PhysicalProperty",
    module: "propSpaceMultidimensional",
    label: "Porosity",
  },
  {
    uri: "http://sweetontology.net/propSpaceDistance/Depth",
    parent: "http://sweetontology.net/prop/PhysicalProperty",
    module: "propSpaceDistance",
    label: "Depth",
  },

  // reprSciUnits
  {
    uri: "http://sweetontology.net/reprSciUnits/Pascal",
    parent: null,
    module: "reprSciUnits",
    label: "Pascal",
  },
  {
    uri: "http://sweetontology.net/reprSciUnits/Kelvin",
    parent: null,
    module: "reprSciUnits",
    label: "Kelvin",
  },
  {
    uri: "http://sweetontology.net/reprSciUnits/Meter",
    parent: null,
    module: "reprSciUnits",
    label: "Meter",
  },
  {
    uri: "http://sweetontology.net/reprSciUnits/Darcy",
    parent: null,
    module: "reprSciUnits",
    label: "Darcy",
  },

  // reprTimeGeologic
  {
    uri: "http://sweetontology.net/reprTimeGeologic/GeochronologicEra",
    parent: null,
    module: "reprTimeGeologic",
    label: "GeochronologicEra",
  },
  {
    uri: "http://sweetontology.net/reprTimeGeologic/Mesozoic",
    parent: "http://sweetontology.net/reprTimeGeologic/GeochronologicEra",
    module: "reprTimeGeologic",
    label: "Mesozoic",
  },
  {
    uri: "http://sweetontology.net/reprTimeGeologic/Cretaceous",
    parent: "http://sweetontology.net/reprTimeGeologic/GeochronologicEra",
    module: "reprTimeGeologic",
    label: "Cretaceous",
  },
  {
    uri: "http://sweetontology.net/reprTimeGeologic/Aptian",
    parent: "http://sweetontology.net/reprTimeGeologic/Cretaceous",
    module: "reprTimeGeologic",
    label: "Aptian",
  },
  {
    uri: "http://sweetontology.net/reprTimeGeologic/Albian",
    parent: "http://sweetontology.net/reprTimeGeologic/Cretaceous",
    module: "reprTimeGeologic",
    label: "Albian",
  },
];

// Index by URI for fast lookups
const HIERARCHY_BY_URI = new Map(SWEET_HIERARCHY.map((n) => [n.uri, n]));

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function loadAlignments() {
  const p = path.join(DATA_DIR, "sweet-alignment.json");
  if (!fs.existsSync(p)) return [];
  try {
    const data = JSON.parse(fs.readFileSync(p, "utf8"));
    return Array.isArray(data?.alignments) ? data.alignments : [];
  } catch {
    return [];
  }
}

/**
 * Walk the embedded hierarchy upwards from a URI to the root.
 * Returns an array of ancestor URIs (not including the start URI itself).
 */
function ancestors(uri) {
  const result = [];
  let current = HIERARCHY_BY_URI.get(uri);
  while (current?.parent) {
    result.push(current.parent);
    current = HIERARCHY_BY_URI.get(current.parent);
  }
  return result;
}

/**
 * Walk the embedded hierarchy downwards from a URI.
 * Returns an array of direct child URIs.
 */
function children(uri) {
  return SWEET_HIERARCHY.filter((n) => n.parent === uri).map((n) => n.uri);
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

/**
 * expand(termId, options?) — returns SWEET expansion data for a Geolytics term.
 *
 * @param {string} termId - Geolytics term id (e.g. 'hidrocarboneto')
 * @param {object} [options]
 * @param {boolean} [options.includeHierarchy=true] - include parent/child URIs
 * @param {boolean} [options.includeSiblings=false] - include sibling URIs (same parent)
 *
 * @returns {{ termId, alignments, sweetUris, hierarchy, modules, found: boolean }}
 */
export function expand(termId, options = {}) {
  const { includeHierarchy = true, includeSiblings = false } = options;

  const allAlignments = loadAlignments();
  const termAlignments = allAlignments.filter((a) => a.geolytics_id === termId);

  if (termAlignments.length === 0) {
    return { termId, found: false, alignments: [], sweetUris: [], hierarchy: null, modules: [] };
  }

  // Collect all unique SWEET URIs referenced by this term's alignments.
  const sweetUrisSet = new Set();
  for (const a of termAlignments) {
    for (const uri of Array.isArray(a.sweet_uris) ? a.sweet_uris : []) {
      sweetUrisSet.add(uri);
    }
  }
  const sweetUris = [...sweetUrisSet];

  // Build hierarchy data for each URI.
  let hierarchy = null;
  if (includeHierarchy) {
    hierarchy = {};
    for (const uri of sweetUris) {
      const node = HIERARCHY_BY_URI.get(uri);
      const ancestorUris = ancestors(uri);
      const childUris = children(uri);
      const siblingUris =
        includeSiblings && node?.parent ? children(node.parent).filter((u) => u !== uri) : [];
      hierarchy[uri] = {
        label: node?.label || null,
        module: node?.module || null,
        parent: node?.parent || null,
        ancestors: ancestorUris,
        children: childUris,
        siblings: siblingUris,
      };
    }
  }

  const modules = [...new Set(termAlignments.map((a) => a.sweet_module).filter(Boolean))];

  return {
    termId,
    found: true,
    alignments: termAlignments,
    sweetUris,
    hierarchy,
    modules,
  };
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const args = process.argv.slice(2).filter((a) => !a.startsWith("--"));
  const flags = process.argv.slice(2).filter((a) => a.startsWith("--"));

  const termId = args[0];
  if (!termId) {
    console.error(
      "Usage: node scripts/sweet-expand.js <geolytics_id> [--include-hierarchy] [--include-siblings] [--json]"
    );
    process.exit(1);
  }

  const jsonMode = flags.includes("--json");
  const includeHierarchy = !flags.includes("--no-hierarchy");
  const includeSiblings = flags.includes("--include-siblings");

  const result = expand(termId, { includeHierarchy, includeSiblings });

  if (jsonMode) {
    console.log(JSON.stringify(result, null, 2));
  } else if (!result.found) {
    console.log(`No SWEET alignment found for term: "${termId}"`);
    console.log("Check data/sweet-alignment.json for available term IDs.");
  } else {
    console.log(`SWEET expansion for: ${termId}`);
    console.log(`Modules: ${result.modules.join(", ")}`);
    console.log("");
    console.log("Aligned SWEET URIs:");
    for (const a of result.alignments) {
      console.log(`  [${a.alignment_type}] ${(a.sweet_uris || []).join(", ")}`);
      if (a.rationale_pt) console.log(`    Rationale: ${a.rationale_pt}`);
    }
    if (result.hierarchy) {
      console.log("");
      console.log("Hierarchy (embedded snippet):");
      for (const [uri, h] of Object.entries(result.hierarchy)) {
        const shortUri = uri.replace("http://sweetontology.net/", "sweet:");
        const parentShort = h.parent
          ? h.parent.replace("http://sweetontology.net/", "sweet:")
          : "none";
        console.log(`  ${shortUri} (${h.module})`);
        console.log(`    parent  : ${parentShort}`);
        if (h.ancestors.length) {
          console.log(
            `    ancestors: ${h.ancestors.map((u) => u.replace("http://sweetontology.net/", "sweet:")).join(" > ")}`
          );
        }
        if (h.children.length) {
          console.log(
            `    children : ${h.children.map((u) => u.replace("http://sweetontology.net/", "sweet:")).join(", ")}`
          );
        }
      }
    }
  }
}
