import { useState } from 'react';
import {
  Breadcrumb,
  Card,
  Input,
  Progress,
  Select,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { useNavigate } from 'react-router-dom';

import { HealthTag } from '../../components/HealthTag';
import { PageTraceCard } from '../../components/PageTrace';
import { buildProjectDetailRoute } from '../../constants/routes';
import { getPageTrace, getProjects } from '../../data/consoleData';
import type { Project } from '../../types/project';
import {
  getDebugLabel,
  getDebugTone,
  getLifecycleLabel,
  getProjectKindLabel,
} from '../../utils/labels';

const columns: ColumnsType<Project> = [
  {
    title: '项目',
    dataIndex: 'name',
    key: 'name',
    render: (_, project) => <strong>{project.name}</strong>,
  },
  {
    title: '项目类型',
    key: 'kind',
    render: (_, project) => getProjectKindLabel(project.kind),
  },
  {
    title: '当前版本',
    dataIndex: 'currentVersion',
    key: 'currentVersion',
  },
  {
    title: '主 Feature',
    dataIndex: 'currentFeature',
    key: 'currentFeature',
  },
  {
    title: '当前阶段',
    dataIndex: 'lifecycle',
    key: 'lifecycle',
    render: (value) => getLifecycleLabel(value),
  },
  {
    title: '总进度',
    dataIndex: 'progress',
    key: 'progress',
    render: (value) => <Progress percent={value} size="small" />,
  },
  {
    title: '健康态',
    dataIndex: 'healthStatus',
    key: 'healthStatus',
    render: (value) => <HealthTag status={value} />,
  },
  {
    title: 'Debug',
    dataIndex: 'debugState',
    key: 'debugState',
    render: (value) => <Tag color={getDebugTone(value)}>{getDebugLabel(value)}</Tag>,
  },
  {
    title: '下一步',
    dataIndex: 'nextStep',
    key: 'nextStep',
  },
  {
    title: '推荐 Skill',
    dataIndex: 'recommendedSkill',
    key: 'recommendedSkill',
    render: (value) => <Tag color="blue">{value}</Tag>,
  },
];

export function ManagementOverviewPage() {
  const navigate = useNavigate();
  const allProjects = getProjects();
  const pageTrace = getPageTrace('management-overview');
  const [query, setQuery] = useState('');
  const [healthFilter, setHealthFilter] = useState<string>('all');
  const [stageFilter, setStageFilter] = useState<string>('all');

  const projects = allProjects.filter((project) => {
    const queryMatched =
      query.length === 0 ||
      project.name.toLowerCase().includes(query.toLowerCase()) ||
      project.currentFeature.toLowerCase().includes(query.toLowerCase());
    const healthMatched = healthFilter === 'all' || project.healthStatus === healthFilter;
    const stageMatched = stageFilter === 'all' || project.lifecycle === stageFilter;
    return queryMatched && healthMatched && stageMatched;
  });

  return (
    <div className="console-page">
      <Breadcrumb style={{ marginBottom: 16 }}>
        <Breadcrumb.Item href="/">首页</Breadcrumb.Item>
        <Breadcrumb.Item>管理总览</Breadcrumb.Item>
      </Breadcrumb>
      <Card
        title="多项目密集管理面"
        extra={<Tag color="cyan">Beacon projects only</Tag>}
      >
        <Typography.Paragraph className="console-muted">
          默认只收 Beacon 项目，不把 `omc / omx` 等外部系统混入注册表。
        </Typography.Paragraph>
        <Space wrap style={{ width: '100%', marginBottom: 16 }}>
          <Input.Search
            allowClear
            placeholder="搜索项目或 feature"
            style={{ width: 260 }}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <Select
            value={healthFilter}
            options={[
              { label: '健康态: 全部', value: 'all' },
              { label: '健康', value: 'healthy' },
              { label: '降级', value: 'degraded' },
              { label: '阻塞', value: 'blocked' },
              { label: '异常', value: 'error' },
            ]}
            onChange={setHealthFilter}
            style={{ width: 160 }}
          />
          <Select
            value={stageFilter}
            options={[
              { label: '阶段: 全部', value: 'all' },
              { label: 'PRD', value: 'prd' },
              { label: 'Prototype', value: 'prototype' },
              { label: 'Implement', value: 'implement' },
              { label: 'QA', value: 'qa' },
              { label: 'Release', value: 'release' },
            ]}
            onChange={setStageFilter}
            style={{ width: 180 }}
          />
          <Tag color="gold">已筛选 {projects.length} / {allProjects.length}</Tag>
        </Space>

        <Table
          rowKey="id"
          columns={columns}
          dataSource={projects}
          pagination={false}
          onRow={(project) => ({
            onClick: () => navigate(buildProjectDetailRoute(project.id)),
          })}
        />
      </Card>

      <div className="console-grid" style={{ marginTop: 16 }}>
        <Card title="阶段分布摘要">
          <ListSummary
            items={[
              `Implement: ${allProjects.filter((project) => project.lifecycle === 'implement').length}`,
              `QA: ${allProjects.filter((project) => project.lifecycle === 'qa').length}`,
              `Release: ${allProjects.filter((project) => project.lifecycle === 'release').length}`,
              `Blocked: ${allProjects.filter((project) => project.healthStatus === 'blocked').length}`,
            ]}
          />
        </Card>
        <Card title="风险与调试摘要">
          <ListSummary
            items={[
              'beacon：revision draft + QA blocked，需要 implement evidence 收口。',
              'shopxo_canada：回归环境不稳定，Ralph failure streak 上升。',
              'slow_uni_bmtop：仅剩 release sign-off，适合快速清线。',
            ]}
          />
        </Card>
      </div>

      <div style={{ marginTop: 16 }}>
        <PageTraceCard trace={pageTrace} />
      </div>
    </div>
  );
}

function ListSummary({ items }: { items: string[] }) {
  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      {items.map((item) => (
        <div key={item} className="summary-item">
          {item}
        </div>
      ))}
    </Space>
  );
}
