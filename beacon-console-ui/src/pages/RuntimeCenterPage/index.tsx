import { Breadcrumb, Card, Descriptions, List, Segmented, Space, Table, Tag, Typography } from 'antd';
import { useState } from 'react';
import { Navigate, useParams } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';

import { PageTraceCard } from '../../components/PageTrace';
import { ROUTES } from '../../constants/routes';
import { getPageTrace, getProjectById } from '../../data/consoleData';
import type { RuntimeMode, TeamAgent } from '../../types/project';
import { getLifecycleLabel, getRuntimeModeLabel } from '../../utils/labels';

const teamColumns: ColumnsType<TeamAgent> = [
  {
    title: 'Agent',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: 'Role',
    dataIndex: 'role',
    key: 'role',
  },
  {
    title: 'Status',
    dataIndex: 'status',
    key: 'status',
    render: (value) => <Tag color={value === 'running' ? 'processing' : 'default'}>{value}</Tag>,
  },
  {
    title: 'Linked Run',
    dataIndex: 'linkedRun',
    key: 'linkedRun',
  },
  {
    title: 'Artifacts',
    dataIndex: 'artifactRefs',
    key: 'artifactRefs',
    render: (value) => value.join(' · '),
  },
  {
    title: 'Session Metadata',
    key: 'session',
    render: (_, agent) =>
      `${agent.session.host} / ${agent.session.sessionRef} / ${agent.session.transcriptRef}`,
  },
];

export function RuntimeCenterPage() {
  const { id } = useParams();
  const project = getProjectById(id);
  const pageTrace = getPageTrace('runtime-center');
  const [mode, setMode] = useState<RuntimeMode>(project?.runtimeSummary.activeMode ?? 'single');

  if (!project) {
    return <Navigate to={ROUTES.MANAGEMENT} replace />;
  }

  const detail =
    project.runtimeDetails.find((item) => item.mode === mode) ?? project.runtimeDetails[0];

  return (
    <div className="console-page">
      <Breadcrumb style={{ marginBottom: 16 }}>
        <Breadcrumb.Item href="/">首页</Breadcrumb.Item>
        <Breadcrumb.Item href={ROUTES.MANAGEMENT}>管理总览</Breadcrumb.Item>
        <Breadcrumb.Item href={`/project/${project.id}`}>{project.name}</Breadcrumb.Item>
        <Breadcrumb.Item>运行中心</Breadcrumb.Item>
      </Breadcrumb>

      <Card
        title={`${project.name} · 运行中心`}
        extra={<Tag color="purple">{getRuntimeModeLabel(detail.mode)}</Tag>}
      >
        <Descriptions column={4} size="small">
          <Descriptions.Item label="当前模式">{getRuntimeModeLabel(detail.mode)}</Descriptions.Item>
          <Descriptions.Item label="状态">{detail.status}</Descriptions.Item>
          <Descriptions.Item label="阶段">{getLifecycleLabel(detail.stage)}</Descriptions.Item>
          <Descriptions.Item label="Linked Run">{detail.linkedRun}</Descriptions.Item>
        </Descriptions>
        <Typography.Paragraph className="console-muted" style={{ marginTop: 12 }}>
          这里只展示有限的 host session metadata、artifact 引用与 recent result，不把完整宿主会话系统并入 Beacon truth。
        </Typography.Paragraph>
        <Segmented
          block
          style={{ marginTop: 16 }}
          options={[
            { label: 'Single', value: 'single' },
            { label: 'Team', value: 'team' },
            { label: 'Ralph', value: 'ralph' },
          ]}
          value={mode}
          onChange={(value) => setMode(value as RuntimeMode)}
        />
      </Card>

      <div className="console-grid console-grid--primary" style={{ marginTop: 16 }}>
        <Card title="运行态摘要">
          <List
            dataSource={[
              `Summary: ${detail.summary}`,
              `Started At: ${detail.startedAt}`,
              `Completed At: ${detail.completedAt ?? 'still running'}`,
              `Artifacts: ${detail.artifactRefs.join(' · ') || 'none'}`,
            ]}
            renderItem={(item) => <List.Item>{item}</List.Item>}
          />
        </Card>
        <Card title="最近结果与 blocker">
          <List
            dataSource={detail.timeline}
            renderItem={(item) => <List.Item>{item}</List.Item>}
          />
        </Card>
      </div>

      {detail.mode === 'team' && detail.teamAgents ? (
        <Card title="Team 代理态" style={{ marginTop: 16 }}>
          <Table
            rowKey="name"
            columns={teamColumns}
            dataSource={detail.teamAgents}
            pagination={false}
          />
        </Card>
      ) : null}

      {detail.mode === 'single' && detail.hostSession ? (
        <Card title="Single Session 引用" style={{ marginTop: 16 }}>
          <Descriptions column={2}>
            <Descriptions.Item label="Host">{detail.hostSession.host}</Descriptions.Item>
            <Descriptions.Item label="Session Ref">{detail.hostSession.sessionRef}</Descriptions.Item>
            <Descriptions.Item label="Updated">{detail.hostSession.updatedAt}</Descriptions.Item>
            <Descriptions.Item label="Transcript Ref">
              {detail.hostSession.transcriptRef}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      ) : null}

      {detail.mode === 'ralph' && detail.ralphLoop ? (
        <Card title="Ralph 闭环观察" style={{ marginTop: 16 }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Descriptions column={2}>
              <Descriptions.Item label="Round Count">
                {detail.ralphLoop.roundCount}
              </Descriptions.Item>
              <Descriptions.Item label="Failure Streak">
                {detail.ralphLoop.failureStreak}
              </Descriptions.Item>
              <Descriptions.Item label="Next Action">
                {detail.ralphLoop.nextAction}
              </Descriptions.Item>
              <Descriptions.Item label="Blocker">{detail.ralphLoop.blocker}</Descriptions.Item>
            </Descriptions>
            <Card size="small" title="Recent Result">
              {detail.ralphLoop.recentResult}
            </Card>
          </Space>
        </Card>
      ) : null}

      <div style={{ marginTop: 16 }}>
        <PageTraceCard trace={pageTrace} />
      </div>
    </div>
  );
}
