#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DEFAULT_TEMPLATE_PATH = path.resolve(__dirname, '..', 'templates', 'structure-map-cytoscape.html');
const RENDERER_MARKER = 'structure-map-renderer-v1';
const ALLOWED_NODE_TYPES = new Set(['problem', 'concept', 'runtime', 'verify', 'doc']);
const REQUIRED_HTML_SECTIONS = ['TITLE', 'HEADING', 'HELP', 'LEGEND', 'FALLBACK', 'INITIAL_DETAIL'];
const REQUIRED_JS_SECTIONS = ['GRAPH_ELEMENTS'];

function usage() {
  return [
    'Usage:',
    '  node structure-map-html/scripts/render-structure-map.mjs --config <config.json> --out <structure-map.html> [--template <template.html>]',
  ].join('\n');
}

function parseArgs(argv = process.argv.slice(2)) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const flag = argv[index];
    if (!flag.startsWith('--')) {
      throw new Error(`unexpected argument: ${flag}\n${usage()}`);
    }
    const key = flag.slice(2);
    const value = argv[index + 1];
    if (!value || value.startsWith('--')) {
      throw new Error(`missing value for --${key}\n${usage()}`);
    }
    args[key] = value;
    index += 1;
  }

  if (!args.config) {
    throw new Error(`missing --config\n${usage()}`);
  }
  if (!args.out) {
    throw new Error(`missing --out\n${usage()}`);
  }

  return {
    configPath: path.resolve(args.config),
    outputPath: path.resolve(args.out),
    templatePath: args.template ? path.resolve(args.template) : DEFAULT_TEMPLATE_PATH,
  };
}

function assertPlainObject(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`${label} must be an object`);
  }
}

function assertString(value, label) {
  if (typeof value !== 'string' || !value.trim()) {
    throw new Error(`${label} must be a non-empty string`);
  }
}

function assertArray(value, label) {
  if (!Array.isArray(value) || value.length === 0) {
    throw new Error(`${label} must be a non-empty array`);
  }
}

function assertNumber(value, label) {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new Error(`${label} must be a finite number`);
  }
}

function normalizeString(value) {
  return String(value || '').trim();
}

function validateConfig(config) {
  assertPlainObject(config, 'config');
  assertString(config.title, 'title');
  assertString(config.help, 'help');
  assertPlainObject(config.initialDetail, 'initialDetail');
  assertString(config.initialDetail.kind, 'initialDetail.kind');
  assertString(config.initialDetail.title, 'initialDetail.title');
  assertString(config.initialDetail.body, 'initialDetail.body');
  if (config.initialDetail.hint !== undefined) {
    assertString(config.initialDetail.hint, 'initialDetail.hint');
  }
  assertArray(config.legend, 'legend');
  assertArray(config.fallback, 'fallback');
  assertArray(config.nodes, 'nodes');
  assertArray(config.edges, 'edges');

  const nodeIds = new Set();
  for (const node of config.nodes) {
    assertPlainObject(node, 'node');
    assertString(node.id, 'node.id');
    if (nodeIds.has(node.id)) {
      throw new Error(`duplicate node id: ${node.id}`);
    }
    nodeIds.add(node.id);
    assertString(node.label, `node ${node.id}.label`);
    assertString(node.type, `node ${node.id}.type`);
    if (!ALLOWED_NODE_TYPES.has(node.type)) {
      throw new Error(`node ${node.id} has unsupported type: ${node.type}`);
    }
    assertString(node.detail, `node ${node.id}.detail`);
    assertPlainObject(node.position, `node ${node.id}.position`);
    assertNumber(node.position.x, `node ${node.id}.position.x`);
    assertNumber(node.position.y, `node ${node.id}.position.y`);
  }

  const legendTypes = new Set();
  for (const item of config.legend) {
    assertPlainObject(item, 'legend item');
    assertString(item.type, 'legend.type');
    if (!ALLOWED_NODE_TYPES.has(item.type)) {
      throw new Error(`legend has unsupported type: ${item.type}`);
    }
    assertString(item.label, `legend ${item.type}.label`);
    legendTypes.add(item.type);
  }

  for (const node of config.nodes) {
    if (!legendTypes.has(node.type)) {
      throw new Error(`node ${node.id} type is missing from legend: ${node.type}`);
    }
  }

  config.fallback.forEach((item, index) => {
    assertString(item, `fallback[${index}]`);
  });

  const edgeIds = new Set();
  for (const edge of config.edges) {
    assertPlainObject(edge, 'edge');
    assertString(edge.id, 'edge.id');
    if (edgeIds.has(edge.id)) {
      throw new Error(`duplicate edge id: ${edge.id}`);
    }
    edgeIds.add(edge.id);
    assertString(edge.source, `edge ${edge.id}.source`);
    assertString(edge.target, `edge ${edge.id}.target`);
    if (!nodeIds.has(edge.source)) {
      throw new Error(`edge ${edge.id} source does not exist: ${edge.source}`);
    }
    if (!nodeIds.has(edge.target)) {
      throw new Error(`edge ${edge.id} target does not exist: ${edge.target}`);
    }
    assertString(edge.label, `edge ${edge.id}.label`);
    if (edge.displayLabel !== undefined) {
      assertString(edge.displayLabel, `edge ${edge.id}.displayLabel`);
    }
    if (edge.detail !== undefined) {
      assertString(edge.detail, `edge ${edge.id}.detail`);
    }
  }

  return config;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function htmlSection(name, content) {
  return [
    `<!-- STRUCTURE_MAP_RENDERER:${name}_START -->`,
    content,
    `<!-- STRUCTURE_MAP_RENDERER:${name}_END -->`,
  ].join('\n');
}

function jsSection(name, content) {
  return [
    `// STRUCTURE_MAP_RENDERER:${name}_START`,
    content,
    `// STRUCTURE_MAP_RENDERER:${name}_END`,
  ].join('\n');
}

function replaceMarkedSection(template, name, content, syntax = 'html') {
  const start = syntax === 'js'
    ? `// STRUCTURE_MAP_RENDERER:${name}_START`
    : `<!-- STRUCTURE_MAP_RENDERER:${name}_START -->`;
  const end = syntax === 'js'
    ? `// STRUCTURE_MAP_RENDERER:${name}_END`
    : `<!-- STRUCTURE_MAP_RENDERER:${name}_END -->`;
  const startIndex = template.indexOf(start);
  const endIndex = template.indexOf(end);
  if (startIndex === -1 || endIndex === -1 || endIndex < startIndex) {
    throw new Error(`missing template marker pair: ${name}`);
  }
  const replacement = syntax === 'js' ? jsSection(name, content) : htmlSection(name, content);
  return `${template.slice(0, startIndex)}${replacement}${template.slice(endIndex + end.length)}`;
}

function addRendererMarker(html) {
  if (/data-generated-by=(["'])structure-map-renderer-v1\1/.test(html)) {
    return html;
  }
  return html.replace(
    /<html\b([^>]*)>/i,
    (match, attrs) => `<html${attrs} data-generated-by="${RENDERER_MARKER}">`,
  );
}

function buildGraphElements(config) {
  const nodes = config.nodes.map((node) => ({
    data: {
      id: normalizeString(node.id),
      label: normalizeString(node.label),
      type: normalizeString(node.type),
      detail: normalizeString(node.detail),
    },
    position: {
      x: node.position.x,
      y: node.position.y,
    },
  }));

  const edges = config.edges.map((edge) => {
    const data = {
      id: normalizeString(edge.id),
      source: normalizeString(edge.source),
      target: normalizeString(edge.target),
      label: normalizeString(edge.label),
    };
    if (edge.displayLabel !== undefined) {
      data.displayLabel = normalizeString(edge.displayLabel);
    }
    if (edge.detail !== undefined) {
      data.detail = normalizeString(edge.detail);
    }
    if (edge.curve !== undefined) {
      data.curve = edge.curve;
    }
    return { data };
  });

  return [...nodes, ...edges];
}

function renderLegend(config) {
  return config.legend
    .map((item) => `            <li><span class="dot ${escapeHtml(item.type)}"></span><span>${escapeHtml(item.label)}</span></li>`)
    .join('\n');
}

function renderFallback(config) {
  const lines = config.fallback
    .map((item) => `            <li>${escapeHtml(item)}</li>`)
    .join('\n');
  return [
    '          Cytoscape.js를 불러오지 못해 텍스트 fallback을 표시합니다.',
    '          <ul>',
    lines,
    '          </ul>',
  ].join('\n');
}

function renderInitialDetail(config) {
  const detail = config.initialDetail;
  const hint = detail.hint
    ? `          <span class="hint">${escapeHtml(detail.hint)}</span>`
    : '';
  return [
    `          <span class="kind">${escapeHtml(detail.kind)}</span>`,
    `          <strong>${escapeHtml(detail.title)}</strong>`,
    `          <span>${escapeHtml(detail.body)}</span>`,
    hint,
  ].filter(Boolean).join('\n');
}

function renderGraphElements(config) {
  return `    const graphElements = ${JSON.stringify(buildGraphElements(config), null, 6)};`;
}

function renderHtml(template, config) {
  for (const name of REQUIRED_HTML_SECTIONS) {
    const marker = `STRUCTURE_MAP_RENDERER:${name}_START`;
    if (!template.includes(marker)) {
      throw new Error(`missing template marker pair: ${name}`);
    }
  }
  for (const name of REQUIRED_JS_SECTIONS) {
    const marker = `STRUCTURE_MAP_RENDERER:${name}_START`;
    if (!template.includes(marker)) {
      throw new Error(`missing template marker pair: ${name}`);
    }
  }

  let html = template;
  html = addRendererMarker(html);
  html = replaceMarkedSection(html, 'TITLE', `  <title>${escapeHtml(config.title)}</title>`);
  html = replaceMarkedSection(html, 'HEADING', `      <h1>${escapeHtml(config.title)}</h1>`);
  html = replaceMarkedSection(html, 'HELP', `          ${escapeHtml(config.help)}`);
  html = replaceMarkedSection(html, 'LEGEND', renderLegend(config));
  html = replaceMarkedSection(html, 'FALLBACK', renderFallback(config));
  html = replaceMarkedSection(html, 'INITIAL_DETAIL', renderInitialDetail(config));
  html = replaceMarkedSection(html, 'GRAPH_ELEMENTS', renderGraphElements(config), 'js');
  return html;
}

async function loadConfig(configPath) {
  const raw = await readFile(configPath, 'utf8');
  const config = JSON.parse(raw);
  return validateConfig(config);
}

async function renderStructureMap({ configPath, templatePath = DEFAULT_TEMPLATE_PATH, outputPath }) {
  if (!configPath) {
    throw new Error('configPath is required');
  }
  if (!outputPath) {
    throw new Error('outputPath is required');
  }
  const [config, template] = await Promise.all([
    loadConfig(configPath),
    readFile(templatePath, 'utf8'),
  ]);
  const html = renderHtml(template, config);
  await mkdir(path.dirname(outputPath), { recursive: true });
  await writeFile(outputPath, html, 'utf8');
  return outputPath;
}

async function main() {
  const options = parseArgs();
  await renderStructureMap(options);
  process.stdout.write(`wrote ${options.outputPath}\n`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  main().catch((error) => {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  });
}

export {
  ALLOWED_NODE_TYPES,
  buildGraphElements,
  parseArgs,
  renderHtml,
  renderStructureMap,
  validateConfig,
};
