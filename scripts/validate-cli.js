#!/usr/bin/env node
'use strict';
/**
 * validate-cli.js — CLI wrapper for the semantic validator.
 *
 * Usage:
 *   node scripts/validate-cli.js "Reserva 4P do Campo de Búzios"
 *   node scripts/validate-cli.js --file claims.json
 *   node scripts/validate-cli.js --format text "Bloco BS-500 em regime de Concessão"
 *   node scripts/validate-cli.js --format json "Bloco BS-500 em regime de Privatização"
 */

const fs = require('node:fs');
const path = require('node:path');
const { validate } = require('./semantic-validator');

// ---------------------------------------------------------------------------
// Argument parsing (no external deps)
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const args = argv.slice(2);
  let format = 'json';
  let filePath = null;
  const claims = [];

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--format') {
      const next = args[i + 1];
      if (next === 'text' || next === 'json') {
        format = next;
        i++;
      } else {
        process.stderr.write(`Unknown format: ${next}. Use 'text' or 'json'.\n`);
        process.exit(1);
      }
    } else if (arg === '--file') {
      filePath = args[++i];
    } else if (!arg.startsWith('--')) {
      claims.push(arg);
    }
  }

  return { format, filePath, claims };
}

// ---------------------------------------------------------------------------
// Text formatter
// ---------------------------------------------------------------------------

function severity(v) {
  return v.severity ? v.severity.toUpperCase() : 'ERROR';
}

function formatText(results) {
  const lines = [];
  for (const { claim, result } of results) {
    const preview = typeof claim === 'string' ? claim : JSON.stringify(claim);
    lines.push(`--- Claim: ${preview.slice(0, 100)} ---`);
    lines.push(`Valid: ${result.valid}`);
    if (result.violations.length > 0) {
      lines.push(`Violations (${result.violations.length}):`);
      for (const v of result.violations) {
        lines.push(`  [${severity(v)}] ${v.rule}`);
        lines.push(`    Evidence:      ${v.evidence}`);
        lines.push(`    Suggested fix: ${v.suggested_fix}`);
        lines.push(`    Source layer:  ${v.source_layer || '-'}`);
      }
    }
    if (result.warnings.length > 0) {
      lines.push(`Warnings (${result.warnings.length}):`);
      for (const w of result.warnings) {
        lines.push(`  [WARN] ${w.rule}`);
        lines.push(`    Evidence:      ${w.evidence}`);
        lines.push(`    Suggested fix: ${w.suggested_fix}`);
        lines.push(`    Source layer:  ${w.source_layer || '-'}`);
      }
    }
    if (result.violations.length === 0 && result.warnings.length === 0) {
      lines.push('  No violations found.');
    }
    lines.push('');
  }
  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function main() {
  const { format, filePath, claims } = parseArgs(process.argv);

  let claimsToValidate = [];

  if (filePath) {
    const abs = path.resolve(filePath);
    if (!fs.existsSync(abs)) {
      process.stderr.write(`File not found: ${abs}\n`);
      process.exit(1);
    }
    let raw;
    try {
      raw = JSON.parse(fs.readFileSync(abs, 'utf8'));
    } catch (err) {
      process.stderr.write(`Failed to parse JSON file: ${err.message}\n`);
      process.exit(1);
    }
    if (Array.isArray(raw)) {
      claimsToValidate = raw;
    } else if (raw && typeof raw === 'object') {
      claimsToValidate = [raw];
    } else {
      process.stderr.write('JSON file must contain an array or object claim.\n');
      process.exit(1);
    }
  } else if (claims.length > 0) {
    claimsToValidate = claims;
  } else {
    process.stderr.write(
      'Usage: node scripts/validate-cli.js [--format text|json] [--file path.json] "<claim>"\n'
    );
    process.exit(1);
  }

  const results = claimsToValidate.map((claim) => ({ claim, result: validate(claim) }));

  if (format === 'text') {
    process.stdout.write(formatText(results));
  } else {
    const output = results.length === 1 ? results[0] : results;
    process.stdout.write(JSON.stringify(output, null, 2) + '\n');
  }

  // Exit with non-zero code if any claim has violations
  const hasViolations = results.some((r) => !r.result.valid);
  process.exit(hasViolations ? 1 : 0);
}

main();
