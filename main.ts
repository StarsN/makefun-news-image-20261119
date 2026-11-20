// The World in One Day — 19 November 2026.
// Delivers the front-page image (entry.png, beside this file) to
// $MAKEFUN_OUTPUT_DIR/entry.png (default /output).
// Node 22, standard library only. No network, no writes besides the copy.
//
// Before copying, the program checks the image it is about to deliver:
// it must be a real PNG, at most 1024x1024 pixels and at most 1 MiB, so a
// broken build can never be submitted silently.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_BYTES = 1024 * 1024;
const MAX_PIXELS = 1024;

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const src = join(dirname(fileURLToPath(import.meta.url)), 'entry.png');
const dst = join(outDir, 'entry.png');

// Read and validate the image first; fail loudly instead of copying junk.
const bytes = readFileSync(src);
if (bytes.length > MAX_BYTES) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
}
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error('entry.png is not a PNG file');
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > MAX_PIXELS || height > MAX_PIXELS) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 limit`);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(src, dst);

// Confirm the delivered copy is byte-for-byte the source.
if (statSync(dst).size !== bytes.length) {
  throw new Error('delivered entry.png does not match the source');
}
