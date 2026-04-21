import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { Alert, Button } from 'antd';
import './index.css';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(_error: Error): Partial<State> {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({
      error,
      errorInfo,
    });

    // Log error to console in development
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <Alert
            message="应用出错"
            description={
              <div>
                <p>抱歉，应用遇到了一个错误。</p>
                {import.meta.env.DEV && this.state.error && (
                  <details style={{ marginTop: 16 }}>
                    <summary>错误详情</summary>
                    <pre style={{ marginTop: 8, fontSize: 12 }}>
                      {this.state.error.toString()}
                      {this.state.errorInfo?.componentStack}
                    </pre>
                  </details>
                )}
              </div>
            }
            type="error"
            showIcon
            action={
              <Button size="small" onClick={this.handleReset}>
                重新加载
              </Button>
            }
          />
        </div>
      );
    }

    return this.props.children;
  }
}
