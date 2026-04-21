import { useEffect, useState } from 'react';
import {
  Alert,
  Breadcrumb,
  Button,
  Card,
  Col,
  List,
  Row,
  Space,
  Tag,
  Tree,
  Typography,
} from 'antd';
import { Navigate, useNavigate, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { PageTraceCard } from '../../components/PageTrace';
import { ROUTES, buildMaterialDocumentDetailRoute } from '../../constants/routes';
import { getMaterialById, getPageTrace, getProjectById, getProjectMaterials } from '../../data/consoleData';
import type { MaterialDocument } from '../../types/project';
import { getMaterialTypeLabel } from '../../utils/labels';

export function MaterialViewerPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const project = getProjectById(id);
  const pageTrace = getPageTrace('material-viewer');
  const materials = getProjectMaterials(id);
  const [selectedMaterialId, setSelectedMaterialId] = useState<string | undefined>(
    materials[0]?.id,
  );

  useEffect(() => {
    setSelectedMaterialId(materials[0]?.id);
  }, [id]);

  if (!project) {
    return <Navigate to={ROUTES.MANAGEMENT} replace />;
  }

  const selectedMaterial = getMaterialById(id, selectedMaterialId) ?? materials[0];

  const treeData = buildMaterialTree(materials);

  return (
    <div className="console-page">
      <Breadcrumb style={{ marginBottom: 16 }}>
        <Breadcrumb.Item href="/">首页</Breadcrumb.Item>
        <Breadcrumb.Item href={ROUTES.MANAGEMENT}>管理总览</Breadcrumb.Item>
        <Breadcrumb.Item href={`/project/${project.id}`}>{project.name}</Breadcrumb.Item>
        <Breadcrumb.Item>项目物料查看器</Breadcrumb.Item>
      </Breadcrumb>

      <Alert
        type="info"
        showIcon
        message="只读模式"
        description="文档按 version -> document type -> feature 组织，仅支持浏览与回链，不提供网页内编辑。"
      />

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={8}>
          <Card title="物料树">
            <Tree
              defaultExpandAll
              selectedKeys={selectedMaterial ? [selectedMaterial.id] : []}
              treeData={treeData}
              onSelect={(keys) => {
                const [firstKey] = keys;
                if (typeof firstKey === 'string' && getMaterialById(id, firstKey)) {
                  setSelectedMaterialId(firstKey);
                }
              }}
            />
          </Card>
        </Col>
        <Col span={16}>
          <Card
            title={selectedMaterial?.title ?? '暂无可读文档'}
            extra={
              selectedMaterial ? (
                <Button
                  type="primary"
                  onClick={() => navigate(buildMaterialDocumentDetailRoute(project.id, selectedMaterial.id))}
                >
                  打开详情
                </Button>
              ) : null
            }
          >
            {selectedMaterial ? (
              <Space direction="vertical" style={{ width: '100%' }}>
                <Space wrap>
                  <Tag color="blue">{selectedMaterial.version}</Tag>
                  <Tag>{getMaterialTypeLabel(selectedMaterial.type)}</Tag>
                  <Tag color="purple">{selectedMaterial.feature}</Tag>
                </Space>
                <Typography.Paragraph className="console-muted">
                  {selectedMaterial.summary}
                </Typography.Paragraph>
                <Typography.Text className="console-muted">
                  来源路径：<code>{selectedMaterial.path}</code>
                </Typography.Text>
                <div className="markdown-surface">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {selectedMaterial.content}
                  </ReactMarkdown>
                </div>
              </Space>
            ) : (
              <Typography.Text>当前版本暂无文档。</Typography.Text>
            )}
          </Card>
        </Col>
      </Row>

      <Card title="当前版本文档列表" style={{ marginTop: 16 }}>
        <List
          dataSource={materials}
          renderItem={(material) => (
            <List.Item
              actions={[
                <Button
                  key={material.id}
                  type="link"
                  onClick={() => setSelectedMaterialId(material.id)}
                >
                  预览
                </Button>,
              ]}
            >
              <List.Item.Meta
                title={`${material.version} · ${getMaterialTypeLabel(material.type)} · ${material.feature}`}
                description={material.path}
              />
            </List.Item>
          )}
        />
      </Card>

      <div style={{ marginTop: 16 }}>
        <PageTraceCard trace={pageTrace} />
      </div>
    </div>
  );
}

function buildMaterialTree(materials: MaterialDocument[]) {
  const versions = Array.from(new Set(materials.map((material) => material.version)));

  return versions.map((version) => {
    const versionMaterials = materials.filter((material) => material.version === version);
    const types = Array.from(new Set(versionMaterials.map((material) => material.type)));
    return {
      key: `version-${version}`,
      title: version,
      children: types.map((type) => {
        const typeMaterials = versionMaterials.filter((material) => material.type === type);
        const features = Array.from(new Set(typeMaterials.map((material) => material.feature)));
        return {
          key: `${version}-${type}`,
          title: getMaterialTypeLabel(type),
          children: features.map((feature) => ({
            key: `${version}-${type}-${feature}`,
            title: feature,
            children: typeMaterials
              .filter((material) => material.feature === feature)
              .map((material) => ({
                key: material.id,
                title: material.title,
                isLeaf: true,
              })),
          })),
        };
      }),
    };
  });
}
