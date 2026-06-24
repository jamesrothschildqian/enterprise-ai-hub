"""Generate _vi.json and _ms.json from _en.json with per-industry translations"""
import json, os, copy

MOCK_DIR = r"D:\VBCD\oc-agt\enterprise-ai-hub\backend\config\mock_data"

# Industry-level translations for KBA, document content, and risk descriptions
TRANSLATIONS = {}

# === VIETNAMESE ===
TRANSLATIONS["vi"] = {
  "smart_manufacturing": {
    "doc_titles": {
      "Production Order PO-2024-1120": "L\u1ec7nh s\u1ea3n xu\u1ea5t PO-2024-1120",
      "QC Report QC-2024-886": "B\u00e1o c\u00e1o ki\u1ec3m tra QC-2024-886",
      "Equipment Maintenance Record MC-001": "H\u1ed3 s\u01a1 b\u1ea3o tr\u00ec thi\u1ebft b\u1ecb MC-001",
    },
    "kb_qa": {
      "How to improve equipment OEE?": "L\u00e0m th\u1ebf n\u00e0o \u0111\u1ec3 c\u1ea3i thi\u1ec7n OEE thi\u1ebft b\u1ecb?",
      "What is Digital Twin?": "Digital Twin l\u00e0 g\u00ec?",
      "Difference between Lean Manufacturing and Six Sigma?": "Kh\u00e1c bi\u1ec7t gi\u1eefa Lean Manufacturing v\u00e0 Six Sigma?",
      "How to choose SPC control charts?": "L\u00e0m th\u1ebf n\u00e0o \u0111\u1ec3 ch\u1ecdn bi\u1ec3u \u0111\u1ed3 ki\u1ec3m so\u00e1t SPC?",
    },
  },
  "international_trade": {
    "doc_titles": {
      "Import Customs Declaration CD-2024-1122": "T\u1edd khai h\u1ea3i quan nh\u1eadp kh\u1ea9u CD-2024-1122",
      "Export Customs Declaration CD-2024-1123": "T\u1edd khai h\u1ea3i quan xu\u1ea5t kh\u1ea9u CD-2024-1123",
      "Certificate of Origin CO-2024-1125": "Gi\u1ea5y ch\u1ee9ng nh\u1eadn xu\u1ea5t x\u1ee9 CO-2024-1125",
    },
    "kb_qa": {
      "What are the latest Incoterms 2024 changes?": "Nh\u1eefng thay \u0111\u1ed5i m\u1edbi nh\u1ea5t c\u1ee7a Incoterms 2024 l\u00e0 g\u00ec?",
      "How to handle cross-border data compliance?": "L\u00e0m th\u1ebf n\u00e0o \u0111\u1ec3 tu\u00e2n th\u1ee7 d\u1eef li\u1ec7u xuy\u00ean bi\u00ean gi\u1edbi?",
      "What are key documents for L/C payment?": "C\u00e1c t\u00e0i li\u1ec7u ch\u00ednh cho thanh to\u00e1n L/C l\u00e0 g\u00ec?",
      "How to manage exchange rate risk?": "L\u00e0m th\u1ebf n\u00e0o \u0111\u1ec3 qu\u1ea3n l\u00fd r\u1ee7i ro t\u1ef7 gi\u00e1?",
    },
  },
  "finance": {
    "doc_titles": {
      "Loan Application LA-2024-1025": "\u0110\u01a1n vay v\u1ed1n LA-2024-1025",
      "Wealth Management Subscription Agreement": "H\u1ee3p \u0111\u1ed3ng mua s\u1ea3n ph\u1ea9m qu\u1ea3n l\u00fd t\u00e0i s\u1ea3n",
      "Risk Warning Letter": "Th\u01b0 c\u1ea3nh b\u00e1o r\u1ee7i ro",
    },
    "kb_qa": {
      "What are the KYC requirements for new accounts?": "Y\u00eau c\u1ea7u KYC cho t\u00e0i kho\u1ea3n m\u1edbi l\u00e0 g\u00ec?",
      "How to identify suspicious transactions?": "L\u00e0m th\u1ebf n\u00e0o \u0111\u1ec3 x\u00e1c \u0111\u1ecbnh giao d\u1ecbch \u0111\u00e1ng ng\u1edd?",
      "What is the AML compliance process?": "Quy tr\u00ecnh tu\u00e2n th\u1ee7 AML l\u00e0 g\u00ec?",
      "How to evaluate credit risk?": "L\u00e0m th\u1ebf n\u00e0o \u0111\u1ec3 \u0111\u00e1nh gi\u00e1 r\u1ee7i ro t\u00edn d\u1ee5ng?",
    },
  },
  "shipping_logistics": {
    "doc_titles": {
      "Bill of Lading BL-2024-1118": "V\u1eadn \u0111\u01a1n \u0111\u01b0\u1eddng bi\u1ec3n BL-2024-1118",
      "Cargo Manifest CM-2024-1119": "B\u1ea3n k\u00ea h\u00e0ng h\u00f3a CM-2024-1119",
      "Warehouse Receipt WR-2024-1120": "Bi\u00ean nh\u1eadn kho WR-2024-1120",
    },
    "kb_qa": {
      "What are the key factors affecting shipping costs?": "C\u00e1c y\u1ebfu t\u1ed1 ch\u00ednh \u1ea3nh h\u01b0\u1edfng \u0111\u1ebfn chi ph\u00ed v\u1eadn chuy\u1ec3n?",
      "How to optimize container loading?": "L\u00e0m th\u1ebf n\u00e0o \u0111\u1ec3 t\u1ed1i \u01b0u h\u00f3a x\u1ebfp container?",
      "What is the Incoterms responsibility split?": "Ph\u00e2n chia tr\u00e1ch nhi\u1ec7m Incoterms nh\u01b0 th\u1ebf n\u00e0o?",
      "How to track cargo in real time?": "L\u00e0m th\u1ebf n\u00e0o \u0111\u1ec3 theo d\u00f5i h\u00e0ng h\u00f3a theo th\u1eddi gian th\u1ef1c?",
    },
  },
  "real_estate": {
    "doc_titles": {
      "Sales Contract SC-2024-1101": "H\u1ee3p \u0111\u1ed3ng mua b\u00e1n SC-2024-1101",
      "Lease Agreement LS-2024-1102": "H\u1ee3p \u0111\u1ed3ng cho thu\u00ea LS-2024-1102",
      "Property Appraisal Report AR-2024-1103": "B\u00e1o c\u00e1o th\u1ea9m \u0111\u1ecbnh gi\u00e1 AR-2024-1103",
    },
    "kb_qa": {
      "How to calculate property ROI?": "C\u00e1ch t\u00ednh ROI b\u1ea5t \u0111\u1ed9ng s\u1ea3n?",
      "What affects property valuation?": "Y\u1ebfu t\u1ed1 n\u00e0o \u1ea3nh h\u01b0\u1edfng \u0111\u1ebfn \u0111\u1ecbnh gi\u00e1 b\u1ea5t \u0111\u1ed9ng s\u1ea3n?",
      "How to conduct due diligence?": "C\u00e1ch th\u1ef1c hi\u1ec7n th\u1ea9m \u0111\u1ecbnh ph\u00e1p l\u00fd?",
      "What are the key lease clauses?": "C\u00e1c \u0111i\u1ec1u kho\u1ea3n ch\u00ednh trong h\u1ee3p \u0111\u1ed3ng thu\u00ea?",
    },
  },
  "hr": {
    "doc_titles": {
      "Employment Contract EC-2024-1001": "H\u1ee3p \u0111\u1ed3ng lao \u0111\u1ed9ng EC-2024-1001",
      "Performance Review PR-2024-1002": "\u0110\u00e1nh gi\u00e1 hi\u1ec7u su\u1ea5t PR-2024-1002",
      "Training Record TR-2024-1003": "H\u1ed3 s\u01a1 \u0111\u00e0o t\u1ea1o TR-2024-1003",
    },
    "kb_qa": {
      "How to conduct effective performance reviews?": "C\u00e1ch th\u1ef1c hi\u1ec7n \u0111\u00e1nh gi\u00e1 hi\u1ec7u su\u1ea5t hi\u1ec7u qu\u1ea3?",
      "What are the best recruitment practices?": "C\u00e1c ph\u01b0\u01a1ng ph\u00e1p tuy\u1ec3n d\u1ee5ng t\u1ed1t nh\u1ea5t?",
      "How to handle employee grievances?": "C\u00e1ch x\u1eed l\u00fd khi\u1ebfu n\u1ea1i c\u1ee7a nh\u00e2n vi\u00ean?",
      "What is the offboarding process?": "Quy tr\u00ecnh ngh\u1ec9 vi\u1ec7c l\u00e0 g\u00ec?",
    },
  },
}

# === MALAY ===
TRANSLATIONS["ms"] = {
  "smart_manufacturing": {
    "doc_titles": {
      "Production Order PO-2024-1120": "Perintah Pengeluaran PO-2024-1120",
      "QC Report QC-2024-886": "Laporan Kawalan Kualiti QC-2024-886",
      "Equipment Maintenance Record MC-001": "Rekod Penyelenggaraan Peralatan MC-001",
    },
    "kb_qa": {
      "How to improve equipment OEE?": "Bagaimana meningkatkan OEE peralatan?",
      "What is Digital Twin?": "Apakah Digital Twin?",
      "Difference between Lean Manufacturing and Six Sigma?": "Perbezaan antara Lean Manufacturing dan Six Sigma?",
      "How to choose SPC control charts?": "Bagaimana memilih carta kawalan SPC?",
    },
  },
  "international_trade": {
    "doc_titles": {
      "Import Customs Declaration CD-2024-1122": "Pengisytiharan Kastam Import CD-2024-1122",
      "Export Customs Declaration CD-2024-1123": "Pengisytiharan Kastam Eksport CD-2024-1123",
      "Certificate of Origin CO-2024-1125": "Sijil Asal CO-2024-1125",
    },
    "kb_qa": {
      "What are the latest Incoterms 2024 changes?": "Apakah perubahan terkini Incoterms 2024?",
      "How to handle cross-border data compliance?": "Bagaimana menguruskan pematuhan data rentas sempadan?",
      "What are key documents for L/C payment?": "Apakah dokumen utama untuk pembayaran L/C?",
      "How to manage exchange rate risk?": "Bagaimana menguruskan risiko kadar pertukaran?",
    },
  },
  "finance": {
    "doc_titles": {
      "Loan Application LA-2024-1025": "Permohonan Pinjaman LA-2024-1025",
      "Wealth Management Subscription Agreement": "Perjanjian Langganan Pengurusan Kekayaan",
      "Risk Warning Letter": "Surat Amaran Risiko",
    },
    "kb_qa": {
      "What are the KYC requirements for new accounts?": "Apakah keperluan KYC untuk akaun baru?",
      "How to identify suspicious transactions?": "Bagaimana mengenal pasti transaksi mencurigakan?",
      "What is the AML compliance process?": "Apakah proses pematuhan AML?",
      "How to evaluate credit risk?": "Bagaimana menilai risiko kredit?",
    },
  },
  "shipping_logistics": {
    "doc_titles": {
      "Bill of Lading BL-2024-1118": "Bil Muatan BL-2024-1118",
      "Cargo Manifest CM-2024-1119": "Manifes Kargo CM-2024-1119",
      "Warehouse Receipt WR-2024-1120": "Resit Gudang WR-2024-1120",
    },
    "kb_qa": {
      "What are the key factors affecting shipping costs?": "Apakah faktor utama yang mempengaruhi kos penghantaran?",
      "How to optimize container loading?": "Bagaimana mengoptimumkan pemuatan kontena?",
      "What is the Incoterms responsibility split?": "Apakah pembahagian tanggungjawab Incoterms?",
      "How to track cargo in real time?": "Bagaimana menjejak kargo secara masa nyata?",
    },
  },
  "real_estate": {
    "doc_titles": {
      "Sales Contract SC-2024-1101": "Kontrak Jualan SC-2024-1101",
      "Lease Agreement LS-2024-1102": "Perjanjian Pajakan LS-2024-1102",
      "Property Appraisal Report AR-2024-1103": "Laporan Penilaian Harta AR-2024-1103",
    },
    "kb_qa": {
      "How to calculate property ROI?": "Bagaimana mengira ROI hartanah?",
      "What affects property valuation?": "Apa yang mempengaruhi penilaian hartanah?",
      "How to conduct due diligence?": "Bagaimana menjalankan due diligence?",
      "What are the key lease clauses?": "Apakah klausa utama pajakan?",
    },
  },
  "hr": {
    "doc_titles": {
      "Employment Contract EC-2024-1001": "Kontrak Pekerjaan EC-2024-1001",
      "Performance Review PR-2024-1002": "Semakan Prestasi PR-2024-1002",
      "Training Record TR-2024-1003": "Rekod Latihan TR-2024-1003",
    },
    "kb_qa": {
      "How to conduct effective performance reviews?": "Bagaimana menjalankan semakan prestasi yang berkesan?",
      "What are the best recruitment practices?": "Apakah amalan pengambilan terbaik?",
      "How to handle employee grievances?": "Bagaimana mengendalikan rungutan pekerja?",
      "What is the offboarding process?": "Apakah proses offboarding?",
    },
  },
}

def translate_doc(doc, lang, industry):
    """Translate document title and simple fields"""
    t = TRANSLATIONS[lang].get(industry, {})
    titles = t.get("doc_titles", {})
    if doc.get("title") in titles:
        doc["title"] = titles[doc["title"]]
    return doc

def translate_kb(kb, lang, industry):
    """Translate knowledge base Q&A"""
    t = TRANSLATIONS[lang].get(industry, {})
    qa = t.get("kb_qa", {})
    if kb.get("question") in qa:
        kb["question"] = qa[kb["question"]]
    return kb

def process_file(industry, lang_code):
    en_path = os.path.join(MOCK_DIR, f"{industry}_en.json")
    with open(en_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    # Translate documents
    docs = data.get("doc_parser", {}).get("documents", [])
    for doc in docs:
        translate_doc(doc, lang_code, industry)
    
    # Translate KBA
    kb_list = data.get("ai_agent", {}).get("knowledge_base", [])
    for kb in kb_list:
        translate_kb(kb, lang_code, industry)

    out_path = os.path.join(MOCK_DIR, f"{industry}_{lang_code}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Created {out_path}")

def main():
    industries = ["smart_manufacturing", "international_trade", "finance", "shipping_logistics", "real_estate", "hr"]
    for ind in industries:
        process_file(ind, "vi")
        process_file(ind, "ms")

if __name__ == "__main__":
    main()
