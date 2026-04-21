import type { HealthStatus } from '../types/project';

export const getHealthColor = (status: HealthStatus): string => {
  const colorMap: Record<HealthStatus, string> = {
    healthy: '#52c41a',
    degraded: '#d48806',
    blocked: '#ff4d4f',
    error: '#531dab',
  };
  return colorMap[status];
};

export const getHealthText = (status: HealthStatus): string => {
  const textMap: Record<HealthStatus, string> = {
    healthy: '健康',
    degraded: '降级',
    blocked: '阻塞',
    error: '异常',
  };
  return textMap[status];
};

export const getHealthIcon = (status: HealthStatus): string => {
  const iconMap: Record<HealthStatus, string> = {
    healthy: '✅',
    degraded: '🛠',
    blocked: '⛔',
    error: '🧭',
  };
  return iconMap[status];
};
