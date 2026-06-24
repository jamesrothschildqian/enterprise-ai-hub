import { useState } from 'react';
import { FloatButton, Modal, Typography, List, Tag, Space } from 'antd';
import { QuestionCircleOutlined, SwapOutlined, BulbOutlined } from '@ant-design/icons';
import { useLocaleStore } from '../store/localeStore';

const { Paragraph, Text } = Typography;

export default function DemoGuide() {
  const { t } = useLocaleStore();
  const [open, setOpen] = useState(false);

  const tips = [
    { icon: <SwapOutlined />, key: 'demo.guide.tip1', color: 'blue' },
    { icon: <BulbOutlined />, key: 'demo.guide.tip2', color: 'green' },
    { icon: <BulbOutlined />, key: 'demo.guide.tip3', color: 'geekblue' },
    { icon: <BulbOutlined />, key: 'demo.guide.tip4', color: 'purple' },
    { icon: <BulbOutlined />, key: 'demo.guide.tip5', color: 'gold' },
    { icon: <BulbOutlined />, key: 'demo.guide.tip6', color: 'cyan' },
    { icon: <BulbOutlined />, key: 'demo.guide.tip7', color: 'orange' },
    { icon: <BulbOutlined />, key: 'demo.guide.tip8', color: 'magenta' },
  ];

  return (
    <div className="demo-float">
      <FloatButton
        icon={<QuestionCircleOutlined />}
        type="primary"
        tooltip={t('demo.guide.tooltip')}
        onClick={() => setOpen(true)}
      />
      <Modal
        title={`🎯 ${t('demo.guide.title')}`}
        open={open}
        onCancel={() => setOpen(false)}
        footer={null}
        width={560}
      >
        <Paragraph type="secondary" style={{ marginBottom: 16 }}>
          {t('demo.guide.desc')}
        </Paragraph>
        <List
          dataSource={tips}
          renderItem={(item) => (
            <List.Item style={{ padding: '8px 0' }}>
              <Space>
                <Tag color={item.color} style={{ borderRadius: 12, margin: 0 }}>{item.icon}</Tag>
                <Text>{t(item.key)}</Text>
              </Space>
            </List.Item>
          )}
        />
        <Paragraph type="secondary" style={{ marginTop: 16, fontSize: 12 }}>
          💡 {t('demo.guide.route')}
        </Paragraph>
      </Modal>
    </div>
  );
}
