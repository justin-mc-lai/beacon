import { useEffect, useState } from 'react';
import {
  Alert,
  Breadcrumb,
  Button,
  Card,
  Col,
  Descriptions,
  Empty,
  Input,
  List,
  Row,
  Select,
  Space,
  Tag,
  Tree,
  Typography,
} from 'antd';
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { PageTraceCard } from '../../components/PageTrace';
import { ROUTES, buildMaterialDocumentDetailRoute, buildProjectDetailRoute } from '../../constants/routes';
import { getPageTrace, getProjectById } from '../../data/consoleData';
import { getMaterialById, getProjectMaterials } from '../../data/materialCatalog';
import type { MaterialDocument } from '../../types/project';
import { getMaterialTypeLabel } from '../../utils/labels';

export function MaterialViewerPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const project = getProjectById(id);
  const pageTrace = getPageTrace('material-viewer');
  const materials = getProjectMaterials(id);
  const [selectedMaterialId, setSelectedMaterialId] = useState<string | undefined>(materials[0]?.id);
  const [query, setQuery] = useState('');
  const [versionFilter, setVersionFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');

  const filteredMaterials = materials.filter((material) => {
    const matchesQuery =
      query.length === 0
      || material.title.toLowerCase().includes(query.toLowerCase())
      || material.feature.toLowerCase().includes(query.toLowerCase())
      || material.path.toLowerCase().includes(query.toLowerCase());
    const matchesVersion = versionFilter === 'all' || material.version === versionFilter;
    const matchesType = typeFilter === 'all' || material.type === typeFilter;
    return matchesQuery && matchesVersion && matchesType;
  });

  useEffect(() => {
    if (filteredMaterials.length === 0) {
      setSelectedMaterialId(undefined);
      return;
    }
    const nextSelection = filteredMaterials.find((material) => material.id === selectedMaterialId);
    if (!nextSelection) {
      setSelectedMaterialId(filteredMaterials[0]?.id);
    }
  }, [filteredMaterials, selectedMaterialId]);

  if (!project) {
    return <Navigate to={ROUTES.MANAGEMENT} replace />;
  }

  const selectedMaterial = getMaterialById(id, selectedMaterialId) ?? filteredMaterials[0];
  const versions = Array.from(new Set(materials.map((material) => material.version)));
  const types = Array.from(new Set(materials.map((material) => material.type)));
  const treeData = buildMaterialTree(filteredMaterials);

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
        <Breadcrumb.Item>项目文档目录</Breadcrumb.Item>
      </Breadcrumb>

      <div className="console-hero">
        <div>
          <Tag color="cyan">Beacon 受管文档</Tag>
          <Typography.Title level={2} style={{ marginBottom: 8 }}>
            {project.name} 项目文档目录
          </Typography.Title>
          <Typography.Paragraph className="console-muted">
            这里展示 Beacon 仓内受管的真实项目文档材料。文档按版本、材料类型与主题归档，
            仅用于浏览、核对与回链，不在页面内直接编辑。
          </Typography.Paragraph>
        </div>
        <div className="console-kpi-strip">
          <div className="console-kpi">
            <span>文档总数</span>
            <strong>{materials.length}</strong>
          </div>
          <div className="console-kpi">
            <span>版本数</span>
            <strong>{versions.length}</strong>
          </div>
          <div className="console-kpi">
            <span>材料类型</span>
            <strong>{types.length}</strong>
          </div>
        </div>
      </div>

      <Alert
        type="info"
        showIcon
        message="受管材料来源"
        description="当前页面优先读取 Beacon 仓内对真实项目的正式文档材料与发布证据，不直接读取外部项目仓的自由文档树。"
      />

      <Card title="筛选条件" style={{ marginTop: 16 }}>
        <div className="console-toolbar">
          <Input.Search
            allowClear
            placeholder="搜索标题、主题或来源路径"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <Select
            value={versionFilter}
            onChange={setVersionFilter}
            options={[
              { label: '全部版本', value: 'all' },
              ...versions.map((version) => ({ label: version, value: version })),
            ]}
          />
          <Select
            value={typeFilter}
            onChange={setTypeFilter}
            options={[
              { label: '全部材料类型', value: 'all' },
              ...types.map((type) => ({ label: getMaterialTypeLabel(type), value: type })),
            ]}
          />
        </div>
      </Card>

      {filteredMaterials.length === 0 ? (
        <Card style={{ marginTop: 16 }}>
          <Empty
            description="当前筛选条件下未找到受管文档材料。请调整筛选条件，或检查 Beacon 仓内是否已归档该项目的正式材料。"
          />
        </Card>
      ) : (
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} xl={8}>
            <Card title="文档目录树" className="console-panel--full">
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

            <Card title="当前结果" style={{ marginTop: 16 }}>
              <List
                size="small"
                dataSource={filteredMaterials}
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
                      title={material.title}
                      description={`${material.version} · ${getMaterialTypeLabel(material.type)}`}
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>

          <Col xs={24} xl={16}>
            <Card
              title={selectedMaterial?.title ?? '未选择文档'}
              className="console-panel--full"
              extra={
                selectedMaterial ? (
                  <Button
                    type="primary"
                    onClick={() =>
                      navigate(buildMaterialDocumentDetailRoute(project.id, selectedMaterial.id))
                    }
                  >
                    查看文档详情
                  </Button>
                ) : null
              }
            >
              {selectedMaterial ? (
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  <Descriptions column={2} size="small" bordered>
                    <Descriptions.Item label="项目">{project.name}</Descriptions.Item>
                    <Descriptions.Item label="当前版本">{selectedMaterial.version}</Descriptions.Item>
                    <Descriptions.Item label="材料类型">
                      {getMaterialTypeLabel(selectedMaterial.type)}
                    </Descriptions.Item>
                    <Descriptions.Item label="主题">{selectedMaterial.feature}</Descriptions.Item>
                    <Descriptions.Item label="来源路径" span={2}>
                      <code>{selectedMaterial.path}</code>
                    </Descriptions.Item>
                  </Descriptions>
                  <Typography.Paragraph className="console-muted">
                    {selectedMaterial.summary}
                  </Typography.Paragraph>
                  <div className="markdown-surface">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {selectedMaterial.content}
                    </ReactMarkdown>
                  </div>
                </Space>
              ) : (
                <Empty description="请选择左侧文档材料以查看内容。" />
              )}
            </Card>
          </Col>
        </Row>
      )}

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
