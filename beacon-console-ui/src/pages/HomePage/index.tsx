import { Button, Card, Col, List, Row, Space, Statistic, Table, Tag, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';

import { HealthTag } from '../../components/HealthTag';
import { PageTraceCard } from '../../components/PageTrace';
import {
  ROUTES,
  buildProjectDetailRoute,
  buildRuntimeCenterRoute,
} from '../../constants/routes';
import { getPageTrace, getPortfolioSummary, getProjects } from '../../data/consoleData';
import type { Project } from '../../types/project';
import { getLifecycleLabel, getProjectKindLabel } from '../../utils/labels';

const interventionColumns: ColumnsType<Project> = [
  {
    title: '项目',
    dataIndex: 'name',
    key: 'name',
    render: (_, project) => <strong>{project.name}</strong>,
  },
  {
    title: '版本',
    dataIndex: 'currentVersion',
    key: 'currentVersion',
  },
  {
    title: '阶段',
    dataIndex: 'lifecycle',
    key: 'lifecycle',
    render: (value) => getLifecycleLabel(value),
  },
  {
    title: '当前交付',
    dataIndex: 'currentDelivery',
    key: 'currentDelivery',
  },
  {
    title: 'Blocker',
    dataIndex: 'blocker',
    key: 'blocker',
  },
  {
    title: '下一步',
    dataIndex: 'nextStep',
    key: 'nextStep',
  },
];

export function HomePage() {
  const navigate = useNavigate();
  const summary = getPortfolioSummary();
  const projects = getProjects();
  const interventionProjects = projects.filter(
    (project) => project.healthStatus !== 'healthy' || project.lifecycle !== 'release',
  );
  const featuredProject = projects.find((project) => project.id === 'beacon') ?? projects[0];
  const pageTrace = getPageTrace('home');

  return (
    <div className="console-page">
      <div className="console-hero">
        <div>
          <Tag color="cyan">CEO / Owner View</Tag>
          <Typography.Title level={1}>先回答经营判断，再决定是否下钻</Typography.Title>
          <Typography.Paragraph className="console-muted">
            首页默认只给项目组合、阻塞点、当前交付与下一步，不展示 tmux pane、raw event、
            transcript 或宿主交互洪流。
          </Typography.Paragraph>
        </div>
        <Space wrap>
          <Button type="primary" onClick={() => navigate(ROUTES.MANAGEMENT)}>
            查看管理总览
          </Button>
          <Button onClick={() => navigate(buildProjectDetailRoute(featuredProject.id))}>
            进入重点项目
          </Button>
        </Space>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card className="stat-card">
            <Statistic title="活跃项目" value={summary.totalProjects} />
          </Card>
        </Col>
        <Col span={6}>
          <Card className="stat-card">
            <Statistic
              title="阻塞项目"
              value={summary.blockedProjects}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card className="stat-card">
            <Statistic title="活跃 Runtime" value={summary.activeRuntimeCount} />
          </Card>
        </Col>
        <Col span={6}>
          <Card className="stat-card">
            <Statistic title="今日交付" value={summary.deliveredToday} />
          </Card>
        </Col>
      </Row>

      <div className="console-grid console-grid--primary">
        <Card
          title="重点介入区"
          extra={<Tag color="gold">{summary.interventionCount} 个待介入</Tag>}
        >
          <List
            dataSource={interventionProjects.slice(0, 3)}
            renderItem={(project) => (
              <List.Item
                actions={[
                  <Button
                    key={`${project.id}-detail`}
                    type="link"
                    onClick={() => navigate(buildProjectDetailRoute(project.id))}
                  >
                    项目详情
                  </Button>,
                ]}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <strong>{project.name}</strong>
                      <HealthTag status={project.healthStatus} />
                    </Space>
                  }
                  description={`${project.interventionReason} 当前建议：${project.nextStep}`}
                />
              </List.Item>
            )}
          />
        </Card>

        <Card title="重点项目摘要">
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <div>
              <Typography.Title level={3}>{featuredProject.name}</Typography.Title>
              <Typography.Paragraph className="console-muted">
                {featuredProject.currentDelivery}
              </Typography.Paragraph>
            </div>
            <Space wrap>
              <Tag>{getProjectKindLabel(featuredProject.kind)}</Tag>
              <Tag color="blue">{featuredProject.currentVersion}</Tag>
              <Tag color="purple">{getLifecycleLabel(featuredProject.lifecycle)}</Tag>
              <HealthTag status={featuredProject.healthStatus} />
            </Space>
            <div className="summary-list">
              <div>
                <span>主 Feature</span>
                <strong>{featuredProject.currentFeature}</strong>
              </div>
              <div>
                <span>Blocker</span>
                <strong>{featuredProject.blocker}</strong>
              </div>
              <div>
                <span>Runtime 摘要</span>
                <strong>{featuredProject.runtimeSummary.summary}</strong>
              </div>
            </div>
            <Space wrap>
              <Button type="primary" onClick={() => navigate(buildProjectDetailRoute(featuredProject.id))}>
                继续接力
              </Button>
              <Button onClick={() => navigate(buildRuntimeCenterRoute(featuredProject.id))}>
                查看 Runtime 中心
              </Button>
            </Space>
          </Space>
        </Card>
      </div>

      <Card title="项目推进摘要" style={{ marginTop: 16 }}>
        <Table
          rowKey="id"
          pagination={false}
          columns={interventionColumns}
          dataSource={interventionProjects}
          size="small"
        />
      </Card>

      <div className="console-grid" style={{ marginTop: 16 }}>
        <Card title="当前交付">
          <List
            dataSource={projects.flatMap((project) =>
              project.latestDelivery.slice(0, 1).map((item) => `${project.name}: ${item}`),
            )}
            renderItem={(item) => <List.Item>{item}</List.Item>}
          />
        </Card>
        <Card title="下一步建议">
          <List
            dataSource={[
              '先处理 Beacon 本身的 implement / QA evidence，解除 release gate。',
              '对 blocked 的 shopxo_canada 先稳定回归环境，再让 Ralph 完成闭环。',
              '对 slow_uni_bmtop 执行最后的 release sign-off，完成真实项目线验收。',
            ]}
            renderItem={(item) => <List.Item>{item}</List.Item>}
          />
        </Card>
      </div>

      <div style={{ marginTop: 16 }}>
        <PageTraceCard trace={pageTrace} />
      </div>
    </div>
  );
}
