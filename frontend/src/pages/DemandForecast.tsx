import { useEffect, useState } from 'react';
import { Card, Button, Statistic, Typography, Segmented, Spin, Row, Col, Space, InputNumber, Alert, Divider, Empty } from 'antd';
import { ThunderboltOutlined, LineChartOutlined, BulbOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useIndustryStore } from '../store/industryStore';
import { useLocaleStore } from '../store/localeStore';
import { getForecastData, runPredict, getForecastInsight, getDemoCases, executeDemoCase } from '../services/api';

const { Title, Paragraph, Text } = Typography;

export default function DemandForecast() {
  const { currentData, currentId } = useIndustryStore();
  const { t } = useLocaleStore();
  const [fcData, setFcData] = useState<any>(null);
  const [metric, setMetric] = useState<string>('');
  const [periods, setPeriods] = useState(30);
  const [insight, setInsight] = useState('');
  const [loading, setLoading] = useState(false);
  const [executingCase, setExecutingCase] = useState<string | null>(null);
  const [forecastCases, setForecastCases] = useState<any[]>([]);

  useEffect(() => {
    getDemoCases('demand_forecast').then(r => setForecastCases(r.cases || [])).catch(() => {});
  }, []);

  const handleDemoCase = async (caseId: string) => {
    setExecutingCase(caseId);
    try {
      const res = await executeDemoCase(caseId);
      if (res.series) {
        setFcData(res);
        setInsight('');
      } else if (res.insight) {
        setFcData(res);
        setInsight(res.insight);
      }
    } finally { setExecutingCase(null); }
  };

  useEffect(() => {
    setLoading(true);
    getForecastData().then(res => {
      setFcData(res);
      setMetric(res.metrics?.[0]?.key || '');
    }).finally(() => setLoading(false));
    setInsight('');
  }, [currentData]);

  const handlePredict = async () => {
    setLoading(true);
    try {
      const res = await runPredict(periods);
      setFcData(res);
      setMetric(res.metrics?.[0]?.key || '');
    } finally { setLoading(false); }
  };

  const handleInsight = async () => {
    setLoading(true);
    try {
      const res = await getForecastInsight(metric);
      setInsight(res.insight || t('demandForecast.noInsight'));
    } finally { setLoading(false); }
  };

  if (!fcData) return <Spin size="large" style={{ display: 'block', paddingTop: 120, textAlign: 'center' }} />;

  const currentSeries = fcData.series?.find((s: any) => s.key === metric) || fcData.series?.[0];
  const metricUnit = fcData.metrics?.find((m: any) => m.key === metric)?.unit || '';

  // Build ECharts option
  let chartOption: any = null;
  if (currentSeries) {
    const allDates = [...(currentSeries.history || []).map((h: any) => h.date), ...(currentSeries.prediction || []).map((p: any) => p.date)];
    const allValues = [...(currentSeries.history || []).map((h: any) => h.value), ...(currentSeries.prediction || []).map((p: any) => p.value)];
    const splitIdx = (currentSeries.history || []).length;
    chartOption = {
      tooltip: { trigger: 'axis', formatter: (params: any) => {
        const p = params[0];
        const isPred = p.dataIndex >= splitIdx;
        return `${p.axisValue}<br/>${p.seriesName}: ${p.value}${metricUnit}${isPred ? t('demandForecast.predictSuffix') : ''}`;
      }},
      legend: { data: [t('demandForecast.historyData'), t('demandForecast.forecastData')] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: allDates, axisLabel: { rotate: 45, fontSize: 10 } },
      yAxis: { type: 'value', name: metricUnit },
      series: [
        {
          name: t('demandForecast.historyData'), type: 'line', smooth: true,
              data: allValues.map((v: number, i: number) => (i < splitIdx ? v : null)),
          lineStyle: { width: 2, color: '#1677ff' }, areaStyle: { opacity: 0.1, color: '#1677ff' },
          symbol: 'circle', symbolSize: 4,
        },
        {
          name: t('demandForecast.forecastData'), type: 'line', smooth: true,
              data: allValues.map((v: number, i: number) => (i >= splitIdx ? v : null)),
          lineStyle: { width: 2, color: '#ff4d4f', type: 'dashed' },
          areaStyle: { opacity: 0.05, color: '#ff4d4f' },
          symbol: 'diamond', symbolSize: 6,
        },
      ],
    };
  }

  // ECharts bar option
  const barOption = chartOption ? {
    ...chartOption,
    series: chartOption.series.map((s: any, idx: number) => ({ ...s, type: 'bar', barWidth: '40%' })),
  } : null;

  return (
    <div>
      <div className="page-header">
        <Title level={3}>{t('demandForecast.title')}</Title>
        <Paragraph type="secondary">{t('demandForecast.desc')}</Paragraph>
      </div>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={16}>
          <Card className="section-card" size="small">
            <Space style={{ marginBottom: 12 }}>
              {fcData.metrics?.length > 0 && (
                <Segmented
                  value={metric}
                  onChange={(v) => setMetric(v as string)}
                  options={fcData.metrics.map((m: any) => ({ value: m.key, label: `${m.name} (${m.unit || '-'})` }))}
                />
              )}
              <Space.Compact>
                <InputNumber
                  value={periods} onChange={(v) => setPeriods(v || 30)}
                  min={7} max={90}
                  style={{ width: 100 }}
                />
                <Button style={{ pointerEvents: 'none', backgroundColor: '#f5f5f5', borderColor: '#d9d9d9', color: '#999' }}>{t('demandForecast.days')}</Button>
              </Space.Compact>
            </Space>
            <Space>
              <Button type="primary" icon={<LineChartOutlined />} onClick={handlePredict} loading={loading}>{t('demandForecast.runPredict')}</Button>
              <Button icon={<BulbOutlined />} onClick={handleInsight} loading={loading}>{t('demandForecast.runInsight')}</Button>
            </Space>
            <Divider style={{ margin: '12px 0' }} />
            <Text strong style={{ fontSize: 12 }}>{t('common.demoRun')}</Text>
            <div style={{ display: 'flex', gap: 6, marginTop: 6, flexWrap: 'wrap' }}>
              {forecastCases.map((c: any) => (
                <Button key={c.id} size="small" icon={<ThunderboltOutlined />}
                  onClick={() => handleDemoCase(c.id)} loading={executingCase === c.id}>
                  {c.title}
                </Button>
              ))}
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Row gutter={8}>
            {currentSeries && (
              <>
                <Col span={12}>
                  <Card size="small" className="kpi-card" style={{ textAlign: 'center' }}>
                    <Statistic
                      title={t('demandForecast.latestValue')}
                      value={currentSeries.history?.[currentSeries.history.length - 1]?.value || '-'}
                      suffix={metricUnit}
                    />
                  </Card>
                </Col>
                <Col span={12}>
                  <Card size="small" className="kpi-card" style={{ textAlign: 'center' }}>
                    <Statistic
                      title={t('demandForecast.firstPredict')}
                      value={currentSeries.prediction?.[0]?.value || '-'}
                      suffix={metricUnit}
                      valueStyle={{ color: '#ff4d4f' }}
                    />
                  </Card>
                </Col>
              </>
            )}
          </Row>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card title={t('demandForecast.trendChart')} className="section-card" size="small">
            {chartOption ? <ReactECharts option={chartOption} style={{ height: 380 }} /> : <Empty description={t('common.noData')} />}
          </Card>
        </Col>
        <Col span={12}>
          <Card title={t('demandForecast.barChart')} className="section-card" size="small">
            {barOption ? <ReactECharts option={barOption} style={{ height: 380 }} /> : <Empty description={t('common.noData')} />}
          </Card>
        </Col>
      </Row>

      {insight && (
        <Card title={t('demandForecast.insightTitle')} className="section-card" size="small" style={{ marginTop: 16 }}>
          <Alert icon={<BulbOutlined />} message={insight} type="info" showIcon />
          <div className="text-secondary" style={{ fontSize: 12, marginTop: 8 }}>{t('demandForecast.engineInfo', { confidence: fcData.confidence || '85%' })}</div>
        </Card>
      )}
    </div>
  );
}
