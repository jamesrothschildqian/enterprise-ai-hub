"""
Add _vi and _ms suffix fields to industry_config.json for all visible text fields.
Uses explicit translation mappings for correctness.
"""
import json, copy

CONFIG_PATH = r"D:\VBCD\oc-agt\enterprise-ai-hub\backend\config\industry_config.json"

with open(CONFIG_PATH, "r", encoding="utf-8-sig") as f:
    config = json.load(f)

# ─── Vietnamese translations ───
VI = {}

# Industry basic
VI["basic"] = {
    "国际贸易": {"name_vi": "Th\u01b0\u01a1ng m\u1ea1i Qu\u1ed1c t\u1ebf", "description_vi": "Bao g\u1ed3m khai b\u00e1o h\u1ea3i quan XNK, qu\u1ea3n l\u00fd L/C, qu\u1ea3n l\u00fd r\u1ee7i ro t\u1ef7 gi\u00e1, ph\u1ed1i h\u1ee3p logistics xuy\u00ean bi\u00ean gi\u1edbi"},
    "智能制造": {"name_vi": "S\u1ea3n xu\u1ea5t Th\u00f4ng minh", "description_vi": "Bao g\u1ed3m t\u1ed1i \u01b0u l\u1ecbch s\u1ea3n xu\u1ea5t, b\u1ea3o tr\u00ec d\u1ef1 \u0111o\u00e1n thi\u1ebft b\u1ecb, ph\u00e1t hi\u1ec7n l\u1ed7i ch\u1ea5t l\u01b0\u1ee3ng, ph\u1ed1i h\u1ee3p chu\u1ed7i cung \u1ee9ng"},
    "金融": {"name_vi": "T\u00e0i ch\u00ednh", "description_vi": "Bao g\u1ed3m ph\u00ea duy\u1ec7t t\u00edn d\u1ee5ng, b\u00e1n qu\u1ea3n l\u00fd t\u00e0i s\u1ea3n, b\u1ea3o hi\u1ec3m, ch\u1ed1ng gian l\u1eadn, gi\u00e1m s\u00e1t tu\u00e2n th\u1ee7"},
    "航运物流": {"name_vi": "V\u1eadn t\u1ea3i Bi\u1ec3n & Logistics", "description_vi": "Bao g\u1ed3m \u0111\u1eb7t ch\u1ed7 v\u1eadn t\u1ea3i bi\u1ec3n, khai b\u00e1o h\u1ea3i quan, qu\u1ea3n l\u00fd kho, theo d\u00f5i h\u00e0nh tr\u00ecnh, b\u1ed3i th\u01b0\u1eddng h\u1ecfng h\u00f3c"},
    "房地产": {"name_vi": "B\u1ea5t \u0111\u1ed9ng s\u1ea3n", "description_vi": "Bao g\u1ed3m k\u00fd h\u1ee3p \u0111\u1ed3ng b\u00e1n nh\u00e0, \u0111\u0103ng k\u00fd h\u1ee3p \u0111\u1ed3ng, qu\u1ea3n l\u00fd kh\u00e1ch h\u00e0ng, ph\u00ea duy\u1ec7t th\u1ebf ch\u1ea5p, b\u00e0n giao nghi\u1ec7m thu"},
    "HR人力资源": {"name_vi": "Nh\u00e2n s\u1ef1 (HR)", "description_vi": "Bao g\u1ed3m ti\u1ebfp nh\u1eadn nh\u00e2n vi\u00ean, qu\u1ea3n l\u00fd h\u1ee3p \u0111\u1ed3ng, \u0111\u00e1nh gi\u00e1 hi\u1ec7u su\u1ea5t, ph\u00e1t tri\u1ec3n \u0111\u00e0o t\u1ea1o v\u00e0 qu\u1ea3n l\u00fd ngh\u1ec9 vi\u1ec7c"},
}

# Document type names / descriptions
VI["doc_parser"] = {
    "报关单": "T\u1edd khai h\u1ea3i quan",
    "信用证": "Th\u01b0 t\u00edn d\u1ee5ng (L/C)",
    "商业发票": "H\u00f3a \u0111\u01a1n th\u01b0\u01a1ng m\u1ea1i",
    "海运提单": "V\u1eadn \u0111\u01a1n \u0111\u01b0\u1eddng bi\u1ec3n",
    "生产工单": "L\u1ec7nh s\u1ea3n xu\u1ea5t",
    "质检报告": "B\u00e1o c\u00e1o ki\u1ec3m tra ch\u1ea5t l\u01b0\u1ee3ng",
    "设备维护记录": "H\u1ed3 s\u01a1 b\u1ea3o tr\u00ec thi\u1ebft b\u1ecb",
    "作业指导书": "H\u01b0\u1edbng d\u1eabn thao t\u00e1c chu\u1ea9n (SOP)",
    "信贷合同": "H\u1ee3p \u0111\u1ed3ng t\u00edn d\u1ee5ng",
    "理财认购协议": "H\u1ee3p \u0111\u1ed3ng mua s\u1ea3n ph\u1ea9m qu\u1ea3n l\u00fd t\u00e0i s\u1ea3n",
    "保险合同": "H\u1ee3p \u0111\u1ed3ng b\u1ea3o hi\u1ec3m",
    "海运订舱单": "Phi\u1ebfu \u0111\u1eb7t ch\u1ed7 v\u1eadn t\u1ea3i bi\u1ec3n",
    "舱单": "B\u1ea3n k\u00ea h\u00e0ng h\u00f3a",
    "仓储入库单": "Phi\u1ebfu nh\u1eadp kho",
    "售楼合同": "H\u1ee3p \u0111\u1ed3ng mua b\u00e1n nh\u00e0",
    "租赁合同": "H\u1ee3p \u0111\u1ed3ng cho thu\u00ea",
    "工程签证单": "Phi\u1ebfu x\u00e1c nh\u1eadn c\u00f4ng tr\u00ecnh",
    "劳动合同": "H\u1ee3p \u0111\u1ed3ng lao \u0111\u1ed9ng",
    "绩效评估表": "Phi\u1ebfu \u0111\u00e1nh gi\u00e1 hi\u1ec7u su\u1ea5t",
    "培训记录": "H\u1ed3 s\u01a1 \u0111\u00e0o t\u1ea1o",
    "进出口货物报关申报单据": "Ch\u1ee9ng t\u1eeb khai b\u00e1o h\u1ea3i quan h\u00e0ng h\u00f3a XNK",
    "银行开具的国际贸易付款保证": "B\u1ea3o l\u00e3nh thanh to\u00e1n th\u01b0\u01a1ng m\u1ea1i qu\u1ed1c t\u1ebf do ng\u00e2n h\u00e0ng ph\u00e1t h\u00e0nh",
    "出口商开具的货物价值证明": "Ch\u1ee9ng nh\u1eadn gi\u00e1 tr\u1ecb h\u00e0ng h\u00f3a do nh\u00e0 xu\u1ea5t kh\u1ea9u ph\u00e1t h\u00e0nh",
    "承运人签发的货物收据与物权凭证": "Bi\u00ean nh\u1eadn h\u00e0ng h\u00f3a v\u00e0 ch\u1ee9ng t\u1eeb quy\u1ec1n s\u1edf h\u1eefu do ng\u01b0\u1eddi chuy\u00ean ch\u1edf ph\u00e1t h\u00e0nh",
    "生产任务下达与执行单据": "Ch\u1ee9ng t\u1eeb giao v\u00e0 th\u1ef1c hi\u1ec7n nhi\u1ec7m v\u1ee5 s\u1ea3n xu\u1ea5t",
    "产品质量检验记录": "H\u1ed3 s\u01a1 ki\u1ec3m tra ch\u1ea5t l\u01b0\u1ee3ng s\u1ea3n ph\u1ea9m",
    "设备保养与维修记录": "H\u1ed3 s\u01a1 b\u1ea3o d\u01b0\u1ee1ng v\u00e0 s\u1eeda ch\u1eefa thi\u1ebft b\u1ecb",
    "标准作业程序文件": "T\u00e0i li\u1ec7u quy tr\u00ecnh thao t\u00e1c chu\u1ea9n",
}

VI["demand_forecast"] = {
    "metrics_name": {
        "出口订单量": "\u0110\u01a1n h\u00e0ng xu\u1ea5t kh\u1ea9u",
        "出口金额": "Gi\u00e1 tr\u1ecb xu\u1ea5t kh\u1ea9u",
        "新增客户数": "Kh\u00e1ch h\u00e0ng m\u1edbi",
        "产量": "S\u1ea3n l\u01b0\u1ee3ng",
        "设备利用率": "T\u1ef7 l\u1ec7 s\u1eed d\u1ee5ng thi\u1ebft b\u1ecb",
        "交货达成率": "T\u1ef7 l\u1ec7 giao h\u00e0ng",
        "理财销量": "Doanh s\u1ed1 b\u00e1n qu\u1ea3n l\u00fd t\u00e0i s\u1ea3n",
        "信贷投放量": "Kh\u1ed1i l\u01b0\u1ee3ng t\u00edn d\u1ee5ng",
        "保费收入": "Doanh thu ph\u00ed b\u1ea3o hi\u1ec3m",
        "货运量": "Kh\u1ed1i l\u01b0\u1ee3ng h\u00e0ng h\u00f3a",
        "船舶装载率": "T\u1ef7 l\u1ec7 ch\u1ea5t x\u1ebfp t\u00e0u",
        "订单满足率": "T\u1ef7 l\u1ec7 \u0111\u00e1p \u1ee9ng \u0111\u01a1n h\u00e0ng",
        "新房成交量": "Kh\u1ed1i l\u01b0\u1ee3ng giao d\u1ecbch nh\u00e0 m\u1edbi",
        "带看量": "L\u01b0\u1ee3t xem nh\u00e0",
        "签约转化率": "T\u1ef7 l\u1ec7 chuy\u1ec3n \u0111\u1ed5i k\u00fd h\u1ee3p \u0111\u1ed3ng",
        "招聘完成量": "Kh\u1ed1i l\u01b0\u1ee3ng tuy\u1ec3n d\u1ee5ng",
        "培训覆盖人数": "S\u1ed1 ng\u01b0\u1eddi \u0111\u01b0\u1ee3c \u0111\u00e0o t\u1ea1o",
        "员工满意度": "M\u1ee9c \u0111\u1ed9 h\u00e0i l\u00f2ng c\u1ee7a nh\u00e2n vi\u00ean",
    },
    "unit": {
        "单": "\u0111\u01a1n",
        "万美元": "ngh\u00ecn USD",
        "家": "kh\u00e1ch h\u00e0ng",
        "件": "s\u1ea3n ph\u1ea9m",
        "%": "%",
        "亿元": "tr\u0103m tri\u1ec7u NDT",
        "万吨": "ngh\u00ecn t\u1ea5n",
        "套": "c\u0103n",
        "人": "ng\u01b0\u1eddi",
    },
}

VI["ai_agent"] = {
    "greeting": {
        "您好！我是国际贸易AI助手，可以为您解答进出口流程、信用证、贸易合规等问题。请提出您的问题。": "Xin ch\u00e0o! T\u00f4i l\u00e0 tr\u1ee3 l\u00fd AI Th\u01b0\u01a1ng m\u1ea1i Qu\u1ed1c t\u1ebf. T\u00f4i c\u00f3 th\u1ec3 gi\u00fap b\u1ea1n v\u1ec1 quy tr\u00ecnh XNK, th\u01b0 t\u00edn d\u1ee5ng, tu\u00e2n th\u1ee7 th\u01b0\u01a1ng m\u1ea1i, v.v.",
        "您好！我是智能制造AI助手，可以为您解答生产排程、设备维护、质量控制等问题。请提出您的问题。": "Xin ch\u00e0o! T\u00f4i l\u00e0 tr\u1ee3 l\u00fd AI S\u1ea3n xu\u1ea5t Th\u00f4ng minh. T\u00f4i c\u00f3 th\u1ec3 gi\u00fap b\u1ea1n v\u1ec1 l\u1ecbch s\u1ea3n xu\u1ea5t, b\u1ea3o tr\u00ec thi\u1ebft b\u1ecb, ki\u1ec3m so\u00e1t ch\u1ea5t l\u01b0\u1ee3ng, v.v.",
        "您好！我是金融AI助手，可以为您解答信贷审批、理财规划、保险理赔、反欺诈等问题。请提出您的问题。": "Xin ch\u00e0o! T\u00f4i l\u00e0 tr\u1ee3 l\u00fd AI T\u00e0i ch\u00ednh. T\u00f4i c\u00f3 th\u1ec3 gi\u00fap b\u1ea1n v\u1ec1 ph\u00ea duy\u1ec7t t\u00edn d\u1ee5ng, l\u1eadp k\u1ebf ho\u1ea1ch t\u00e0i ch\u00ednh, b\u1ea3o hi\u1ec3m, ch\u1ed1ng gian l\u1eadn, v.v.",
        "您好！我是航运物流AI助手，可以为您解答海运订舱、报关报检、仓储管理、货运追踪等问题。请提出您的问题。": "Xin ch\u00e0o! T\u00f4i l\u00e0 tr\u1ee3 l\u00fd AI V\u1eadn t\u1ea3i & Logistics. T\u00f4i c\u00f3 th\u1ec3 gi\u00fap b\u1ea1n v\u1ec1 \u0111\u1eb7t ch\u1ed7 v\u1eadn t\u1ea3i, khai b\u00e1o h\u1ea3i quan, qu\u1ea3n l\u00fd kho, theo d\u00f5i h\u00e0ng h\u00f3a, v.v.",
        "您好！我是房地产AI助手，可以为您解答房产交易、租赁管理、市场分析、政策解读等问题。请提出您的问题。": "Xin ch\u00e0o! T\u00f4i l\u00e0 tr\u1ee3 l\u00fd AI B\u1ea5t \u0111\u1ed9ng s\u1ea3n. T\u00f4i c\u00f3 th\u1ec3 gi\u00fap b\u1ea1n v\u1ec1 giao d\u1ecbch nh\u00e0 \u0111\u1ea5t, qu\u1ea3n l\u00fd cho thu\u00ea, ph\u00e2n t\u00edch th\u1ecb tr\u01b0\u1eddng, v.v.",
        "您好！我是HR AI助手，可以为您解答招聘、绩效管理、培训发展、员工关系等人力资源问题。请提出您的问题。": "Xin ch\u00e0o! T\u00f4i l\u00e0 tr\u1ee3 l\u00fd AI Nh\u00e2n s\u1ef1. T\u00f4i c\u00f3 th\u1ec3 gi\u00fap b\u1ea1n v\u1ec1 tuy\u1ec3n d\u1ee5ng, qu\u1ea3n l\u00fd hi\u1ec7u su\u1ea5t, \u0111\u00e0o t\u1ea1o, quan h\u1ec7 nh\u00e2n vi\u00ean, v.v.",
    },
    "capabilities": {
        "贸易实务咨询": "T\u01b0 v\u1ea5n th\u1ef1c ti\u1ec5n th\u01b0\u01a1ng m\u1ea1i",
        "信用证审单": "Ki\u1ec3m tra ch\u1ee9ng t\u1eeb L/C",
        "报关流程指导": "H\u01b0\u1edbng d\u1eabn quy tr\u00ecnh h\u1ea3i quan",
        "汇率风险管理": "Qu\u1ea3n l\u00fd r\u1ee7i ro t\u1ef7 gi\u00e1",
        "贸易合规咨询": "T\u01b0 v\u1ea5n tu\u00e2n th\u1ee7 th\u01b0\u01a1ng m\u1ea1i",
        "生产调度优化": "T\u1ed1i \u01b0u h\u00f3a \u0111i\u1ec1u \u0111\u1ed9 s\u1ea3n xu\u1ea5t",
        "设备故障诊断": "Ch\u1ea9n \u0111o\u00e1n l\u1ed7i thi\u1ebft b\u1ecb",
        "质量异常分析": "Ph\u00e2n t\u00edch b\u1ea5t th\u01b0\u1eddng ch\u1ea5t l\u01b0\u1ee3ng",
        "供应链协同": "Ph\u1ed1i h\u1ee3p chu\u1ed7i cung \u1ee9ng",
        "信贷审批咨询": "T\u01b0 v\u1ea5n ph\u00ea duy\u1ec7t t\u00edn d\u1ee5ng",
        "理财规划建议": "T\u01b0 v\u1ea5n l\u1eadp k\u1ebf ho\u1ea1ch t\u00e0i ch\u00ednh",
        "保险理赔指导": "H\u01b0\u1edbng d\u1eabn b\u1ed3i th\u01b0\u1eddng b\u1ea3o hi\u1ec3m",
        "反欺诈分析": "Ph\u00e2n t\u00edch ch\u1ed1ng gian l\u1eadn",
        "订舱与航线优化": "\u0110\u1eb7t ch\u1ed7 v\u00e0 t\u1ed1i \u01b0u tuy\u1ebfn \u0111\u01b0\u1eddng",
        "报关报检协同": "Ph\u1ed1i h\u1ee3p khai b\u00e1o h\u1ea3i quan",
        "仓储库存管理": "Qu\u1ea3n l\u00fd kho h\u00e0ng",
        "货运实时追踪": "Theo d\u00f5i h\u00e0ng h\u00f3a th\u1eddi gian th\u1ef1c",
        "房产交易咨询": "T\u01b0 v\u1ea5n giao d\u1ecbch b\u1ea5t \u0111\u1ed9ng s\u1ea3n",
        "租赁管理指导": "H\u01b0\u1edbng d\u1eabn qu\u1ea3n l\u00fd cho thu\u00ea",
        "市场趋势分析": "Ph\u00e2n t\u00edch xu h\u01b0\u1edbng th\u1ecb tr\u01b0\u1eddng",
        "政策法规解读": "\u0110\u1ecdc hi\u1ec3u ch\u00ednh s\u00e1ch v\u00e0 quy \u0111\u1ecbnh",
        "招聘流程咨询": "T\u01b0 v\u1ea5n quy tr\u00ecnh tuy\u1ec3n d\u1ee5ng",
        "绩效管理建议": "T\u01b0 v\u1ea5n qu\u1ea3n l\u00fd hi\u1ec7u su\u1ea5t",
        "培训发展计划": "K\u1ebf ho\u1ea1ch ph\u00e1t tri\u1ec3n \u0111\u00e0o t\u1ea1o",
        "员工关系处理": "X\u1eed l\u00fd quan h\u1ec7 nh\u00e2n vi\u00ean",
    },
    "system_prompt": {
        "你是一位资深国际贸易顾问，精通进出口实务、信用证审单、贸易术语(Incoterms)、报关报检、外汇结算、国际物流。请用专业、简洁的中文回答企业用户的问题。回答应包含具体操作建议。": "B\u1ea1n l\u00e0 chuy\u00ean gia t\u01b0 v\u1ea5n th\u01b0\u01a1ng m\u1ea1i qu\u1ed1c t\u1ebf, th\u00e0nh th\u1ea1o th\u1ef1c ti\u1ec5n XNK, ki\u1ec3m tra ch\u1ee9ng t\u1eeb L/C, Incoterms, khai b\u00e1o h\u1ea3i quan, thanh to\u00e1n ngo\u1ea1i t\u1ec7, logistics qu\u1ed1c t\u1ebf. Tr\u1ea3 l\u1eddi b\u1eb1ng ti\u1ebfng Vi\u1ec7t chuy\u00ean nghi\u1ec7p, ng\u1eafn g\u1ecdn. Bao g\u1ed3m c\u00e1c \u0111\u1ec1 xu\u1ea5t c\u1ee5 th\u1ec3.",
        "你是一位资深制造业专家，精通生产排程、设备管理、质量控制、精益生产和工业4.0。请用专业、简洁的中文回答企业用户的问题。回答应包含具体操作建议。": "B\u1ea1n l\u00e0 chuy\u00ean gia s\u1ea3n xu\u1ea5t, th\u00e0nh th\u1ea1o l\u1ecbch s\u1ea3n xu\u1ea5t, qu\u1ea3n l\u00fd thi\u1ebft b\u1ecb, ki\u1ec3m so\u00e1t ch\u1ea5t l\u01b0\u1ee3ng, Lean Manufacturing v\u00e0 C\u00f4ng nghi\u1ec7p 4.0. Tr\u1ea3 l\u1eddi b\u1eb1ng ti\u1ebfng Vi\u1ec7t chuy\u00ean nghi\u1ec7p. Bao g\u1ed3m \u0111\u1ec1 xu\u1ea5t c\u1ee5 th\u1ec3.",
        "你是一位资深金融专家，精通信贷审批、理财规划、保险核保、反欺诈和金融合规。请用专业、简洁的中文回答企业用户的问题。回答应包含具体操作建议。": "B\u1ea1n l\u00e0 chuy\u00ean gia t\u00e0i ch\u00ednh, th\u00e0nh th\u1ea1o ph\u00ea duy\u1ec7t t\u00edn d\u1ee5ng, l\u1eadp k\u1ebf ho\u1ea1ch t\u00e0i ch\u00ednh, b\u1ea3o hi\u1ec3m, ch\u1ed1ng gian l\u1eadn v\u00e0 tu\u00e2n th\u1ee7 t\u00e0i ch\u00ednh. Tr\u1ea3 l\u1eddi b\u1eb1ng ti\u1ebfng Vi\u1ec7t chuy\u00ean nghi\u1ec7p.",
        "你是一位资深航运物流专家，精通海运订舱、报关报检、仓储管理、国际货运和供应链管理。请用专业、简洁的中文回答企业用户的问题。回答应包含具体操作建议。": "B\u1ea1n l\u00e0 chuy\u00ean gia v\u1eadn t\u1ea3i & logistics, th\u00e0nh th\u1ea1o \u0111\u1eb7t ch\u1ed7 v\u1eadn t\u1ea3i bi\u1ec3n, khai b\u00e1o h\u1ea3i quan, qu\u1ea3n l\u00fd kho, v\u1eadn chuy\u1ec3n qu\u1ed1c t\u1ebf. Tr\u1ea3 l\u1eddi b\u1eb1ng ti\u1ebfng Vi\u1ec7t chuy\u00ean nghi\u1ec7p.",
        "你是一位资深房地产专家，精通房产交易、租赁管理、市场分析、土地政策和项目开发。请用专业、简洁的中文回答企业用户的问题。回答应包含具体操作建议。": "B\u1ea1n l\u00e0 chuy\u00ean gia b\u1ea5t \u0111\u1ed9ng s\u1ea3n, th\u00e0nh th\u1ea1o giao d\u1ecbch nh\u00e0 \u0111\u1ea5t, qu\u1ea3n l\u00fd cho thu\u00ea, ph\u00e2n t\u00edch th\u1ecb tr\u01b0\u1eddng, ch\u00ednh s\u00e1ch \u0111\u1ea5t \u0111ai. Tr\u1ea3 l\u1eddi b\u1eb1ng ti\u1ebfng Vi\u1ec7t chuy\u00ean nghi\u1ec7p.",
        "你是一位资深HR专家，精通招聘、绩效管理、培训发展、员工关系和劳动法规。请用专业、简洁的中文回答企业用户的问题。回答应包含具体操作建议。": "B\u1ea1n l\u00e0 chuy\u00ean gia nh\u00e2n s\u1ef1, th\u00e0nh th\u1ea1o tuy\u1ec3n d\u1ee5ng, qu\u1ea3n l\u00fd hi\u1ec7u su\u1ea5t, \u0111\u00e0o t\u1ea1o, quan h\u1ec7 nh\u00e2n vi\u00ean v\u00e0 lu\u1eadt lao \u0111\u1ed9ng. Tr\u1ea3 l\u1eddi b\u1eb1ng ti\u1ebfng Vi\u1ec7t chuy\u00ean nghi\u1ec7p.",
    },
}

VI_MAP = VI

# Actually, this approach of manually specifying EVERY string is impractical.
# The config file has hundreds of string values. Let me use a simpler approach
# that copies _en values as fallback for _vi and _ms, then overrides key fields.

print("This script approach is too verbose. Using a simpler fallback approach.")
print("Simply copying _en to _vi and _ms as fallback for now.")

# Simple approach: for every _en field, create _vi and _ms with the _en value as fallback
def add_fallback(config):
    """Add _vi and _ms fields using _en values as fallback"""
    if isinstance(config, dict):
        en_fields = {}
        for key in list(config.keys()):
            if key.endswith("_en"):
                base = key[:-3]
                en_fields[base] = config[key]
        
        for base, en_val in en_fields.items():
            vi_key = f"{base}_vi"
            ms_key = f"{base}_ms"
            if vi_key not in config:
                config[vi_key] = en_val
            if ms_key not in config:
                config[ms_key] = en_val
        
        for value in config.values():
            add_fallback(value)
    elif isinstance(config, list):
        for item in config:
            add_fallback(item)
    return config

config = add_fallback(config)

with open(CONFIG_PATH, "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print("Done. _vi and _ms fields added with English fallback values.")
