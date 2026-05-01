/**
 * cypher_query — executes a Cypher query against Neo4j.
 *
 * Only active when NEO4J_URI env var is set. Uses the official neo4j driver
 * via dynamic import so that the server still boots without it installed.
 */

import { z } from "zod";

export const schema = z.object({
  query: z
    .string()
    .min(1)
    .describe("Cypher query to run (e.g. MATCH (n:Entity) RETURN n LIMIT 5)"),
});

type Input = z.infer<typeof schema>;

const SETUP_HINT = `
To enable cypher_query, start Neo4j and set these environment variables:
  NEO4J_URI=bolt://localhost:7687
  NEO4J_USER=neo4j
  NEO4J_PASSWORD=geolytics123

Quick start with Docker:
  docker compose up -d
  # wait ~30 s for Neo4j to be ready, then load data:
  docker compose run --rm loader

Schema: see build/neo4j/nodes.cypher and build/neo4j/relationships.cypher
Example query: MATCH (p:Entity {id:'poco'})-[r]->(b:Entity) RETURN p,r,b LIMIT 10
`.trim();

export async function execute(input: Input): Promise<string> {
  const uri = process.env["NEO4J_URI"];
  if (!uri) {
    return JSON.stringify({
      error: "Neo4j not configured",
      detail: SETUP_HINT,
    });
  }

  const user = process.env["NEO4J_USER"] ?? "neo4j";
  const password = process.env["NEO4J_PASSWORD"] ?? "";

  let neo4j: {
    driver: (uri: string, auth: unknown) => {
      session: () => {
        run: (q: string) => Promise<{ records: Array<{ toObject: () => unknown }> }>;
        close: () => Promise<void>;
      };
      close: () => Promise<void>;
    };
    auth: { basic: (u: string, p: string) => unknown };
  };

  try {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore — optional peer dep, not listed in devDependencies
    neo4j = (await import("neo4j-driver")) as typeof neo4j;
  } catch {
    return JSON.stringify({
      error: "neo4j-driver not installed",
      detail: "Run: npm install neo4j-driver  inside mcp/geolytics-mcp/",
    });
  }

  const driver = neo4j.driver(uri, neo4j.auth.basic(user, password));
  const session = driver.session();

  try {
    const result = await session.run(input.query);
    const records = result.records.map((r) => r.toObject());
    return JSON.stringify({ ok: true, records_count: records.length, records }, null, 2);
  } catch (err) {
    return JSON.stringify({
      ok: false,
      error: err instanceof Error ? err.message : String(err),
    });
  } finally {
    await session.close();
    await driver.close();
  }
}
