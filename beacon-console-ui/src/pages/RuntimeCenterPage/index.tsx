import {
  Breadcrumb,
  Card,
  Descriptions,
  List,
  Segmented,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import { useState } from 'react';
import { Navigate, useParams } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';

import { PageTraceCard } from '../../components/PageTrace';
import { ROUTES } from '../../constants/routes';
import { getPageTrace, getProjectById } from '../../data/consoleData';
import type { RuntimeMode, TeamAgent } from '../../types/project';
import {
  getLifecycleLabel,
  getRuntimeModeLabel,
  getRuntimeStatusLabel,
} from '../../utils/labels';

const teamColumns: ColumnsType<TeamAgent> = [
  {
    title: '执行单元',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: '职责',
    dataIndex: 'role',
    key: 'role',
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    render: (value) => (
      <Tag color={value === 'running' ? 'processing' : 'default'}>
        {getRuntimeStatusLabel(value)}
      </Tag>
    ),
  },
  {
    title: '关联执行批次',
    dataIndex: 'linkedRun',
    key: 'linkedRun',
  },
  {
    title: '产物引用',
    dataIndex: 'artifactRefs',
    key: 'artifactRefs',
    render: (value) => value.join(' · '),
  },
  {
    title: '会话元数据',
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
        <Breadcrumb.Item>执行中心</Breadcrumb.Item>
      </Breadcrumb>

      <Card
        title={`${project.name} · 执行中心`}
        extra={<Tag color="purple">{getRuntimeModeLabel(detail.mode)}</Tag>}
      >
        <Descriptions column={4} size="small">
          <Descriptions.Item label="当前模式">{getRuntimeModeLabel(detail.mode)}</Descriptions.Item>
          <Descriptions.Item label="状态">{getRuntimeStatusLabel(detail.status)}</Descriptions.Item>
          <Descriptions.Item label="阶段">{getLifecycleLabel(detail.stage)}</Descriptions.Item>
          <Descriptions.Item label="关联执行批次">{detail.linkedRun}</Descriptions.Item>
        </Descriptions>
        <Typography.Paragraph className="console-muted" style={{ marginTop: 12 }}>
          当前页面只展示受控的宿主会话引用、产物定位与最近结果，
          不把完整宿主会话系统直接并入 Beacon 正式真相。
        </Typography.Paragraph>
        <Segmented
          block
          style={{ marginTop: 16 }}
          options={[
            { label: getRuntimeModeLabel('single'), value: 'single' },
            { label: getRuntimeModeLabel('team'), value: 'team' },
            { label: getRuntimeModeLabel('ralph'), value: 'ralph' },
          ]}
          value={mode}
          onChange={(value) => setMode(value as RuntimeMode)}
        />
      </Card>

      <div className="console-grid console-grid--primary" style={{ marginTop: 16 }}>
        <Card title="执行态摘要">
          <List
            dataSource={[
              `执行摘要：${detail.summary}`,
              `开始时间：${detail.startedAt}`,
              `完成时间：${detail.completedAt ?? '仍在执行'}`,
              `产物引用：${detail.artifactRefs.join(' · ') || '暂无'}`,
            ]}
            renderItem={(item) => <List.Item>{item}</List.Item>}
          />
        </Card>
        <Card title="最近结果与阻塞事项">
          <List
            dataSource={detail.timeline}
            renderItem={(item) => <List.Item>{item}</List.Item>}
          />
        </Card>
      </div>

      {detail.mode === 'team' && detail.teamAgents ? (
        <Card title="协同执行单元视图" style={{ marginTop: 16 }}>
          <Table
            rowKey="name"
            columns={teamColumns}
            dataSource={detail.teamAgents}
            pagination={false}
          />
        </Card>
      ) : null}

      {detail.mode === 'single' && detail.hostSession ? (
        <Card title="单线会话引用" style={{ marginTop: 16 }}>
          <Descriptions column={2}>
            <Descriptions.Item label="宿主">{detail.hostSession.host}</Descriptions.Item>
            <Descriptions.Item label="会话引用">{detail.hostSession.sessionRef}</Descriptions.Item>
            <Descriptions.Item label="更新时间">{detail.hostSession.updatedAt}</Descriptions.Item>
            <Descriptions.Item label="记录引用">
              {detail.hostSession.transcriptRef}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      ) : null}

      {detail.mode === 'ralph' && detail.ralphLoop ? (
        <Card title="Ralph 验证闭环观察" style={{ marginTop: 16 }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Descriptions column={2}>
              <Descriptions.Item label="轮次">{detail.ralphLoop.roundCount}</Descriptions.Item>
              <Descriptions.Item label="连续失败计数">
                {detail.ralphLoop.failureStreak}
              </Descriptions.Item>
              <Descriptions.Item label="下一动作">
                {detail.ralphLoop.nextAction}
              </Descriptions.Item>
              <Descriptions.Item label="当前阻塞事项">
                {detail.ralphLoop.blocker}
              </Descriptions.Item>
            </Descriptions>
            <Card size="small" title="最近结果">
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
