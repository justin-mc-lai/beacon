import { Breadcrumb, Card, Descriptions, List, Space, Tag, Typography } from 'antd';
import { Navigate, useNavigate, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { PageTraceCard } from '../../components/PageTrace';
import { ROUTES, buildMaterialDocumentDetailRoute, buildMaterialViewerRoute } from '../../constants/routes';
import { getMaterialById, getPageTrace, getProjectById, getProjectMaterials } from '../../data/consoleData';
import { getMaterialTypeLabel } from '../../utils/labels';

export function MaterialDocumentDetailPage() {
  const navigate = useNavigate();
  const { id, materialId } = useParams();
  const project = getProjectById(id);
  const material = getMaterialById(id, materialId);
  const pageTrace = getPageTrace('material-document-detail');

  if (!project || !material) {
    return <Navigate to={buildMaterialViewerRoute(id ?? '')} replace />;
  }

  const relatedDocuments = getProjectMaterials(id).filter((item) =>
    material.relatedIds.includes(item.id),
  );

  return (
    <div className="console-page">
      <Breadcrumb style={{ marginBottom: 16 }}>
        <Breadcrumb.Item href="/">首页</Breadcrumb.Item>
        <Breadcrumb.Item href={ROUTES.MANAGEMENT}>管理总览</Breadcrumb.Item>
        <Breadcrumb.Item href={`/project/${project.id}`}>{project.name}</Breadcrumb.Item>
        <Breadcrumb.Item href={buildMaterialViewerRoute(project.id)}>项目物料</Breadcrumb.Item>
        <Breadcrumb.Item>{material.title}</Breadcrumb.Item>
      </Breadcrumb>

      <Card title={material.title} extra={<Tag color="blue">只读</Tag>}>
        <Descriptions column={2} size="small">
          <Descriptions.Item label="版本">{material.version}</Descriptions.Item>
          <Descriptions.Item label="文档类型">
            {getMaterialTypeLabel(material.type)}
          </Descriptions.Item>
          <Descriptions.Item label="Feature">{material.feature}</Descriptions.Item>
          <Descriptions.Item label="更新时间">{material.updatedAt}</Descriptions.Item>
          <Descriptions.Item label="来源路径" span={2}>
            <code>{material.path}</code>
          </Descriptions.Item>
        </Descriptions>
        <div className="markdown-surface" style={{ marginTop: 16 }}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{material.content}</ReactMarkdown>
        </div>
      </Card>

      <div className="console-grid" style={{ marginTop: 16 }}>
        <Card title="同类 / 关联文档">
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
                    切换
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
        </Card>
        <Card title="阅读约束">
          <Space direction="vertical">
            <Typography.Text>当前页面只读，不提供网页内编辑。</Typography.Text>
            <Typography.Text>版本、类型与 feature 上下文始终保留。</Typography.Text>
            <Typography.Text>来源路径用于回链正式真相，不替代本地文档树。</Typography.Text>
          </Space>
        </Card>
      </div>

      <div style={{ marginTop: 16 }}>
        <PageTraceCard trace={pageTrace} />
      </div>
    </div>
  );
}
