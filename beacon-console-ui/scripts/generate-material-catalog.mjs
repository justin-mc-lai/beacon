import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const uiRoot = path.resolve(__dirname, '..');
const repoRoot = path.resolve(uiRoot, '..');

const PROJECTS = [
  {
    id: 'slow-uni-bmtop',
    currentVersion: 'v0.9.2',
    aliases: [
      'slow_uni_bmtop',
      'slow-uni-bmtop',
      '/Users/apple/Developer/Personal/products/slow_uni_bmtop',
    ],
    inputs: ['docs/beacon'],
  },
  {
    id: 'rolo',
    currentVersion: 'v2.1.0',
    aliases: ['rolo', '/Users/apple/Developer/Personal/products/rolo'],
    inputs: ['docs/beacon'],
  },
  {
    id: 'shopxo-canada',
    currentVersion: 'v3.4.1',
    aliases: [
      'shopxo_canada',
      'shopxo-canada',
      '/Users/apple/Developer/Personal/products/shopxo_canada',
    ],
    inputs: ['docs/beacon'],
  },
];

const OUTPUT_PATH = path.join(uiRoot, 'src', 'data', 'generatedProjectMaterials.ts');
const SKIP_SEGMENTS = new Set([
  '.git',
  '.beacon',
  '.pytest_cache',
  'coverage',
  'dist',
  'node_modules',
  'tmp',
  'vendor',
]);
const SKIP_FILES = new Set(['AGENTS.md']);
const TYPE_PRIORITY = {
  summary: 0,
  prd: 1,
  'user-story': 2,
  'test-case': 3,
  prototype: 4,
  execution: 5,
  release: 6,
  architecture: 7,
  research: 8,
  plan: 9,
  report: 10,
  guide: 11,
};

function collectMarkdownFiles(basePath, inputPath) {
  const resolved = path.join(basePath, inputPath);
  if (!fs.existsSync(resolved)) {
    return [];
  }
  const stats = fs.statSync(resolved);
  if (stats.isFile()) {
    return resolved.endsWith('.md') ? [resolved] : [];
  }

  const files = [];
  const stack = [resolved];
  while (stack.length > 0) {
    const current = stack.pop();
    if (!current) {
      continue;
    }
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      if (SKIP_SEGMENTS.has(entry.name) || SKIP_FILES.has(entry.name)) {
        continue;
      }
      const nextPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(nextPath);
        continue;
      }
      if (entry.isFile() && nextPath.endsWith('.md')) {
        files.push(nextPath);
      }
    }
  }
  return files;
}

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function extractHeading(content) {
  const match = content.match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : '';
}

function stripMarkdown(value) {
  return value
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/[*_>#-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function extractSummary(content) {
  const lines = content
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .filter((line) => !line.startsWith('#'))
    .filter((line) => !line.startsWith('```'))
    .filter((line) => !line.startsWith('|'))
    .filter((line) => line !== '---');
  const summary = stripMarkdown(lines[0] ?? '');
  return summary.length > 140 ? `${summary.slice(0, 137)}...` : summary;
}

function toTitle(relativePath, content) {
  const heading = extractHeading(content);
  if (heading) {
    return heading;
  }
  const baseName = path.basename(relativePath, '.md');
  return baseName
    .replace(/[-_]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function inferVersion(relativePath, currentVersion) {
  const match = relativePath.match(/\/(v\d+\.\d+\.\d+)\//i);
  return match ? match[1] : currentVersion;
}

function inferType(relativePath) {
  const lower = relativePath.toLowerCase();
  if (lower.includes('/summary')) return 'summary';
  if (lower.includes('/prd/')) return 'prd';
  if (lower.includes('/user-story/') || lower.includes('user-stories')) return 'user-story';
  if (lower.includes('/test-case') || lower.includes('/test-cases/') || lower.includes('/qa/'))
    return 'test-case';
  if (lower.includes('/prototype/') || lower.includes('wireframe')) return 'prototype';
  if (lower.includes('/release/')) return 'release';
  if (lower.includes('/execution/')) return 'execution';
  if (
    lower.includes('/architecture/')
    || lower.includes('system-architecture')
    || lower.includes('feature-boundaries')
    || lower.includes('front-end-pages-routes')
    || lower.includes('frontend-pages-routes')
  ) {
    return 'architecture';
  }
  if (lower.includes('/research/') || lower.includes('/brainstorms/') || lower.includes('analysis')) {
    return 'research';
  }
  if (lower.includes('/plans/') || lower.includes('version-plan') || lower.includes('roadmap')) {
    return 'plan';
  }
  if (lower.includes('report') || lower.includes('progress') || lower.includes('acceptance')) {
    return 'report';
  }
  return 'guide';
}

function inferFeature(relativePath) {
  const normalized = relativePath.replace(/\\/g, '/');
  const parts = normalized.split('/');
  const anchor = parts.findIndex((part) =>
    [
      'prd',
      'user-story',
      'test-cases',
      'prototype',
      'execution',
      'release',
      'research',
      'plans',
      'brainstorms',
      'features',
      'architecture',
      'ui',
    ].includes(part.toLowerCase()),
  );
  if (anchor >= 0 && parts[anchor + 1]) {
    return parts[anchor + 1].replace(/\.md$/i, '');
  }
  if (parts[0] === 'docs' && parts[1]) {
    return parts[1].replace(/\.md$/i, '');
  }
  return path.basename(relativePath, '.md');
}

function slug(value) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function compareVersion(left, right) {
  const normalize = (value) =>
    value
      .replace(/^v/i, '')
      .split('.')
      .map((segment) => Number.parseInt(segment, 10) || 0);
  const l = normalize(left);
  const r = normalize(right);
  const length = Math.max(l.length, r.length);
  for (let index = 0; index < length; index += 1) {
    const delta = (r[index] ?? 0) - (l[index] ?? 0);
    if (delta !== 0) {
      return delta;
    }
  }
  return 0;
}

function matchesProjectAlias(content, aliases) {
  return aliases.some((alias) => content.includes(alias));
}

function buildProjectMaterials(project) {
  const files = project.inputs.flatMap((input) => collectMarkdownFiles(repoRoot, input));
  const seen = new Set();
  const documents = files
    .filter((filePath) => {
      const relativePath = path.relative(repoRoot, filePath).replace(/\\/g, '/');
      if (seen.has(relativePath)) {
        return false;
      }
      seen.add(relativePath);
      return true;
    })
    .map((filePath) => {
      const relativePath = path.relative(repoRoot, filePath).replace(/\\/g, '/');
      const content = fs.readFileSync(filePath, 'utf8');
      const stats = fs.statSync(filePath);
      return {
        id: `${project.id}-${slug(relativePath)}`,
        title: toTitle(relativePath, content),
        version: inferVersion(relativePath, project.currentVersion),
        type: inferType(relativePath),
        feature: inferFeature(relativePath),
        path: relativePath,
        summary: extractSummary(content) || '从项目工作区导入的受管 Markdown 文档材料。',
        content,
        relatedIds: [],
        createdAt: stats.birthtime.toISOString().slice(0, 10),
        updatedAt: stats.mtime.toISOString().slice(0, 10),
        matched: matchesProjectAlias(content, project.aliases),
      };
    })
    .filter((document) => document.matched)
    .sort((left, right) => {
      const versionOrder = compareVersion(left.version, right.version);
      if (versionOrder !== 0) {
        return versionOrder;
      }
      const typeOrder = (TYPE_PRIORITY[left.type] ?? 99) - (TYPE_PRIORITY[right.type] ?? 99);
      if (typeOrder !== 0) {
        return typeOrder;
      }
      return left.path.localeCompare(right.path, 'en');
    });

  const byVersion = new Map();
  const byType = new Map();
  const byFeature = new Map();
  for (const document of documents) {
    byVersion.set(document.version, [...(byVersion.get(document.version) ?? []), document.id]);
    byType.set(document.type, [...(byType.get(document.type) ?? []), document.id]);
    byFeature.set(document.feature, [...(byFeature.get(document.feature) ?? []), document.id]);
  }

  return documents.map((document) => {
    const related = new Set([
      ...(byVersion.get(document.version) ?? []),
      ...(byType.get(document.type) ?? []),
      ...(byFeature.get(document.feature) ?? []),
    ]);
    related.delete(document.id);
    return {
      ...document,
      relatedIds: Array.from(related).slice(0, 8),
    };
  }).map(({ matched: _matched, ...document }) => document);
}

const generatedProjectMaterials = Object.fromEntries(
  PROJECTS.map((project) => [project.id, buildProjectMaterials(project)]),
);

const fileContents = `import type { MaterialDocument } from '../types/project';

export const generatedProjectMaterials: Record<string, MaterialDocument[]> = ${JSON.stringify(
  generatedProjectMaterials,
  null,
  2,
)} as Record<string, MaterialDocument[]>;
`;

fs.writeFileSync(OUTPUT_PATH, fileContents);

console.log(
  `generated material catalog for ${Object.keys(generatedProjectMaterials).length} project(s): ${path.relative(
    repoRoot,
    OUTPUT_PATH,
  )}`,
);
