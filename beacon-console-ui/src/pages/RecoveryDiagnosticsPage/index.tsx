import { Alert, Breadcrumb, Card, List, Space, Tag, Typography } from 'antd';
import { Navigate, useParams } from 'react-router-dom';

import { PageTraceCard } from '../../components/PageTrace';
import { ROUTES } from '../../constants/routes';
import { getPageTrace, getProjectById } from '../../data/consoleData';

export function RecoveryDiagnosticsPage() {
  const { id } = useParams();
  const project = getProjectById(id);
  const pageTrace = getPageTrace('recovery-diagnostics');

  if (!project) {
    return <Navigate to={ROUTES.MANAGEMENT} replace />;
  }

  return (
    <div className="console-page">
      <Breadcrumb style={{ marginBottom: 16 }}>
        <Breadcrumb.Item href="/">首页</Breadcrumb.Item>
        <Breadcrumb.Item href={ROUTES.MANAGEMENT}>管理总览</Breadcrumb.Item>
        <Breadcrumb.Item href={`/project/${project.id}`}>{project.name}</Breadcrumb.Item>
        <Breadcrumb.Item>恢复诊断</Breadcrumb.Item>
      </Breadcrumb>

      <Alert
        type="warning"
        showIcon
        message="正式真相仍来自 docs/beacon 与 .beacon"
        description="PocketBase / SQLite / runtime projection 只提供读模型。当前页面只解释 degraded / rebuild / doctor，不替代 requirement truth。"
      />

      <div className="console-grid console-grid--primary" style={{ marginTop: 16 }}>
        <Card
          title="诊断状态"
          extra={<Tag color={project.recovery.status === 'healthy-warning' ? 'blue' : 'gold'}>{project.recovery.status}</Tag>}
        >
          <List
            dataSource={project.recovery.truthSources}
            renderItem={(item) => <List.Item>{item}</List.Item>}
          />
        </Card>
        <Card title="恢复步骤">
          <List
            dataSource={project.recovery.steps}
            renderItem={(item) => <List.Item>{item}</List.Item>}
          />
        </Card>
      </div>

      <Card title="问题列表" style={{ marginTop: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          {project.recovery.issues.map((issue) => (
            <Card
              key={issue.title}
              size="small"
              title={issue.title}
              extra={<Tag color={issue.severity === 'critical' ? 'red' : issue.severity === 'warning' ? 'gold' : 'blue'}>{issue.severity}</Tag>}
            >
              <Typography.Paragraph>{issue.detail}</Typography.Paragraph>
              <Typography.Text className="console-muted">
                建议：{issue.recommendation}
              </Typography.Text>
            </Card>
          ))}
        </Space>
      </Card>

      <Card title="风险提示" style={{ marginTop: 16 }}>
        <List
          dataSource={project.recovery.riskNotes}
          renderItem={(item) => <List.Item>{item}</List.Item>}
        />
      </Card>

      <div style={{ marginTop: 16 }}>
        <PageTraceCard trace={pageTrace} />
      </div>
    </div>
  );
}
