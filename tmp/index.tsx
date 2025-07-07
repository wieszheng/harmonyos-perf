import { PageContainer } from '@ant-design/pro-components';

import {
  Button,
  Card,
  Col, Descriptions,
  Form,
  Input,
  message,
  Row,
  Select,
  Steps,
  Tabs,
} from 'antd';
import React, { useState } from 'react';

const { Option } = Select;

const AccessPage: React.FC = () => {
  const [current, setCurrent] = useState(0);
  const [form] = Form.useForm();
  const [taskInfo, setTaskInfo] = useState<any>({});

  const handleChange = (value: string[]) => {
    console.log(`selected ${value}`);
  };

  const next = async () => {
    if (current === 0) {
      try {
        const values = await form.validateFields();
        console.log(values);
        setTaskInfo(values);
        setCurrent(1);
      } catch (e) {
        message.error('请完善任务信息');
      }
    }
    if (current === 1) {
      setCurrent(current + 1);
    }
  };

  const prev = () => {
    setCurrent(current - 1);
  };

  const items = [
    {
      label: '已安装的应用',
      key: 'item-1',
      children: (
        <Form.Item name={['app', 'installedApp']} noStyle>
          <Select placeholder="请选择应用">
            <Option value="app1">应用1</Option>
            <Option value="app2">应用2</Option>
          </Select>
        </Form.Item>
      ),
    },
    {
      label: '安装的新应用',
      key: 'item-2',
      children: (
        <Form.Item name={['app', 'newApp']} noStyle>
          <Select placeholder="请选择应用">
            <Option value="newApp1">新应用1</Option>
            <Option value="newApp2">新应用2</Option>
          </Select>
        </Form.Item>
      ),
    },
  ];
  const formItemLayout = {
    labelCol: {
      xs: { span: 24 },
      sm: { span: 5 },
    },
    wrapperCol: {
      xs: { span: 24 },
      sm: { span: 15 },
    },
  };

  return (
    <PageContainer
      ghost
      header={{
        title: '场景化性能任务',
      }}
    >
      <Card>
        <Steps
          current={current}
          items={[
            {
              title: '创建任务',
            },
            {
              title: '执行测试',
            },
            {
              title: '查看报告',
            },
          ]}
        />
      </Card>
      <Card style={{ marginTop: 20 }}>
        {current === 0 && (
          <Form {...formItemLayout} form={form} layout="horizontal">
            <Form.Item
              label="任务名称"
              name="taskName"
              rules={[{ required: true, message: '请输入任务名称' }]}
            >
              <Input placeholder="请输入任务名称" showCount maxLength={60} />
            </Form.Item>
            <Form.Item label="备注信息" name="remark">
              <Input.TextArea showCount maxLength={100} />
            </Form.Item>
            <Form.Item
              label="测试设备"
              name="device"
              rules={[{ required: true, message: '请选择测试设备' }]}
            >
              <Select placeholder="请选择测试设备">
                <Option value="device1">设备1</Option>
                <Option value="device2">设备2</Option>
              </Select>
            </Form.Item>
            <Form.Item
              label="选择应用"
              name="app"
              required
              rules={[
                {
                  validator(_, value) {
                    const { installedApp, newApp } = value || {};
                    if (!installedApp && !newApp) {
                      return Promise.reject(
                        new Error('请选择已安装或新安装的应用'),
                      );
                    }
                    return Promise.resolve();
                  },
                },
              ]}
            >
              <Tabs defaultActiveKey="1" centered items={items}>
              </Tabs>
            </Form.Item>
            <Form.Item
              label="监控项配置"
              name="monitor"
              initialValue={['cpuFerd', 'cpuUsage', 'mem']}
              rules={[{ required: true, message: '请选择配置项' }]}
            >
              <Select
                mode="multiple"
                placeholder="请选择配置项"
                style={{ width: '100%' }}
                onChange={handleChange}
                maxTagCount={'responsive'}
                options={[
                  {
                    label: 'CPU单核负载',
                    value: 'cpuFerd',
                  },
                  {
                    label: 'CPU频率',
                    value: 'cpuUsage',
                  },
                  {
                    label: '内存',
                    value: 'mem',
                  },
                  {
                    label: '帧率FPS',
                    value: 'fps',
                  },
                  {
                    label: '温度',
                    value: 'temp',
                  },
                  {
                    label: 'GPU',
                    value: 'gpu',
                  },
                ]}
              />
            </Form.Item>

            <Form.Item style={{ marginTop: 120 }}>
              <Row gutter={[8, 8]}>
                <Col span={6} offset={15}>
                  <Button type="primary" block onClick={next}>
                    创建任务
                  </Button>
                </Col>
              </Row>
            </Form.Item>
          </Form>
        )}
        {
          current === 1 && (
            <Row gutter={[8, 8]}>
              <Col span={3} offset={9}>
                <Button onClick={prev} block>停止测试</Button>

              </Col>
              <Col span={3}>
                <Button type="primary" block onClick={next}>查看报告</Button>
              </Col>
            </Row>
          )
        }
        {
          current === 2 && (
            <Row gutter={[8, 8]}>
              <Col span={3} offset={9}>
                <Button type="primary" block />
              </Col>
            </Row>
          )
        }
      </Card>
    </PageContainer>
  );
};

export default AccessPage;
