import { Breadcrumb, Button, Card, Descriptions, Empty, List, Space, Tag, Typography } from 'antd';
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { PageTraceCard } from '../../components/PageTrace';
import {
  ROUTES,
  buildMaterialDocumentDetailRoute,
  buildMaterialViewerRoute,
  buildProjectDetailRoute,
} from '../../constants/routes';
import {
  getPageTrace,
  getProjectById,
} from '../../data/consoleData';
import { getMaterialById, getRelatedMaterials } from '../../data/materialCatalog';
import { getMaterialTypeLabel } from '../../utils/labels';

export function MaterialDocumentDetailPage() {
  const navigate = useNavigate();
  const { id, materialId } = useParams();
  const project = getProjectById(id);
  const material = getMaterialById(id, materialId);
  const relatedDocuments = getRelatedMaterials(id, materialId);
  const pageTrace = getPageTrace('material-document-detail');

  if (!project || !material) {
    return <Navigate to={buildMaterialViewerRoute(id ?? '')} replace />;
  }

  return (
    <div className="console-page">
      <Breadcrumb style={{ marginBottom: 16 }}>
        <Breadcrumb.Item>
          <Link to={ROUTES.HOME}>首页</Link>
        </Breadcrumb.Item>
        <Breadcrumb.Item>
          <Link to={ROUTES.MANAGEMENT}>管理总览</Link>
        </Breadcrumb.Item>
        <Breadcrumb.Item>
          <Link to={buildProjectDetailRoute(project.id)}>{project.name}</Link>
        </Breadcrumb.Item>
        <Breadcrumb.Item>
          <Link to={buildMaterialViewerRoute(project.id)}>项目文档目录</Link>
        </Breadcrumb.Item>
        <Breadcrumb.Item>{material.title}</Breadcrumb.Item>
      </Breadcrumb>

      <Card
        title={material.title}
        extra={
          <Space wrap>
            <Tag color="blue">{material.version}</Tag>
            <Tag>{getMaterialTypeLabel(material.type)}</Tag>
            <Button onClick={() => navigate(buildMaterialViewerRoute(project.id))}>返回目录</Button>
          </Space>
        }
      >
        <Descriptions column={2} size="small" bordered>
          <Descriptions.Item label="项目">{project.name}</Descriptions.Item>
          <Descriptions.Item label="主题">{material.feature}</Descriptions.Item>
          <Descriptions.Item label="更新时间">{material.updatedAt}</Descriptions.Item>
          <Descriptions.Item label="来源路径">
            <code>{material.path}</code>
          </Descriptions.Item>
        </Descriptions>

        <Typography.Paragraph className="console-muted" style={{ marginTop: 16 }}>
          {material.summary}
        </Typography.Paragraph>

        <div className="markdown-surface" style={{ marginTop: 16 }}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{material.content}</ReactMarkdown>
        </div>
      </Card>

      <div className="console-grid" style={{ marginTop: 16 }}>
        <Card title="关联文档">
          {relatedDocuments.length === 0 ? (
            <Empty description="当前文档暂无更多关联材料。" />
          ) : (
            <List
              dataSource={relatedDocuments}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <Typography.Link
                      key={item.id}
                      onClick={() =>
                        navigate(buildMaterialDocumentDetailRoute(project.id, item.id))
                      }
                    >
                      切换查看
                    </Typography.Link>,
                  ]}
                >
                  <List.Item.Meta
                    title={item.title}
                    description={`${item.version} · ${getMaterialTypeLabel(item.type)}`}
                  />
                </List.Item>
              )}
            />
          )}
        </Card>
        <Card title="阅读约束">
          <Space direction="vertical">
            <Typography.Text>当前页面只读，不在页面内直接编辑文档。</Typography.Text>
            <Typography.Text>文档目录、版本、主题与来源路径必须完整保留。</Typography.Text>
            <Typography.Text>正式真相仍以 Beacon 仓内归档材料为准。</Typography.Text>
          </Space>
        </Card>
      </div>

      <div style={{ marginTop: 16 }}>
        <PageTraceCard trace={pageTrace} />
      </div>
    </div>
  );
}
