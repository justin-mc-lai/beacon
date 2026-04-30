import type { MaterialDocument } from '../types/project';
import { getProjectById } from './consoleData';
import { generatedProjectMaterials } from './generatedProjectMaterials';

export function getProjectMaterials(projectId?: string): MaterialDocument[] {
  const staticMaterials = getProjectById(projectId)?.materials ?? [];
  const generatedMaterials = projectId ? (generatedProjectMaterials[projectId] ?? []) : [];
  const merged = [...staticMaterials, ...generatedMaterials];
  const deduped = new Map(merged.map((material) => [material.id, material]));
  return Array.from(deduped.values());
}

export function getMaterialById(
  projectId: string | undefined,
  materialId: string | undefined,
): MaterialDocument | undefined {
  return getProjectMaterials(projectId).find((material) => material.id === materialId);
}

export function getRelatedMaterials(
  projectId: string | undefined,
  materialId: string | undefined,
): MaterialDocument[] {
  const current = getMaterialById(projectId, materialId);
  if (!current) {
    return [];
  }

  const materials = getProjectMaterials(projectId);
  const explicit = materials.filter((item) => current.relatedIds.includes(item.id));
  if (explicit.length > 0) {
    return explicit;
  }

  return materials
    .filter((item) => item.id !== current.id)
    .filter(
      (item) =>
        item.version === current.version
        || item.type === current.type
        || item.feature === current.feature,
    )
    .slice(0, 8);
}
