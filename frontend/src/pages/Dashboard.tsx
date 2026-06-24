import { useEffect, useState } from 'react';
import { Row, Col, Card, Spin, Typography, Space } from 'antd';
import {
  FileTextOutlined, LineChartOutlined, RobotOutlined, SafetyOutlined,
  SearchOutlined, ArrowUpOutlined, ArrowDownOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useNavigate } from 'react-router-dom';
import { useIndustryStore } from '../store/industryStore';
import { useLocaleStore } from '../store/localeStore';
import { getDocTemplates, getForecastData, getRiskIndicators, getAICapabilities, getBITables } from '../services/api';

const { Title, Paragraph } = Typography;

const moduleEntries = [
  { key: 'doc-parser', icon: <FileTextOutlined style={{ fontSize: 28, color: '#1677ff' }} />, nameKey: 'dashboard.modules.docParser', color: '#e6f4ff' },
  { key: 'demand-forecast', icon: <LineChartOutlined style={{ fontSize: 28, color: '#52c41a' }} />, nameKey: 'dashboard.modules.demandForecast', color: '#f6ffed' },
  { key: 'ai-agent', icon: <RobotOutlined style={{ fontSize: 28, color: '#722ed1' }} />, nameKey: 'dashboard.modules.aiAgent', color: '#f9f0ff' },
  { key: 'risk-control', icon: <SafetyOutlined style={{ fontSize: 28, color: '#fa8c16' }} />, nameKey: 'dashboard.modules.riskControl', color: '#fff7e6' },
  { key: 'chatbi', icon: <SearchOutlined style={{ fontSize: 28, color: '#13c2c2' }} />, nameKey: 'dashboard.modules.chatBI', color: '#e6fffb' },
];

export default function Dashboard() {
  const navigate = useNavigate();
  const { currentData, currentId } = useIndustryStore();
  const { t, locale, isZh } = useLocaleStore();
  const [kpis, setKpis] = useState({ docs: 0, forecast: 0, risks: 0, chats: 0, bi: 0 });
  const [chartData, setChartData] = useState<any>(null);
  const [riskChart, setRiskChart] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getDocTemplates().catch(() => ({ templates: [] })),
      getForecastData().catch(() => ({})),
      getRiskIndicators().catch(() => ({ indicators: [] })),
      getAICapabilities().catch(() => ({ capabilities: [] })),
      getBITables().catch(() => ({ tables: [] })),
    ]).then(([docs, forecast, risk, ai, bi]) => {
      const dt = docs.templates || [];
      const fc = forecast.series || [];
      const ri = risk.indicators || [];
      const ac = ai.capabilities || [];
      const bt = bi.tables || [];

      setKpis({
        docs: dt.length * 12 + Math.floor(Math.random() * 20),
        forecast: fc.length > 0 ? Math.round((0.78 + Math.random() * 0.18) * 100) : 0,
        risks: ri.filter((r: any) => r.status === 'warning').length,
        chats: ac.length * 25 + Math.floor(Math.random() * 30),
        bi: bt.length * 8 + Math.floor(Math.random() * 10),
      });

      // Forecast ECharts
      if (fc.length > 0) {
        const s = fc[0];
        const allDates = [...(s.history || []).map((h: any) => h.date), ...(s.prediction || []).map((p: any) => p.date)];
        const allValues = [...(s.history || []).map((h: any) => h.value), ...(s.prediction || []).map((p: any) => p.value)];
        const splitIdx = (s.history || []).length;
        setChartData({
          tooltip: { trigger: 'axis' },
          legend: { data: [s.name] },
          grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
          xAxis: { type: 'category', data: allDates, axisLabel: { rotate: 30, fontSize: 10 } },
          yAxis: { type: 'value' },
          series: [{
            name: s.name, type: 'line', smooth: true, data: allValues.map((v: number, i: number) => ({
              value: v, itemStyle: i >= splitIdx ? { color: '#ff4d4f' } : undefined,
            })), lineStyle: { width: 2 }, areaStyle: { opacity: 0.1 },
          }],
        });
      }

      // Risk pie
      if (ri.length > 0) {
        setRiskChart({
          tooltip: { trigger: 'item' },
          series: [{
            type: 'pie', radius: ['40%', '70%'], center: ['50%', '50%'],
            label: { show: true, formatter: '{b}\n{d}%', fontSize: 11 },
            emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
            data: ri.map((r: any) => ({
              name: r.name, value: Math.round((r.value || 0.5) * 100),
              itemStyle: { color: r.status === 'warning' ? '#faad14' : r.status === 'danger' ? '#ff4d4f' : '#52c41a' },
            })),
          }],
        });
      }
      setLoading(false);
    });
  }, [currentData]);

  if (loading) return <Spin size="large" style={{ display: 'block', paddingTop: 120, textAlign: 'center' }} />;

  const kpiList = [
    { label: t('dashboard.kpi.documents'), value: kpis.docs, unit: t('dashboard.kpi.unit.documents'), icon: <FileTextOutlined />, color: '#1677ff', trend: '+12%', up: true },
    { label: t('dashboard.kpi.forecast'), value: kpis.forecast + '%', unit: '', icon: <LineChartOutlined />, color: '#52c41a', trend: '+3.5%', up: true },
    { label: t('dashboard.kpi.riskCoverage'), value: kpis.risks, unit: t('dashboard.kpi.unit.percent'), icon: <SafetyOutlined />, color: '#fa8c16', trend: kpis.risks > 0 ? '+2' : '0', up: false },
    { label: t('dashboard.kpi.satisfaction'), value: kpis.chats, unit: t('dashboard.kpi.unit.documents'), icon: <RobotOutlined />, color: '#722ed1', trend: '+8%', up: true },
    { label: t('dashboard.kpi.responseTime'), value: kpis.bi, unit: t('dashboard.kpi.unit.ms'), icon: <SearchOutlined />, color: '#13c2c2', trend: '+5%', up: true },
  ];

  return (
    <div>
      <div className="page-header">
        <Title level={3}>{t('dashboard.title')}</Title>
        <Paragraph type="secondary">{t('dashboard.desc', { industry: currentData?.basic?.name || currentId || '-' })}</Paragraph>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
        {kpiList.map((k) => (
          <Col span={4} key={k.label} style={{ minWidth: 180 }}>
            <Card className="kpi-card" size="small" styles={{ body: { padding: '16px 20px' } }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div className="kpi-value" style={{ color: k.color }}>{k.value}<span style={{ fontSize: 14, fontWeight: 400, color: '#8c8c8c' }}> {k.unit}</span></div>
                  <div className="kpi-label">{k.label}</div>
                </div>
                <span style={{ fontSize: 24, color: k.color, opacity: 0.3 }}>{k.icon}</span>
              </div>
              <div style={{ marginTop: 8, fontSize: 12 }}>
                {k.up ? <ArrowUpOutlined style={{ color: '#52c41a' }} /> : <ArrowDownOutlined style={{ color: '#ff4d4f' }} />}
                <span className="kpi-trend" style={{ color: k.up ? '#52c41a' : '#ff4d4f' }}>{k.trend}</span>
                <span style={{ color: '#8c8c8c', marginLeft: 8 }}>{t('dashboard.vsLastMonth')}</span>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={16} style={{ marginBottom: 20 }}>
        {moduleEntries.map((m) => (
          <Col span={4} key={m.key} style={{ minWidth: 160 }}>
            <Card
              hoverable
              className="section-card"
              onClick={() => navigate(`/${m.key}`)}
              styles={{ body: { padding: 20, background: m.color, borderRadius: 12, textAlign: 'center', cursor: 'pointer' } }}
            >
              <div style={{ marginBottom: 8 }}>{m.icon}</div>
              <div style={{ fontWeight: 600, fontSize: 14 }}>{t(m.nameKey)}</div>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={16}>
        <Col span={14}>
          <Card title={t('dashboard.trend.title')} className="section-card" size="small">
            {chartData ? <ReactECharts option={chartData} style={{ height: 320 }} /> : <div className="text-center text-secondary" style={{ padding: 60 }}>{t('common.noData')}</div>}
          </Card>
        </Col>
        <Col span={10}>
          <Card title={t('dashboard.riskPie.title')} className="section-card" size="small">
            {riskChart ? <ReactECharts option={riskChart} style={{ height: 320 }} /> : <div className="text-center text-secondary" style={{ padding: 60 }}>{t('common.noData')}</div>}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
