import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

import {
  renderStructureMap,
  validateConfig,
} from '../scripts/render-structure-map.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const skillDir = path.resolve(__dirname, '..');
const templatePath = path.join(skillDir, 'templates', 'structure-map-cytoscape.html');
const exampleConfigPath = path.join(skillDir, 'examples', 'structure-map.config.example.json');

async function withTempDir(fn) {
  const dir = await mkdtemp(path.join(tmpdir(), 'structure-map-renderer-'));
  try {
    return await fn(dir);
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
}

async function loadExampleConfig() {
  return JSON.parse(await readFile(exampleConfigPath, 'utf8'));
}

test('renders example config through the official template', async () => {
  await withTempDir(async (dir) => {
    const outputPath = path.join(dir, 'structure-map.html');

    await renderStructureMap({
      configPath: exampleConfigPath,
      templatePath,
      outputPath,
    });

    const html = await readFile(outputPath, 'utf8');
    assert.match(html, /data-template="structure-map-cytoscape-v1"/);
    assert.match(html, /data-generated-by="structure-map-renderer-v1"/);
    assert.match(html, /const graphElements = \[/);
    assert.match(html, /"source": "problem"/);
    assert.match(html, /STRUCTURE_MAP_RENDERER:GRAPH_ELEMENTS_START/);
    assert.doesNotMatch(html, /__PLACEHOLDER__/);
  });
});

test('rejects duplicate node IDs', async () => {
  const config = await loadExampleConfig();
  config.nodes.push({ ...config.nodes[0], label: '중복 노드' });

  assert.throws(
    () => validateConfig(config),
    /duplicate node id: problem/,
  );
});

test('rejects edges that point to missing nodes', async () => {
  const config = await loadExampleConfig();
  config.edges[0].target = 'missing-node';

  assert.throws(
    () => validateConfig(config),
    /edge e1 target does not exist: missing-node/,
  );
});

test('rejects unsupported node types', async () => {
  const config = await loadExampleConfig();
  config.nodes[0].type = 'freeform';

  assert.throws(
    () => validateConfig(config),
    /node problem has unsupported type: freeform/,
  );
});

test('fails when a required template marker pair is missing', async () => {
  await withTempDir(async (dir) => {
    const brokenTemplatePath = path.join(dir, 'broken-template.html');
    const outputPath = path.join(dir, 'structure-map.html');
    const template = await readFile(templatePath, 'utf8');
    await writeFile(
      brokenTemplatePath,
      template.replace('STRUCTURE_MAP_RENDERER:TITLE_START', 'STRUCTURE_MAP_RENDERER:TITLE_REMOVED'),
      'utf8',
    );

    await assert.rejects(
      () => renderStructureMap({
        configPath: exampleConfigPath,
        templatePath: brokenTemplatePath,
        outputPath,
      }),
      /missing template marker pair: TITLE/,
    );
  });
});
