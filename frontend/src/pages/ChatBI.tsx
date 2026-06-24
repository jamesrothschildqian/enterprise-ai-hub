import { useEffect, useState } from 'react';
import { Card, Input, Button, Select, Table, Typography, Spin, Tag, Row, Col, Space, Empty, Segmented, Divider, Alert } from 'antd';
import { SearchOutlined, TableOutlined, BarChartOutlined, BulbOutlined, ThunderboltOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useIndustryStore } from '../store/industryStore';
import { useLocaleStore } from '../store/localeStore';
import { getBITables, queryChatBI, getDemoCases, executeDemoCase } from '../services/api';

const { Title, Paragraph, Text } = Typography;

export default function ChatBI() {
  const { currentData, currentId } = useIndustryStore();
  const { t, locale } = useLocaleStore();
  const [tables, setTables] = useState<any[]>([]);
  const [selectedTable, setSelectedTable] = useState('');
  const [queryText, setQueryText] = useState('');
  const [result, setResult] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'table' | 'chart'>('table');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [biCases, setBiCases] = useState<any[]>([]);
  const [execCase, setExecCase] = useState<string | null>(null);

  useEffect(() => {
    getDemoCases('chatbi').then(r => setBiCases(r.cases || [])).catch(() => {});
  }, []);

  const handleBiDemo = async (caseId: string) => {
    setExecCase(caseId);
    try {
      const res = await executeDemoCase(caseId);
      if (res.rows || res.columns) {
        setResult(res);
        setHistory(prev => [res.query || '', ...prev.slice(0, 19)]);
      }
    } finally { setExecCase(null); }
  };

  useEffect(() => {
    setLoading(true);
    getBITables().then(res => {
      const tbls = res.tables || [];
      setTables(tbls);
      if (tbls.length > 0) setSelectedTable(tbls[0].name);
    }).finally(() => setLoading(false));
    setResult(null);
  }, [currentData]);

  const handleQuery = async (q?: string) => {
    const query = q || queryText;
    if (!query.trim() || loading) return;
    setLoading(true);
    try {
      const res = await queryChatBI(query.trim(), selectedTable);
      setResult(res);
      setHistory(prev => [query.trim(), ...prev.slice(0, 19)]);
    } catch {
      setResult({ error: t('common.queryFailed'), query });
    } finally { setLoading(false); }
  };

  const tableData = result?.table || result;
  const columns = tableData?.columns?.map((c: string) => ({
    title: c, dataIndex: c, key: c, ellipsis: true,
    render: (v: any) => typeof v === 'number' ? v.toLocaleString() : v,
  })) || [];
  const dataSource = tableData?.rows?.map((row: any, i: number) => {
    const obj: any = { key: i };
    (tableData.columns || []).forEach((col: string, j: number) => { obj[col] = row[col] !== undefined ? row[col] : row[j]; });
    return obj;
  }) || [];

  // Auto chart
  const chartData = result?.chart;
  let chartOption: any = null;
  if (chartData) {
    const base = {
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: chartData.data?.map((d: any) => d.name) || [], axisLabel: { rotate: 30, fontSize: 11 } },
      yAxis: { type: 'value' },
    };
    if (chartData.chart_type === 'pie') {
      chartOption = {
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        series: [{
          type: 'pie', radius: ['35%', '65%'],
          label: { show: true, formatter: '{b}\n{d}%', fontSize: 11 },
          data: chartData.data?.map((d: any) => ({ name: d.name, value: d.value })) || [],
        }],
      };
    } else if (chartData.chart_type === 'line') {
      chartOption = {
        ...base,
        series: [{ type: 'line', smooth: true, data: chartData.data?.map((d: any) => d.value) || [], areaStyle: { opacity: 0.1 } }],
      };
    } else {
      chartOption = {
        ...base,
        series: [{ type: 'bar', barWidth: '40%', data: chartData.data?.map((d: any) => d.value) || [] }],
      };
    }
  }

  const exampleQuestions = (() => {
    if (locale === 'zh') {
      const examples: Record<string, string[]> = {
        international_trade: ['按金额排序显示前5条订单', '统计各国的订单数量', '查询汇率最高的币种', '显示最近1个月的订单'],
        smart_manufacturing: ['显示良率最高的产线', '按产量排序生产日报', '统计各产线OEE平均值', '找出设备温度最高的记录'],
        finance: ['按金额排序显示前5笔贷款', '统计各产品类型销售额', '查询利率最低的贷款', '显示近期的理财销售数据'],
        shipping_logistics: ['显示在途货物列表', '统计各仓库利用率', '找出预计延误的运单', '按库容排序仓库'],
        real_estate: ['按去化率排序楼盘', '统计各城市楼盘数量', '查询均价最高的楼盘', '显示待租房源'],
        hr: ['按部门统计员工数', '查询入职最早的员工', '显示培训预算最高的项目', '统计各学历人数'],
      };
      return examples[currentId] || examples.international_trade;
    }
    const examples: Record<string, string[]> = {
      international_trade: ['Show top 5 orders by amount', 'Count orders by country', 'Find currency with highest rate', 'Show orders from last month'],
      smart_manufacturing: ['Show line with lowest yield', 'Sort daily production by output', 'Average OEE by production line', 'Find highest equipment temperature'],
      finance: ['Show top 5 loans by amount', 'Sales by product type', 'Find loan with lowest rate', 'Recent wealth management sales'],
      shipping_logistics: ['Show in-transit cargo', 'Warehouse utilization rates', 'Find delayed shipments', 'Sort warehouses by capacity'],
      real_estate: ['Sort properties by sell-through rate', 'Count properties by city', 'Highest average price property', 'Show available rentals'],
      hr: ['Count employees by department', 'Find earliest hired employee', 'Show highest training budget', 'Count by education level'],
    };
    return examples[currentId] || examples.international_trade;
  })();

  return (
    <div>
      <div className="page-header">
        <Title level={3}>{t('chatbi.title')}</Title>
        <Paragraph type="secondary">{t('chatbi.desc')}</Paragraph>
      </div>

      <Row gutter={16}>
        <Col span={10}>
          <Card title={t('chatbi.tableCard')} className="section-card" size="small" styles={{ body: { maxHeight: 400, overflow: 'auto' } }}>
            {tables.map((tbl: any) => (
              <Card
                key={tbl.name}
                size="small"
                title={<Space><TableOutlined />{tbl.name}</Space>}
                style={{ marginBottom: 8, cursor: 'pointer', border: selectedTable === tbl.name ? '2px solid #1677ff' : undefined }}
                onClick={() => { setSelectedTable(tbl.name); setResult(null); }}
              >
                <Space size={4} wrap>
                  {(tbl.columns || []).map((c: string) => <Tag key={c} style={{ fontSize: 11 }}>{c}</Tag>)}
                </Space>
                <div className="text-secondary" style={{ fontSize: 11, marginTop: 6 }}>{t('chatbi.recordCount', { count: String(tbl.row_count || 0), key: tbl.primary_key || '-' })}</div>
                {tbl.preview?.length > 0 && (
                  <>
                    <Divider style={{ margin: '8px 0' }} />
                    <Table
                      dataSource={tbl.preview.map((r: any, i: number) => {
                        const obj: any = { _key: i };
                        (tbl.columns || []).forEach((c: string) => { obj[c] = r[c]; });
                        return obj;
                      })}
                      columns={(tbl.columns || []).slice(0, 4).map((c: string) => ({ title: c, dataIndex: c, key: c, ellipsis: true, render: (v: any) => typeof v === 'number' ? v.toLocaleString() : v }))}
                      pagination={false}
                      size="small"
                    />
                  </>
                )}
              </Card>
            ))}
          </Card>
        </Col>

        <Col span={14}>
          <Card className="section-card" styles={{ body: { padding: 0 } }}>
            <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0' }}>
              <Space style={{ width: '100%' }}>
                <Select
                  value={selectedTable}
                  onChange={(v) => { setSelectedTable(v); setResult(null); }}
                  style={{ width: 200 }}
                  options={tables.map(t => ({ value: t.name, label: t.name }))}
                />
                <Segmented value={viewMode} onChange={(v) => setViewMode(v as any)} options={[
                  { value: 'table', label: t('chatbi.viewTable') },
                  { value: 'chart', label: t('chatbi.viewChart') },
                ]} />
              </Space>
            </div>

            <div style={{ padding: 16 }}>
              <Input.Search
                value={queryText} onChange={e => setQueryText(e.target.value)}
                onSearch={handleQuery} enterButton={<><SearchOutlined /> {t('common.send')}</>}
                placeholder={t('chatbi.placeholder')}
                size="large" loading={loading}
              />
            </div>

            <div style={{ padding: '0 16px 12px', display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {exampleQuestions.map((q, i) => (
                <span key={i} className="example-q" onClick={() => { setQueryText(q); handleQuery(q); }}>
                  <BulbOutlined />{q}
                </span>
              ))}
            </div>

            <div style={{ padding: '0 16px 12px', display: 'flex', gap: 6, flexWrap: 'wrap', borderTop: '1px solid #f0f0f0', paddingTop: 8 }}>
              <Text strong style={{ fontSize: 11, lineHeight: '24px' }}>{t('chatbi.demoLabel')}</Text>
              {biCases.map((c: any) => (
                <Button key={c.id} size="small" icon={<ThunderboltOutlined />}
                  onClick={() => handleBiDemo(c.id)} loading={execCase === c.id}
                  style={{ fontSize: 11 }}>
                  {c.title}
                </Button>
              ))}
            </div>

            <Divider style={{ margin: 0 }} />

            <div style={{ padding: 16, minHeight: 300 }}>
              {loading ? (
                <div className="text-center" style={{ padding: 60 }}><Spin /><div className="text-secondary" style={{ marginTop: 12 }}>{t('common.aiAnalyzing')}</div></div>
              ) : result?.error ? (
                <Empty description={t('common.queryFailedRetry')} />
              ) : result ? (
                <>
                  {viewMode === 'table' && dataSource.length > 0 && (
                    <Table
                      dataSource={dataSource}
                      columns={columns}
                      size="small"
                      pagination={dataSource.length > 10 ? { pageSize: 10 } : false}
                      scroll={{ x: 'max-content' }}
                    />
                  )}
                  {viewMode === 'chart' && chartOption && (
                    <ReactECharts option={chartOption} style={{ height: 360 }} />
                  )}
                  {result.summary && (
                    <Alert
                      icon={<BulbOutlined />}
                      message={result.summary}
                      type="success"
                      showIcon
                      style={{ marginTop: 12 }}
                    />
                  )}
                  {result.sql && (
                    <div style={{ marginTop: 8, padding: 8, background: '#f5f5f5', borderRadius: 6 }}>
                      <Text code style={{ fontSize: 12 }}>{result.sql}</Text>
                    </div>
                  )}
                </>
              ) : (
                <Empty description={t('common.noQueryYet')} />
              )}
            </div>
          </Card>

          {history.length > 0 && (
            <Card title={t('chatbi.history')} className="section-card" size="small" style={{ marginTop: 12 }} styles={{ body: { maxHeight: 150, overflow: 'auto' } }}>
              {history.map((h, i) => (
                <Tag key={i} style={{ cursor: 'pointer', marginBottom: 4 }} onClick={() => { setQueryText(h); handleQuery(h); }}>{h}</Tag>
              ))}
            </Card>
          )}
        </Col>
      </Row>
    </div>
  );
}


