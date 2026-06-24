import { useState, useEffect, useRef } from 'react';
import { Card, Input, Button, Typography, Spin, Tag, Row, Col, Space, Avatar, Divider, Empty, Modal, Form, InputNumber } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined, BulbOutlined, ThunderboltOutlined, FileTextOutlined } from '@ant-design/icons';
import { useIndustryStore } from '../store/industryStore';
import { useLocaleStore } from '../store/localeStore';
import { chatWithAI, getAICapabilities, getAIKnowledge, getAIGreeting, batchGenerate, getDemoCases, executeDemoCase } from '../services/api';

const { Title, Paragraph, Text } = Typography;

interface Msg { role: 'user' | 'assistant'; content: string; }

export default function AIAgent() {
  const { currentData, currentId } = useIndustryStore();
  const { t } = useLocaleStore();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [capabilities, setCapabilities] = useState<string[]>([]);
  const [knowledge, setKnowledge] = useState<any[]>([]);
  const [batchOpen, setBatchOpen] = useState(false);
  const [batchResult, setBatchResult] = useState<any[]>([]);
  const [batchLoading, setBatchLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [agentCases, setAgentCases] = useState<any[]>([]);
  const [execCase, setExecCase] = useState<string | null>(null);

  useEffect(() => {
    getDemoCases('ai_agent').then(r => setAgentCases(r.cases || [])).catch(() => {});
  }, []);

  const handleAgentDemo = async (caseId: string) => {
    setExecCase(caseId);
    try {
      const res = await executeDemoCase(caseId);
      if (res.reply) {
        setMessages(prev => [...prev, { role: 'assistant', content: res.reply }]);
      } else if (res.marketing) {
        setBatchResult([...(res.marketing || []), ...(res.invitation || [])]);
      } else if (res.matched_qa) {
        setMessages(prev => [...prev, { role: 'assistant', content: `[KB Match]\nQ: ${res.matched_qa.question}\nA: ${res.matched_qa.answer}` }]);
      }
    } finally { setExecCase(null); }
  };

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getAIGreeting().then(r => r.greeting || t('aiAgent.greeting')),
      getAICapabilities().then(r => r.capabilities || []),
      getAIKnowledge().then(r => r.knowledge_base || []),
    ]).then(([greeting, caps, kb]) => {
      setMessages([{ role: 'assistant', content: greeting }]);
      setCapabilities(caps);
      setKnowledge(kb);
    }).finally(() => setLoading(false));
    setBatchResult([]);
  }, [currentData]);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput('');
    setMessages(p => [...p, { role: 'user', content: userMsg }]);
    setLoading(true);
    try {
      const res = await chatWithAI(userMsg, messages.slice(-6).map(m => ({ role: m.role, content: m.content })));
      setMessages(p => [...p, { role: 'assistant', content: res.reply || t('aiAgent.noReply') }]);
    } catch {
      setMessages(p => [...p, { role: 'assistant', content: t('aiAgent.requestFailed') }]);
    } finally { setLoading(false); }
  };

  const handleQuickQ = (q: string) => {
    setInput(q);
  };

  const handleBatch = async (values: any) => {
    setBatchLoading(true);
    try {
      const res = await batchGenerate(values.type, { company_name: values.company, product: values.product || '', target_market: values.target || '' }, values.count || 3);
      setBatchResult(res.results || []);
    } finally { setBatchLoading(false); }
  };

  const disabled = loading;

  return (
    <div>
      <div className="page-header">
        <Title level={3}>{t('aiAgent.title')}</Title>
        <Paragraph type="secondary">{t('aiAgent.desc')}</Paragraph>
      </div>

      <Row gutter={16}>
        <Col span={16}>
          <Card className="section-card" styles={{ body: { padding: 0 } }}>
            <div className="chat-panel">
              <div className="chat-messages">
                {messages.map((m, i) => (
                  <div key={i} className={`chat-bubble ${m.role}`}>
                    <Space style={{ marginBottom: 4 }}>
                      <Avatar size={20} icon={m.role === 'user' ? <UserOutlined /> : <RobotOutlined />} style={{ background: m.role === 'user' ? '#1677ff' : '#52c41a' }} />
                      <Text style={{ fontSize: 12, color: m.role === 'user' ? 'rgba(255,255,255,0.8)' : '#999' }}>{m.role === 'user' ? t('aiAgent.chatUser') : t('aiAgent.chatAI')}</Text>
                    </Space>
                    <div style={{ marginTop: 4 }}>{m.content}</div>
                  </div>
                ))}
                {loading && <div className="chat-bubble assistant"><Spin size="small" /> {t('aiAgent.thinking')}</div>}
                <div ref={chatEndRef} />
              </div>
              <div className="chat-input-bar">
                <Input.Search
                  value={input} onChange={e => setInput(e.target.value)}
                  onSearch={handleSend} enterButton={<><SendOutlined /> {t('common.send')}</>}
                  placeholder={t('aiAgent.placeholder')} loading={loading}
                  size="large"
                />
              </div>
            </div>
          </Card>
        </Col>

        <Col span={8}>
          <Card title={t('aiAgent.quickQuestions')} className="section-card" size="small" styles={{ body: { maxHeight: 200, overflow: 'auto' } }}>
            {capabilities.length > 0 ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {capabilities.map((c, i) => (
                  <Tag key={i} className="quick-q" onClick={() => handleQuickQ(t('aiAgent.quickIntro', { name: c }))} style={{ cursor: 'pointer' }}>
                    {c}
                  </Tag>
                ))}
              </div>
            ) : <Text type="secondary">{t('aiAgent.noQuickQuestions')}</Text>}
          </Card>

          <Card title={t('aiAgent.knowledgeBase')} className="section-card" size="small" style={{ marginTop: 12 }} styles={{ body: { maxHeight: 280, overflow: 'auto' } }}>
            {knowledge.length > 0 ? knowledge.slice(0, 8).map((item, i) => (
              <div key={i} className="quick-q" style={{ marginBottom: 8, fontSize: 12 }} onClick={() => handleQuickQ(item.question)}>
                <BulbOutlined style={{ color: '#faad14', marginRight: 6 }} />
                <Text ellipsis={{ tooltip: item.question }}>{item.question}</Text>
              </div>
            )) : <Text type="secondary">{t('aiAgent.noKnowledge')}</Text>}
          </Card>

          <Card className="section-card" size="small" style={{ marginTop: 12 }}>
            <Button icon={<ThunderboltOutlined />} block onClick={() => setBatchOpen(true)}>{t('aiAgent.batchGenerate')}</Button>
          </Card>

          <Card title={t('aiAgent.demoCase')} className="section-card" size="small" style={{ marginTop: 12 }} styles={{ body: { padding: '8px 12px' } }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {agentCases.map((c: any) => (
                <Button key={c.id} size="small" block type="default" icon={<ThunderboltOutlined />}
                  onClick={() => handleAgentDemo(c.id)} loading={execCase === c.id}
                  style={{ textAlign: 'left', height: 'auto', whiteSpace: 'normal', padding: '6px 10px', fontSize: 12 }}>
                  {c.title}
                </Button>
              ))}
            </Space>
          </Card>
        </Col>
      </Row>

      <Modal title={t('aiAgent.batchModalTitle')} open={batchOpen} onCancel={() => setBatchOpen(false)} footer={null} width={600}>
        <Form layout="vertical" onFinish={handleBatch}>
          <Form.Item label={t('aiAgent.batchType')} name="type" initialValue="marketing" rules={[{ required: true }]}>
            <select style={{ width: '100%', padding: '4px 8px' }}>
              <option value="marketing">{t('aiAgent.batchTypeMarketing')}</option>
              <option value="invitation">{t('aiAgent.batchTypeInvite')}</option>
            </select>
          </Form.Item>
          <Form.Item label={t('aiAgent.companyName')} name="company" initialValue="示例科技">
            <Input placeholder={t('aiAgent.companyNamePlaceholder')} />
          </Form.Item>
          <Form.Item label={t('aiAgent.product')} name="product">
            <Input placeholder={t('aiAgent.productPlaceholder')} />
          </Form.Item>
          <Form.Item label={t('aiAgent.targetMarket')} name="target">
            <Input placeholder={t('aiAgent.targetPlaceholder')} />
          </Form.Item>
          <Form.Item label={t('aiAgent.generateCount')} name="count" initialValue={3}>
            <InputNumber min={1} max={10} />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={batchLoading} icon={<ThunderboltOutlined />} block>{t('aiAgent.startGenerate')}</Button>
        </Form>
        {batchResult.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <Divider>{t('aiAgent.batchResult')}</Divider>
            {batchResult.map((r, i) => (
              <Card key={i} size="small" title={`v${r.version}`} style={{ marginBottom: 8 }}>
                <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12, margin: 0 }}>{r.content}</pre>
              </Card>
            ))}
          </div>
        )}
      </Modal>
    </div>
  );
}
