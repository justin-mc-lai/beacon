import { Card, List, Tag } from 'antd';

import type { PageTrace } from '../../types/common';

interface PageTraceProps {
  trace: PageTrace;
}

export function PageTraceCard({ trace }: PageTraceProps) {
  return (
    <Card
      title={`Freeze 回链 · ${trace.pageName}`}
      extra={<Tag color="blue">{trace.pageId}</Tag>}
    >
      <div className="trace-card">
        <div>
          <p className="trace-card__label">上游 freeze 证据</p>
          <List
            size="small"
            dataSource={trace.freezeLinks}
            renderItem={(item) => (
              <List.Item>
                <div>
                  <strong>{item.label}</strong>
                  <div className="trace-card__path">{item.path}</div>
                  <div className="trace-card__note">{item.note}</div>
                </div>
              </List.Item>
            )}
          />
        </div>
        <div>
          <p className="trace-card__label">当前实现映射</p>
          <List
            size="small"
            dataSource={trace.currentSpecLinks}
            renderItem={(item) => (
              <List.Item>
                <div>
                  <strong>{item.label}</strong>
                  <div className="trace-card__path">{item.path}</div>
                  <div className="trace-card__note">{item.note}</div>
                </div>
              </List.Item>
            )}
          />
        </div>
      </div>
      <div className="trace-card__ac">
        {trace.acceptanceCriteria.map((acId) => (
          <Tag key={acId}>{acId}</Tag>
        ))}
      </div>
    </Card>
  );
}
