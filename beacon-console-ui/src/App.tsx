import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';

import { ErrorBoundary } from './components/ErrorBoundary';
import { AppRouter } from './router';

function App() {
  return (
    <ErrorBoundary>
      <ConfigProvider locale={zhCN}>
        <AppRouter />
      </ConfigProvider>
    </ErrorBoundary>
  );
}

export default App;
