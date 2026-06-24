import { useEffect, useState, useRef } from 'react';
import { Card, Button, Table, Tag, Typography, Spin, Row, Col, message, Space, Tabs, Descriptions, Alert, Divider, Empty } from 'antd';
import { UploadOutlined, FileTextOutlined, ThunderboltOutlined, InboxOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useIndustryStore } from '../store/industryStore';
import { useLocaleStore } from '../store/localeStore';
import { getDocTemplates, demoParse, batchDemoParse, getDemoCases, executeDemoCase } from '../services/api';

const { Title, Paragraph, Text } = Typography;

export default function DocParser() {
  const { currentData, currentId } = useIndustryStore();
  const { t } = useLocaleStore();
  const [templates, setTemplates] = useState<any[]>([]);
  const [parseResult, setParseResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [batchResults, setBatchResults] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState('templates');
  const [dragover, setDragover] = useState(false);
  const [demoCases, setDemoCases] = useState<any[]>([]);
  const [executingCase, setExecutingCase] = useState<string | null>(null);

  useEffect(() => {
    getDemoCases('doc_parser').then(r => setDemoCases(r.cases || [])).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    getDocTemplates().then(r => setTemplates(r.templates || [])).finally(() => setLoading(false));
    setParseResult(null);
    setBatchResults([]);
  }, [currentData]);

  const handleDemoParse = async (id: string) => {
    setLoading(true);
    try {
      const res = await demoParse(id);
      setParseResult(res);
      setActiveTab('result');
    } finally { setLoading(false); }
  };

  const handleBatchDemo = async () => {
    setLoading(true);
    try {
      const res = await batchDemoParse();
      setBatchResults(res.results || []);
      setActiveTab('batch');
      message.success(t('docParser.demoCaseLoaded', { count: (res.results || []).length }));
    } finally { setLoading(false); }
  };

  const handleDemoCase = async (caseId: string) => {
    setExecutingCase(caseId);
    try {
      const res = await executeDemoCase(caseId);
      if (res.extracted_fields || res.parse_result) {
        setParseResult(res.parse_result || res);
        setActiveTab('result');
      } else if (res.results) {
        setBatchResults(res.results);
        setActiveTab('batch');
      }
      message.success(t('docParser.demoCaseExecuted', { name: demoCases.find(c => c.id === caseId)?.title || caseId }));
    } finally { setExecutingCase(null); }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragover(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      message.info(t('docParser.demoMode', { file: files[0].name }));
    }
  };

  const fieldPieOption = parseResult?.extracted_fields ? {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie', radius: ['40%', '70%'],
      label: { show: true, formatter: '{b}: {c}', fontSize: 11 },
      data: Object.entries(parseResult.extracted_fields).map(([k, v]) => ({
        name: k, value: String(v).length,
      })),
    }],
  } : null;

  const docTypeColor: Record<string, string> = {
    customs_declaration: 'blue', letter_of_credit: 'gold', commercial_invoice: 'green',
    bill_of_lading: 'cyan', production_order: 'purple', qc_report: 'orange',
    credit_contract: 'red', financial_report: 'geekblue', labor_contract: 'magenta', resume: 'lime',
  };

  return (
    <div>
      <div className="page-header">
        <Title level={3}>{t('docParser.title')}</Title>
        <Paragraph type="secondary">{t('docParser.desc')}</Paragraph>
      </div>

      <Row gutter={16}>
        <Col span={8}>
          <Card title={t('docParser.uploadCard')} className="section-card" size="small" styles={{ body: { padding: 0 } }}>
            <div
              className={`upload-zone ${dragover ? 'dragover' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragover(true); }}
              onDragLeave={() => setDragover(false)}
              onDrop={onDrop}
              onClick={() => message.info(t('docParser.demoModeHint'))}
            >
              <InboxOutlined style={{ fontSize: 48, color: '#1677ff' }} />
              <div style={{ fontSize: 16, fontWeight: 600, marginTop: 12 }}>{t('docParser.uploadHint')}</div>
              <div className="text-secondary" style={{ fontSize: 12, marginTop: 4 }}>{t('docParser.uploadFormats')}</div>
            </div>
          </Card>

          <Card className="section-card" size="small" style={{ marginTop: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button type="primary" icon={<ThunderboltOutlined />} block size="large" onClick={handleBatchDemo} loading={loading}>
                {t('docParser.batchFill')}
              </Button>
              <Text type="secondary" style={{ fontSize: 12, textAlign: 'center' }}>
                {t('docParser.batchFillDesc')}
              </Text>
            </Space>
          </Card>

          <Card title={`📋 ${t('docParser.demoCase')}`} className="section-card" size="small" style={{ marginTop: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {demoCases.map((c: any) => (
                <Button key={c.id} block type="default" onClick={() => handleDemoCase(c.id)} loading={executingCase === c.id}
                  icon={<FileTextOutlined />} style={{ textAlign: 'left', height: 'auto', whiteSpace: 'normal', padding: '8px 12px' }}>
                  <div><strong>{c.title}</strong></div>
                  <div className="text-secondary" style={{ fontSize: 11, marginTop: 2 }}>{c.description}</div>
                </Button>
              ))}
            </Space>
          </Card>
        </Col>

        <Col span={16}>
          <Card className="section-card" size="small" styles={{ body: { padding: 0 } }}>
            <Tabs activeKey={activeTab} onChange={setActiveTab} tabBarStyle={{ padding: '8px 16px 0', margin: 0 }} items={[
              {
                key: 'templates', label: t('docParser.templates', { count: templates.length }),
                children: (
                  <div style={{ padding: 16 }}>
                    {loading ? <Spin style={{ display: 'block', padding: 40 }} /> : (
                      <Row gutter={[12, 12]}>
                        {templates.map((tmpl: any) => (
                          <Col span={12} key={tmpl.id}>
                            <Card size="small" hoverable
                              actions={[<Button type="link" size="small" icon={<FileTextOutlined />} onClick={() => handleDemoParse(tmpl.id)}>{t('docParser.demoParse')}</Button>]}
                            >
                              <Space>
                                <Tag color={docTypeColor[tmpl.id] || 'default'}>{tmpl.name}</Tag>
                                <Text type="secondary" style={{ fontSize: 12 }}>{t('docParser.fields', { count: tmpl.fields?.length || 0 })}</Text>
                              </Space>
                              <div className="text-secondary" style={{ fontSize: 12, marginTop: 6 }}>{tmpl.description || tmpl.id}</div>
                            </Card>
                          </Col>
                        ))}
                      </Row>
                    )}
                  </div>
                ),
              },
              {
                key: 'result', label: t('docParser.parseResult'), disabled: !parseResult,
                children: parseResult ? (
                  <div style={{ padding: 16 }}>
                    <Alert message={t('docParser.parseInfo', { type: parseResult.document_type, count: parseResult.fields_count || Object.keys(parseResult.extracted_fields || {}).length })} type="success" showIcon style={{ marginBottom: 12 }} />
                    <Row gutter={16}>
                      <Col span={14}>
                        <Descriptions title={t('docParser.extractedFields')} column={1} size="small" bordered>
                          {Object.entries(parseResult.extracted_fields || {}).map(([k, v]) => (
                            <Descriptions.Item key={k} label={k}><Text strong>{String(v)}</Text></Descriptions.Item>
                          ))}
                        </Descriptions>
                      </Col>
                      <Col span={10}>
                        {fieldPieOption && <ReactECharts option={fieldPieOption} style={{ height: 260 }} />}
                        {parseResult.raw_preview && (
                          <Card title={t('docParser.originalPreview')} size="small" style={{ marginTop: 12 }}>
                            <pre style={{ fontSize: 11, maxHeight: 200, overflow: 'auto', whiteSpace: 'pre-wrap', margin: 0 }}>{parseResult.raw_preview}</pre>
                          </Card>
                        )}
                      </Col>
                    </Row>
                    <Divider />
                    <Text type="secondary" style={{ fontSize: 12 }}>{t('docParser.engineInfo', { engine: parseResult.parse_method || 'mock_ai_parser' })}</Text>
                  </div>
                ) : <Empty description={t('docParser.selectTemplate')} style={{ padding: 40 }} />,
              },
              {
                key: 'batch', label: t('docParser.batchResult', { count: batchResults.length }), disabled: batchResults.length === 0,
                children: (
                  <div style={{ padding: 16 }}>
                    <Table
                      dataSource={batchResults.map((r, i) => ({ ...r, key: i }))}
                      columns={[
                        { title: t('docParser.table.docType'), dataIndex: 'type', render: (t: string) => <Tag color={docTypeColor[t] || 'default'}>{t}</Tag> },
                        { title: t('docParser.table.title'), dataIndex: 'title', ellipsis: true },
                        { title: t('docParser.table.fields'), dataIndex: 'fields', render: (f: any) => (typeof f === 'object' ? Object.keys(f).length : 0) },
                        { title: t('docParser.table.action'), render: (_: any, r: any) => <Button size="small" onClick={() => { setParseResult(r); setActiveTab('result'); }}>{t('common.view')}</Button> },
                      ]}
                      pagination={false} size="small"
                    />
                  </div>
                ),
              },
            ]} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}
