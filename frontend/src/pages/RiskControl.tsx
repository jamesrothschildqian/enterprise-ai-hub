import { useEffect, useState } from 'react';
import { Card, Row, Col, Tag, Typography, Spin, Progress, Alert, Divider, Button, Table, Statistic, Space, Empty } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, MinusOutlined, ThunderboltOutlined, SafetyOutlined, WarningOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useIndustryStore } from '../store/industryStore';
import { useLocaleStore } from '../store/localeStore';
import { getRiskIndicators, assessRisk, analyzeTransactions, getDemoCases, executeDemoCase } from '../services/api';

const { Title, Paragraph, Text } = Typography;

const sevColor: Record<string, string> = { high: '#ff4d4f', medium: '#fa8c16', low: '#52c41a' };
const bkSevMap: Record<string, string> = { '高': 'high', '中': 'medium', '低': 'low' };
const trendIcon: Record<string, any> = {
  up: <ArrowUpOutlined style={{ color: '#ff4d4f' }} />,
  down: <ArrowDownOutlined style={{ color: '#52c41a' }} />,
  stable: <MinusOutlined style={{ color: '#999' }} />,
};

export default function RiskControl() {
  const { currentData, currentId } = useIndustryStore();
  const { t } = useLocaleStore();
  const [indicators, setIndicators] = useState<any[]>([]);
  const [overall, setOverall] = useState(0);
  const [riskList, setRiskList] = useState<any[]>([]);
  const [assessment, setAssessment] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [riskCases, setRiskCases] = useState<any[]>([]);
  const [execCase, setExecCase] = useState<string | null>(null);

  useEffect(() => {
    getDemoCases('risk_control').then(r => setRiskCases(r.cases || [])).catch(() => {});
  }, []);

  const handleRiskDemo = async (caseId: string) => {
    setExecCase(caseId);
    try {
      const res = await executeDemoCase(caseId);
      if (res.risk_list) setRiskList(res.risk_list);
      if (res.risk_assessment) setAssessment(res.risk_assessment);
      if (res.anomalies) setRiskList(res.anomalies.map((a: any) => ({ entity: a.entity, risks: a.anomalies, max_severity: 'high', detail: a.detail })));
    } finally { setExecCase(null); }
  };

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getRiskIndicators(),
      assessRisk(),
      analyzeTransactions(),
    ]).then(([ind, ass, tx]) => {
      setIndicators(ind.indicators || []);
      setOverall(ind.overall_score || 0);
      setAssessment(ass);
      setRiskList(tx.risk_list || []);
    }).finally(() => setLoading(false));
  }, [currentData]);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const tx = await analyzeTransactions();
      setRiskList(tx.risk_list || []);
    } finally { setLoading(false); }
  };

  const gaugeOption = {
    series: [{
      type: 'gauge', startAngle: 200, endAngle: -20,
      min: 0, max: 100, pointer: { show: true },
      progress: { show: true, width: 18, itemStyle: { color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
        colorStops: [{ offset: 0, color: '#52c41a' }, { offset: 0.5, color: '#faad14' }, { offset: 1, color: '#ff4d4f' }] } } },
      axisLine: { lineStyle: { width: 18 } },
      axisTick: { show: false }, splitLine: { show: false }, axisLabel: { show: false },
      detail: { formatter: (v: number) => t('riskControl.scoreSuffix', { value: v }), fontSize: 20, fontWeight: 'bold', offsetCenter: [0, '40%'], color: overall < 0.35 ? '#52c41a' : overall < 0.55 ? '#fa8c16' : '#ff4d4f' },
      data: [{ value: Math.round((1 - overall) * 100), name: t('riskControl.scoreName') }],
    }],
  };

  const pieOption = indicators.length > 0 ? {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie', radius: ['35%', '65%'],
      label: { show: true, formatter: '{b}\n{d}%', fontSize: 11 },
      emphasis: { label: { show: true, fontSize: 14 } },
      data: indicators.map((r: any) => ({
        name: r.name, value: Math.round((r.value || 0.5) * 100),
        itemStyle: { color: r.value > 0.6 ? '#ff4d4f' : r.value > 0.4 ? '#faad14' : '#52c41a' },
      })),
    }],
  } : null;

  const riskColumns = [
    { title: t('riskControl.table.entity'), dataIndex: 'entity', key: 'entity', ellipsis: true },
    { title: t('riskControl.table.riskLevel'), dataIndex: 'max_severity', key: 'severity',
      render: (s: string) => {
        const sevKey = bkSevMap[s] || 'low';
        return <Tag color={sevColor[sevKey] || 'default'}>{t(`riskControl.severity.${sevKey}`)}</Tag>;
      },
    },
    { title: t('riskControl.table.riskTag'), dataIndex: 'risks', key: 'risks',
      render: (risks: any[]) => (
        <Space size={4} wrap>
          {(risks || []).map((r: any, i: number) => (
            <Tag key={i} color={sevColor[r.severity]} style={{ fontSize: 11 }}>{r.risk_name || r.risk_label}</Tag>
          ))}
        </Space>
      ),
    },
    { title: t('riskControl.table.detail'), dataIndex: 'detail', key: 'detail', ellipsis: true, width: 200 },
  ];

  if (loading && indicators.length === 0) return <Spin size="large" style={{ display: 'block', paddingTop: 120, textAlign: 'center' }} />;

  return (
    <div>
      <div className="page-header">
        <Title level={3}>{t('riskControl.title')}</Title>
        <Paragraph type="secondary">{t('riskControl.desc')}</Paragraph>
      </div>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card className="kpi-card" size="small" style={{ textAlign: 'center', background: overall < 0.35 ? '#f6ffed' : overall < 0.55 ? '#fff7e6' : '#fff1f0' }}>
            <Statistic title={t('riskControl.safetyScore')} value={Math.round((1 - overall) * 100)} suffix={t('common.suffix.score')}
              valueStyle={{ color: overall < 0.35 ? '#52c41a' : overall < 0.55 ? '#fa8c16' : '#ff4d4f', fontSize: 28 }}
            />
            <div style={{ marginTop: 4 }}>
              <Tag color={overall < 0.35 ? 'green' : overall < 0.55 ? 'orange' : 'red'} style={{ fontSize: 13, padding: '2px 12px' }}>
                {t(`riskControl.severity.${bkSevMap[assessment?.risk_level] || 'medium'}Short`)}{t('common.suffix.risk')}
              </Tag>
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card className="kpi-card" size="small" style={{ textAlign: 'center' }}>
            <Statistic title={t('riskControl.monitorCount')} value={indicators.length} suffix={t('common.suffix.items')} valueStyle={{ fontSize: 28 }} />
            <div className="text-secondary" style={{ fontSize: 12, marginTop: 4 }}>{indicators.filter(r => r.status === 'warning').length}{t('riskControl.warningCount')}</div>
          </Card>
        </Col>
        <Col span={6}>
          <Card className="kpi-card" size="small" style={{ textAlign: 'center' }}>
            <Statistic title={t('riskControl.riskCount')} value={riskList.length} suffix={t('common.suffix.transactions')} valueStyle={{ fontSize: 28, color: riskList.length > 0 ? '#ff4d4f' : '#52c41a' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card className="kpi-card" size="small" style={{ textAlign: 'center' }}>
            <Button type="primary" icon={<ThunderboltOutlined />} onClick={handleAnalyze} loading={loading} size="large" block>
              {t('riskControl.runAnalysis')}
            </Button>
            <div className="text-secondary" style={{ fontSize: 11, marginTop: 6 }}>{t('riskControl.runAnalysisDesc')}</div>
            <Divider style={{ margin: '8px 0' }} />
            <Text strong style={{ fontSize: 11 }}>{t('riskControl.demoCase')}</Text>
            <Space direction="vertical" style={{ width: '100%', marginTop: 4 }}>
              {riskCases.map((c: any) => (
                <Button key={c.id} size="small" block icon={<ThunderboltOutlined />}
                  onClick={() => handleRiskDemo(c.id)} loading={execCase === c.id}
                  style={{ fontSize: 11, textAlign: 'left', height: 'auto', padding: '4px 8px' }}>
                  {c.title}
                </Button>
              ))}
            </Space>
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        {indicators.map((ind: any) => (
          <Col span={6} key={ind.id} style={{ marginBottom: 16 }}>
            <Card size="small" className="kpi-card"
              style={{ borderLeft: `4px solid ${ind.value > 0.6 ? '#ff4d4f' : ind.value > 0.4 ? '#faad14' : '#52c41a'}` }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <Text strong style={{ fontSize: 13 }}>{ind.name}</Text>
                <Space size={4}>
                  {trendIcon[ind.trend]}
                  <Tag color={ind.status === 'warning' ? 'orange' : ind.status === 'danger' ? 'red' : 'green'}>
                    {ind.status === 'warning' ? t('riskControl.tag.warning') : ind.status === 'danger' ? t('riskControl.tag.danger') : t('riskControl.tag.safe')}
                  </Tag>
                </Space>
              </div>
              <Progress
                percent={Math.round((ind.value || 0) * 100)}
                strokeColor={ind.value > 0.6 ? '#ff4d4f' : ind.value > 0.4 ? '#faad14' : '#52c41a'}
                size="small" format={p => `${p}%`}
              />
              <Text type="secondary" style={{ fontSize: 11, display: 'block', marginTop: 6 }}>{ind.detail}</Text>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={16}>
        <Col span={8}>
          <Card title={t('riskControl.card.health')} className="section-card" size="small">
            <ReactECharts option={gaugeOption} style={{ height: 260 }} />
            {assessment?.suggestions?.length > 0 && (
              <div style={{ marginTop: 8 }}>
                {assessment.suggestions.map((s: any, i: number) => (
                  <Alert key={i} message={`${s.risk}：${s.detail}`} type={s.priority === '高' ? 'error' : s.priority === '中' ? 'warning' : 'success'} showIcon style={{ marginBottom: 4, fontSize: 12 }} />
                ))}
              </div>
            )}
          </Card>
        </Col>
        <Col span={8}>
          <Card title={t('riskControl.card.riskDistribution')} className="section-card" size="small">
            {pieOption ? <ReactECharts option={pieOption} style={{ height: 260 }} /> : <Empty description={t('common.noData')} />}
          </Card>
        </Col>
        <Col span={8}>
          <Card title={t('riskControl.card.assessment')} className="section-card" size="small" styles={{ body: { maxHeight: 260, overflow: 'auto' } }}>
            {assessment?.suggestions?.length > 0 ? assessment.suggestions.map((s: any, i: number) => (
              <Alert
                key={i}
                message={<><Text strong style={{ color: s.priority === '高' ? '#ff4d4f' : '#fa8c16' }}>{s.risk}</Text>：{s.detail}</>}
                type={s.priority === '高' ? 'error' : s.priority === '中' ? 'warning' : 'success'}
                showIcon style={{ marginBottom: 8, fontSize: 12 }}
              />
            )) : <Text type="secondary">{t('riskControl.noAdvice')}</Text>}
          </Card>
        </Col>
      </Row>

      <Card title={t('riskControl.card.riskList')} className="section-card" size="small" style={{ marginTop: 16 }} styles={{ body: { padding: 0 } }}>
        <Table
          dataSource={riskList.map((r, i) => ({ ...r, key: r.transaction_id || i }))}
          columns={riskColumns}
          pagination={false}
          size="small"
          locale={{ emptyText: t('riskControl.table.emptyText') }}
        />
      </Card>
    </div>
  );
}
