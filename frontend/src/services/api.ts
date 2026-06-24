import axios from 'axios';
import { useLocaleStore } from '../store/localeStore';

const api = axios.create({ baseURL: '/api', timeout: 30000 });

api.interceptors.request.use(config => {
  const lang = useLocaleStore.getState().locale;
  if (config.params) {
    config.params.lang = lang;
  } else {
    config.params = { lang };
  }
  return config;
});

// ─── Global ───
export const getIndustries = () => api.get('/industries').then(r => r.data);
export const getIndustryData = (id: string) => api.get(`/industry/${id}`).then(r => r.data);
export const switchIndustry = (id: string) => api.post('/industry/switch', { industry_id: id }).then(r => r.data);
export const healthCheck = () => api.get('/health').then(r => r.data);

// ─── DocParser ───
export const getDocTemplates = (industryId?: string) =>
  api.get('/doc-parser/templates', { params: { industry_id: industryId } }).then(r => r.data);
export const demoParse = (templateId: string, industryId?: string) =>
  api.get(`/doc-parser/demo/${templateId}`, { params: { industry_id: industryId } }).then(r => r.data);
export const uploadParse = (file: File, docType?: string, industryId?: string) => {
  const fd = new FormData();
  fd.append('file', file);
  if (docType) fd.append('doc_type', docType);
  if (industryId) fd.append('industry_id', industryId);
  return api.post('/doc-parser/parse', fd).then(r => r.data);
};
export const batchDemoParse = (industryId?: string) =>
  api.get('/doc-parser/batch-demo', { params: { industry_id: industryId } }).then(r => r.data);

// ─── DemandForecast ───
export const getForecastMetrics = (industryId?: string) =>
  api.get('/demand-forecast/metrics', { params: { industry_id: industryId } }).then(r => r.data);
export const getForecastData = (industryId?: string) =>
  api.get('/demand-forecast/data', { params: { industry_id: industryId } }).then(r => r.data);
export const runPredict = (periods = 30, industryId?: string) =>
  api.post('/demand-forecast/predict', { periods, industry_id: industryId }).then(r => r.data);
export const getForecastInsight = (metricKey?: string, industryId?: string) =>
  api.get('/demand-forecast/insight', { params: { metric_key: metricKey, industry_id: industryId } }).then(r => r.data);

// ─── AIAgent ───
export const getAICapabilities = (industryId?: string) =>
  api.get('/ai-agent/capabilities', { params: { industry_id: industryId } }).then(r => r.data);
export const getAIGreeting = (industryId?: string) =>
  api.get('/ai-agent/greeting', { params: { industry_id: industryId } }).then(r => r.data);
export const getAIKnowledge = (industryId?: string) =>
  api.get('/ai-agent/knowledge', { params: { industry_id: industryId } }).then(r => r.data);
export const chatWithAI = (message: string, history: any[] = [], industryId?: string) =>
  api.post('/ai-agent/chat', { message, history, industry_id: industryId }).then(r => r.data);
export const batchGenerate = (type: string, params: any, count = 3, industryId?: string) =>
  api.post('/ai-agent/batch-generate', { generate_type: type, params, count, industry_id: industryId }).then(r => r.data);

// ─── RiskControl ───
export const getRiskLabels = (industryId?: string) =>
  api.get('/risk-control/labels', { params: { industry_id: industryId } }).then(r => r.data);
export const getRiskIndicators = (industryId?: string) =>
  api.get('/risk-control/indicators', { params: { industry_id: industryId } }).then(r => r.data);
export const assessRisk = (industryId?: string) =>
  api.post('/risk-control/assess', { industry_id: industryId }).then(r => r.data);
export const analyzeTransactions = (transactions?: any[], industryId?: string) =>
  api.post('/risk-control/analyze-transactions', { transactions, industry_id: industryId }).then(r => r.data);
export const detectAnomalies = (data?: any[], industryId?: string) =>
  api.post('/risk-control/detect-anomalies', { data, industry_id: industryId }).then(r => r.data);

// ─── ChatBI ───
export const getBITables = (industryId?: string) =>
  api.get('/chatbi/tables', { params: { industry_id: industryId } }).then(r => r.data);
export const queryChatBI = (query: string, tableName = '', industryId?: string) =>
  api.post('/chatbi/query', { query, table_name: tableName, industry_id: industryId }).then(r => r.data);

// ─── Demo Cases ───
export const getDemoCases = (module?: string) =>
  api.get('/demo/cases', { params: { module } }).then(r => r.data);
export const executeDemoCase = (caseId: string, industryId?: string) =>
  api.post('/demo/execute', { case_id: caseId, industry_id: industryId }).then(r => r.data);

// ─── Report Generator ───
export const getIndustryReport = (industryId?: string) =>
  api.get('/report/report', { params: { industry_id: industryId } }).then(r => r.data);
export const getReportsSummary = () =>
  api.get('/report/reports-summary').then(r => r.data);
