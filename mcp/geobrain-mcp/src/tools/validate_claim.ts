/**
 * validate_claim — delegates to scripts/semantic-validator.js (P1.4).
 *
 * If the validator script is not found, returns a graceful error rather than
 * crashing the server.
 */

import { z } from "zod";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

export const schema = z.object({
  text: z.string().min(1).describe("Natural-language claim to validate against the ontology"),
});

type Input = z.infer<typeof schema>;

const __dirname = dirname(fileURLToPath(import.meta.url));
// At runtime: dist/tools/validate_claim.js
// dist/tools/ -> dist/ -> geolytics-mcp/ -> mcp/ -> repo root  (4 levels up)
const REPO_ROOT = resolve(__dirname, "../../../..");
const VALIDATOR_PATH = resolve(REPO_ROOT, "scripts/semantic-validator.js");

let _validatorModule: { validate?: (text: string) => unknown } | null | undefined = undefined;

async function loadValidator(): Promise<typeof _validatorModule> {
  if (_validatorModule !== undefined) return _validatorModule;
  if (!existsSync(VALIDATOR_PATH)) {
    _validatorModule = null;
    return null;
  }
  try {
    _validatorModule = (await import(/* @vite-ignore */ `file://${VALIDATOR_PATH}`)) as {
      validate?: (text: string) => unknown;
    };
    return _validatorModule;
  } catch {
    _validatorModule = null;
    return null;
  }
}

export async function execute(input: Input): Promise<string> {
  const validator = await loadValidator();

  if (!validator || typeof validator.validate !== "function") {
    return JSON.stringify({
      valid: null,
      error: "validator unavailable",
      detail: "scripts/semantic-validator.js not found. This tool requires P1.4 to be implemented.",
    });
  }

  try {
    const report = await Promise.resolve(validator.validate(input.text));
    return JSON.stringify(report, null, 2);
  } catch (err) {
    return JSON.stringify({
      valid: null,
      error: "validator error",
      detail: err instanceof Error ? err.message : String(err),
    });
  }
}
