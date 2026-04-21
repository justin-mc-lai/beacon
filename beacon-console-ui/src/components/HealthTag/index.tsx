import { Tag } from 'antd';

import type { HealthStatus } from '../../types/project';
import { getHealthColor, getHealthIcon, getHealthText } from '../../utils/health';

interface HealthTagProps {
  status: HealthStatus;
  showIcon?: boolean;
  showText?: boolean;
}

export function HealthTag({
  status,
  showIcon = true,
  showText = true,
}: HealthTagProps) {
  const color = getHealthColor(status);
  const icon = getHealthIcon(status);
  const text = getHealthText(status);

  return (
    <Tag color={color}>
      {showIcon && <span style={{ marginRight: 4 }}>{icon}</span>}
      {showText && text}
    </Tag>
  );
}
