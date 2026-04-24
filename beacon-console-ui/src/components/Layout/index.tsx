import { Layout as AntLayout, Space, Tag } from 'antd';
import { Link, Outlet, useLocation } from 'react-router-dom';

import { ROUTES } from '../../constants/routes';
import './index.css';

const { Header, Content } = AntLayout;

export function Layout() {
  const location = useLocation();
  const inProjectFlow = location.pathname.startsWith('/project/');
  const navItems = [
    { label: '首页', path: ROUTES.HOME },
    { label: '管理总览', path: ROUTES.MANAGEMENT },
  ];

  return (
    <AntLayout className="layout">
      <Header className="layout-header">
        <div className="layout-brand">
          <div>
            <div className="layout-logo">Beacon 管理控制台</div>
            <div className="layout-subtitle">Beacon 受管项目组合视图</div>
          </div>
          <Tag color="blue">v1.3.6</Tag>
        </div>
        <Space wrap className="layout-actions">
          <nav className="layout-nav" aria-label="Primary">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`layout-nav__link${isActive ? ' layout-nav__link--active' : ''}`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <Tag color={inProjectFlow ? 'gold' : 'default'}>
            {inProjectFlow ? '项目上下文' : '项目组合上下文'}
          </Tag>
          <Tag color="cyan">Beacon 受管</Tag>
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
