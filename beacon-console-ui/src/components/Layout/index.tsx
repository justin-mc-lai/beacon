import { Layout as AntLayout, Button, Space, Tag } from 'antd';
import { Link, Outlet, useLocation } from 'react-router-dom';

import { ROUTES } from '../../constants/routes';
import './index.css';

const { Header, Content } = AntLayout;

export function Layout() {
  const location = useLocation();
  const inProjectFlow = location.pathname.startsWith('/project/');

  return (
    <AntLayout className="layout">
      <Header className="layout-header">
        <div className="layout-brand">
          <div>
            <div className="layout-logo">Beacon Console</div>
            <div className="layout-subtitle">lifecycle-first management board</div>
          </div>
          <Tag color="blue">v1.3.6</Tag>
        </div>
        <Space wrap>
          <Button type={location.pathname === ROUTES.HOME ? 'primary' : 'default'}>
            <Link to={ROUTES.HOME}>首页</Link>
          </Button>
          <Button type={location.pathname === ROUTES.MANAGEMENT ? 'primary' : 'default'}>
            <Link to={ROUTES.MANAGEMENT}>管理总览</Link>
          </Button>
          <Tag color={inProjectFlow ? 'gold' : 'default'}>
            {inProjectFlow ? 'Project Flow' : 'Portfolio Flow'}
          </Tag>
          <Tag color="cyan">Beacon only</Tag>
        </Space>
      </Header>
      <Content className="layout-content">
        <div className="layout-shell">
          <Outlet />
        </div>
      </Content>
    </AntLayout>
  );
}
