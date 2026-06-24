import { useEffect, useMemo, useCallback, useState } from 'react';
import { Outlet, useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { Layout, Menu, Select, Space, Tag, Typography, Spin, theme } from 'antd';
import {
  DashboardOutlined, FileTextOutlined, LineChartOutlined, RobotOutlined,
  SafetyOutlined, SearchOutlined, FileDoneOutlined, SwapOutlined,
} from '@ant-design/icons';
import { useIndustryStore } from '../store/industryStore';
import { useLocaleStore } from '../store/localeStore';
import DemoGuide from '../components/DemoGuide';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

const iconMap: Record<string, any> = {
  DashboardOutlined: <DashboardOutlined />,
  FileTextOutlined: <FileTextOutlined />,
  LineChartOutlined: <LineChartOutlined />,
  RobotOutlined: <RobotOutlined />,
  SafetyOutlined: <SafetyOutlined />,
  SearchOutlined: <SearchOutlined />,
  FileDoneOutlined: <FileDoneOutlined />,
};

const navItems = [
  { path: '/dashboard', key: 'nav.dashboard', icon: 'DashboardOutlined' },
  { path: '/doc-parser', key: 'nav.docParser', icon: 'FileTextOutlined' },
  { path: '/demand-forecast', key: 'nav.demandForecast', icon: 'LineChartOutlined' },
  { path: '/ai-agent', key: 'nav.aiAgent', icon: 'RobotOutlined' },
  { path: '/risk-control', key: 'nav.riskControl', icon: 'SafetyOutlined' },
  { path: '/chatbi', key: 'nav.chatBI', icon: 'SearchOutlined' },
  { path: '/report', key: 'nav.report', icon: 'FileDoneOutlined' },
];

export default function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const { industries, currentId, currentData, init, switchTo, loading } = useIndustryStore();
  const { t, locale, setLang } = useLocaleStore();
  const [collapsed, setCollapsed] = useState(false);
  const { token } = theme.useToken();

  useEffect(() => {
    const langParam = searchParams.get('lang');
    if (langParam) setLang(langParam);
    const industryParam = searchParams.get('industry');
    if (industryParam) switchTo(industryParam);
    init();
  }, []);

  const updateURL = useCallback((newIndustry?: string, newLang?: string) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (newIndustry) next.set('industry', newIndustry);
      if (newLang) next.set('lang', newLang);
      return next;
    }, { replace: true });
  }, [setSearchParams]);

  const currentIndustry = useMemo(
    () => industries.find(i => i.id === currentId),
    [industries, currentId],
  );

  const menuItems = useMemo(() =>
    navItems.map(n => ({
      key: n.path,
      icon: iconMap[n.icon],
      label: t(n.key),
    })),
    [t, locale],
  );

  const handleMenuClick = useCallback((info: { key: string }) => {
    navigate(`${info.key}${location.search}`);
  }, [navigate, location.search]);

  const handleSwitchIndustry = useCallback((id: string) => {
    switchTo(id);
    updateURL(id, undefined);
  }, [switchTo, updateURL]);

  const handleLangChange = useCallback((newLang: string) => {
    setLang(newLang);
    updateURL(undefined, newLang);
  }, [setLang, updateURL]);

  const LANG_OPTIONS = [
    { value: 'zh', label: '中文' },
    { value: 'en', label: 'English' },
    { value: 'vi', label: 'Tiếng Việt' },
    { value: 'ms', label: 'Bahasa Melayu' },
  ];

  const selectedKeys = useMemo(() => [location.pathname], [location.pathname]);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="light"
        width={220}
        style={{
          borderRight: `1px solid ${token.colorBorderSecondary}`,
          boxShadow: '2px 0 8px rgba(0,0,0,0.04)',
        }}
      >
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: `1px solid ${token.colorBorderSecondary}`,
          fontWeight: 700,
          fontSize: collapsed ? 14 : 16,
          color: token.colorPrimary,
          padding: '0 16px',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
        }}>
          {collapsed ? 'AI' : t('app.title')}
        </div>
        <Menu
          mode="inline"
          selectedKeys={selectedKeys}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ borderInlineEnd: 'none' }}
        />
      </Sider>
      <Layout>
        <Header style={{
          padding: '0 24px',
          background: token.colorBgContainer,
          borderBottom: `1px solid ${token.colorBorderSecondary}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: 64,
        }}>
          <Space>
            <SwapOutlined style={{ fontSize: 18, color: token.colorPrimary }} />
            {loading && industries.length === 0 ? (
              <Spin size="small" />
            ) : (
              <Select
                value={currentId}
                onChange={handleSwitchIndustry}
                style={{ width: 200 }}
                options={industries.map(i => ({
                  value: i.id,
                  label: `${i.icon || '📋'} ${locale === 'zh' ? i.name : i.name_en}`,
                }))}
                placeholder={t('header.industry.placeholder')}
              />
            )}
            {currentIndustry && (
              <Tag color="blue">{currentIndustry.name_en}</Tag>
            )}
          </Space>
          <Space>
            {currentData && (
              <Text type="secondary" style={{ fontSize: 13 }}>
                {t('common.demoDataReady')}
              </Text>
            )}
            <Select
              value={locale}
              onChange={handleLangChange}
              size="small"
              style={{ width: 140 }}
              options={LANG_OPTIONS}
            />
          </Space>
        </Header>
        <Content style={{ margin: 0, padding: 24, background: '#f5f7fa', minHeight: 'calc(100vh - 64px)' }}>
          <Outlet />
        </Content>
      </Layout>
      <DemoGuide />
    </Layout>
  );
}
