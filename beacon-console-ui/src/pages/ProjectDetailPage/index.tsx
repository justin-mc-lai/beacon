import {
  Breadcrumb,
  Button,
  Card,
  Col,
  Descriptions,
  List,
  Progress,
  Row,
  Space,
  Steps,
  Tag,
  Typography,
} from 'antd';
import { Navigate, useNavigate, useParams } from 'react-router-dom';

import { HealthTag } from '../../components/HealthTag';
import { PageTraceCard } from '../../components/PageTrace';
import {
  ROUTES,
  buildMaterialViewerRoute,
  buildRecoveryDiagnosticsRoute,
  buildRuntimeCenterRoute,
} from '../../constants/routes';
import { getPageTrace, getProjectById } from '../../data/consoleData';
import { getDebugLabel, getDebugTone, getLifecycleLabel, getRequirementLabel, getRequirementTone } from '../../utils/labels';

const lifecycleOrder = ['prd', 'user-story', 'test-case', 'prototype', 'implement', 'qa', 'release'];

export function ProjectDetailPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const project = getProjectById(id);
  const pageTrace = getPageTrace('project-detail');

  if (!project) {
    return <Navigate to={ROUTES.MANAGEMENT} replace />;
  }

  const stepItems = lifecycleOrder.map((stage) => ({
    title: getLifecycleLabel(stage as typeof project.lifecycle),
  }));

  return (
    <div className="console-page">
      <Breadcrumb style={{ marginBottom: 16 }}>
        <Breadcrumb.Item href="/">首页</Breadcrumb.Item>
        <Breadcrumb.Item href={ROUTES.MANAGEMENT}>管理总览</Breadcrumb.Item>
        <Breadcrumb.Item>{project.name}</Breadcrumb.Item>
      </Breadcrumb>

      <Card
        title={
          <Space wrap>
            <Typography.Title level={2} style={{ margin: 0 }}>
              {project.name}
            </Typography.Title>
            <Tag color="blue">{project.currentVersion}</Tag>
            <HealthTag status={project.healthStatus} />
            <Tag color={getDebugTone(project.debugState)}>{getDebugLabel(project.debugState)}</Tag>
          </Space>
        }
        extra={
          <Space wrap>
            <Button onClick={() => navigate(buildRuntimeCenterRoute(project.id))}>运行中心</Button>
            <Button onClick={() => navigate(buildRecoveryDiagnosticsRoute(project.id))}>
              恢复诊断
            </Button>
            <Button type="primary" onClick={() => navigate(buildMaterialViewerRoute(project.id))}>
              项目物料
            </Button>
          </Space>
        }
      >
        <Row gutter={[16, 16]}>
          <Col span={14}>
            <Descriptions column={2} size="small">
              <Descriptions.Item label="项目类型">{project.kind}</Descriptions.Item>
              <Descriptions.Item label="Owner">{project.owner}</Descriptions.Item>
              <Descriptions.Item label="当前阶段">
                {getLifecycleLabel(project.lifecycle)}
              </Descriptions.Item>
              <Descriptions.Item label="推荐 Skill">{project.recommendedSkill}</Descriptions.Item>
              <Descriptions.Item label="工作目录" span={2}>
                <code>{project.rootPath}</code>
              </Descriptions.Item>
              <Descriptions.Item label="Blocker" span={2}>
                {project.blocker}
              </Descriptions.Item>
            </Descriptions>
          </Col>
          <Col span={10}>
            <Card size="small" title="版本 / Git / Worktree">
              <div className="summary-list">
                <div>
                  <span>当前分支</span>
                  <strong>{project.gitStatus.branch}</strong>
                </div>
                <div>
                  <span>目标分支</span>
                  <strong>{project.gitStatus.expectedBranch ?? 'n/a'}</strong>
                </div>
                <div>
                  <span>Worktree</span>
                  <strong>{project.gitStatus.dirty ? 'dirty' : 'clean'}</strong>
                </div>
              </div>
            </Card>
          </Col>
        </Row>
      </Card>

      <div className="console-grid console-grid--primary" style={{ marginTop: 16 }}>
        <Card title="版本线与当前状态">
          <Space wrap style={{ marginBottom: 16 }}>
            {project.versionLine.map((version) => (
              <Tag key={version} color={version === project.currentVersion ? 'blue' : 'default'}>
                {version}
              </Tag>
            ))}
          </Space>
          <Steps
            current={lifecycleOrder.indexOf(project.lifecycle)}
            items={stepItems}
            responsive
            size="small"
          />
          <div style={{ marginTop: 16 }}>
            <Progress percent={project.progress} />
          </div>
        </Card>

        <Card title="运行态摘要">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Tag color="purple">{project.runtimeSummary.activeMode.toUpperCase()}</Tag>
            <Typography.Paragraph>{project.runtimeSummary.summary}</Typography.Paragraph>
            <div className="summary-list">
              <div>
                <span>活跃运行数</span>
                <strong>{project.runtimeSummary.activeRuns}</strong>
              </div>
              <div>
                <span>Linked run</span>
                <strong>{project.runtimeSummary.linkedRun}</strong>
              </div>
            </div>
            <Typography.Text className="console-muted">
              首页与详情页只展示摘要，Team / Ralph 明细统一下钻到运行中心。
            </Typography.Text>
          </Space>
        </Card>
      </div>

      <div className="console-grid" style={{ marginTop: 16 }}>
        <Card title="主 PRD / 主线 Feature">
          <List
            dataSource={project.mainTracks}
            renderItem={(track) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <Space wrap>
                      <strong>{track.title}</strong>
                      <Tag color="blue">{getLifecycleLabel(track.stage)}</Tag>
                    </Space>
                  }
                  description={`${track.summary} · ${track.sourcePath}`}
                />
              </List.Item>
            )}
          />
        </Card>
        <Card title="并行 PRD / 子线">
          <List
            locale={{ emptyText: '当前没有并行 PRD。' }}
            dataSource={project.parallelTracks}
            renderItem={(track) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <Space wrap>
                      <strong>{track.title}</strong>
                      <Tag>{getLifecycleLabel(track.stage)}</Tag>
                    </Space>
                  }
                  description={`${track.summary} · ${track.sourcePath}`}
                />
              </List.Item>
            )}
          />
        </Card>
      </div>

      <Card title="需求闭环状态" style={{ marginTop: 16 }}>
        <Space wrap>
          <Tag color={getRequirementTone(project.requirementClosure.prd)}>
            PRD {getRequirementLabel(project.requirementClosure.prd)}
          </Tag>
          <Tag color={getRequirementTone(project.requirementClosure.userStory)}>
            User Story {getRequirementLabel(project.requirementClosure.userStory)}
          </Tag>
          <Tag color={getRequirementTone(project.requirementClosure.testCase)}>
            Test Case {getRequirementLabel(project.requirementClosure.testCase)}
          </Tag>
          <Tag color={getRequirementTone(project.requirementClosure.prototype)}>
            Prototype {getRequirementLabel(project.requirementClosure.prototype)}
          </Tag>
          <Tag color={getRequirementTone(project.requirementClosure.implement)}>
            Implement {getRequirementLabel(project.requirementClosure.implement)}
          </Tag>
          <Tag color={getRequirementTone(project.requirementClosure.qa)}>
            QA {getRequirementLabel(project.requirementClosure.qa)}
          </Tag>
          <Tag color={getRequirementTone(project.requirementClosure.release)}>
            Release {getRequirementLabel(project.requirementClosure.release)}
          </Tag>
        </Space>
      </Card>

      <div className="console-grid" style={{ marginTop: 16 }}>
        <Card title="最近交付摘要">
          <List
            dataSource={project.latestDelivery}
            renderItem={(item) => <List.Item>{item}</List.Item>}
          />
        </Card>
        <Card title="推荐动作">
          <List
            dataSource={[
              project.nextStep,
              `推荐 skill：${project.recommendedSkill}`,
              `介入原因：${project.interventionReason}`,
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
