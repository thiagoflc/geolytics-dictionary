#!/usr/bin/env node
/**
 * Geolytics MCP Server — entry point.
 *
 * Exposes 9 tools over stdio transport so any MCP-compatible client
 * (Claude Desktop, Claude Code, Cursor, LangGraph) can use the
 * Geolytics O&G semantic dictionary without an internet connection.
 *
 * Transport: stdio (standard for local MCP servers).
 * API: low-level Server class (compatible with @modelcontextprotocol/sdk ^1.0.0).
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { zodToJsonSchema } from "zod-to-json-schema";

import { loadAll } from "./data.js";

// --- tool modules ---
import * as lookupTerm from "./tools/lookup_term.js";
import * as expandAcronym from "./tools/expand_acronym.js";
import * as getEntity from "./tools/get_entity.js";
import * as getEntityNeighbors from "./tools/get_entity_neighbors.js";
import * as validateClaim from "./tools/validate_claim.js";
import * as cypherQuery from "./tools/cypher_query.js";
import * as searchRag from "./tools/search_rag.js";
import * as listLayers from "./tools/list_layers.js";
import * as crosswalkLookup from "./tools/crosswalk_lookup.js";

// Load all static data into memory before registering handlers.
loadAll();

const server = new Server(
  {
    name: "geolytics-mcp",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// ---------- tool registry ----------

const tools = [
  {
    name: "lookup_term",
    description:
      "Search the Geolytics O&G dictionary for a term (PT or EN). Returns matches " +
      "from glossary.json, extended-terms.json and ontopetro classes with full context: " +
      "definition PT/EN, layer URIs (petrokgraph, OSDU, GeoSciML), legal sources, examples.",
    inputSchema: zodToJsonSchema(lookupTerm.schema),
  },
  {
    name: "expand_acronym",
    description:
      "Expand an O&G acronym/sigla (e.g. ANP, BOP, FPSO, API, UTS). Returns all senses " +
      "with PT/EN expansion, category, and disambiguation hint when multiple senses exist. " +
      "Excludes generic IT acronyms by default.",
    inputSchema: zodToJsonSchema(expandAcronym.schema),
  },
  {
    name: "get_entity",
    description:
      "Get a single entity from the entity graph by id (e.g. 'poco', 'bacia-sedimentar'). " +
      "Returns the full node plus all outgoing and incoming relations resolved to neighbor objects.",
    inputSchema: zodToJsonSchema(getEntity.schema),
  },
  {
    name: "get_entity_neighbors",
    description:
      "Multi-hop BFS traversal of the entity graph starting from an entity id. " +
      "hops=1 returns direct neighbors, hops=2 goes two levels deep. " +
      "Optionally filter to specific relation types (edge_types).",
    inputSchema: zodToJsonSchema(getEntityNeighbors.schema),
  },
  {
    name: "validate_claim",
    description:
      "Validate a natural-language claim against the ontology using the semantic validator " +
      "(P1.4). Returns a structured report. If the validator is not available, returns " +
      "{valid: null, error: 'validator unavailable'}.",
    inputSchema: zodToJsonSchema(validateClaim.schema),
  },
  {
    name: "cypher_query",
    description:
      "Execute a Cypher query against the Neo4j knowledge graph. Only active when the " +
      "NEO4J_URI environment variable is set. Returns helpful setup instructions if Neo4j " +
      "is not configured.",
    inputSchema: zodToJsonSchema(cypherQuery.schema),
  },
  {
    name: "search_rag",
    description:
      "BM25 full-text search over the RAG corpus (ai/rag-corpus.jsonl, ~1 245 chunks). " +
      "No embedding provider — runs fully offline. Returns ranked chunks with score, type " +
      "and metadata. Use k to control result count (default 5).",
    inputSchema: zodToJsonSchema(searchRag.schema),
  },
  {
    name: "list_layers",
    description:
      "List the semantic layers of the Geolytics ontology (BFO+GeoCore, GeoSciML, " +
      "O3PO+GeoReservoir, Petro KGraph, OSDU, ANP, Petrobras Internal) with metadata: " +
      "maintainer, type, description, concept count, language.",
    inputSchema: zodToJsonSchema(listLayers.schema),
  },
  {
    name: "crosswalk_lookup",
    description:
      "Find equivalent terms across ontology layers by URI or entity id. " +
      "Given a petrokgraph_uri, OSDU kind, GeoSciML URI, GSO URI or plain id, returns " +
      "all matched entities with their cross-layer URI mappings. " +
      "Example: what is OSDU's term for GeoCore's Bacia?",
    inputSchema: zodToJsonSchema(crosswalkLookup.schema),
  },
];

// ---------- handlers ----------

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let text: string;

    switch (name) {
      case "lookup_term":
        text = lookupTerm.execute(lookupTerm.schema.parse(args));
        break;
      case "expand_acronym":
        text = expandAcronym.execute(expandAcronym.schema.parse(args));
        break;
      case "get_entity":
        text = getEntity.execute(getEntity.schema.parse(args));
        break;
      case "get_entity_neighbors":
        text = getEntityNeighbors.execute(getEntityNeighbors.schema.parse(args));
        break;
      case "validate_claim":
        text = await validateClaim.execute(validateClaim.schema.parse(args));
        break;
      case "cypher_query":
        text = await cypherQuery.execute(cypherQuery.schema.parse(args));
        break;
      case "search_rag":
        text = searchRag.execute(searchRag.schema.parse(args));
        break;
      case "list_layers":
        text = listLayers.execute({} as never);
        break;
      case "crosswalk_lookup":
        text = crosswalkLookup.execute(crosswalkLookup.schema.parse(args));
        break;
      default:
        return {
          content: [{ type: "text" as const, text: `Unknown tool: ${name}` }],
          isError: true,
        };
    }

    return {
      content: [{ type: "text" as const, text }],
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      content: [{ type: "text" as const, text: `Error: ${message}` }],
      isError: true,
    };
  }
});

// ---------- start ----------

const transport = new StdioServerTransport();
await server.connect(transport);
