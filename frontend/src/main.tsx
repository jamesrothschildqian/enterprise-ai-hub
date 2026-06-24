import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import enUS from 'antd/locale/en_US';
import App from './App';
import { useLocaleStore } from './store/localeStore';

const antdLocales: Record<string, any> = { zh: zhCN, en: enUS };

function Root() {
  const locale = useLocaleStore((s) => s.locale);
  return (
    <React.StrictMode>
      <ConfigProvider locale={antdLocales[locale] || enUS}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </ConfigProvider>
    </React.StrictMode>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(<Root />);
