# 📊 中美公司财报下载地址汇总表

> 本表汇总了 Streamlit 智能识别系统（P7）涉及的全部 16 家公司、37 个财年的财报数据来源信息。
> - ✅ 美国公司 10 家（31 个财年）：均可通过 SEC EDGAR 自动下载
> - ⚠️ 中国公司 6 家（6 个财年）：均无法自动下载，需人工获取 PDF 后上传

---

## 🇺🇸 美国公司（SEC EDGAR 可下载）

| 公司 | Ticker | 覆盖财年 | SEC EDGAR 搜索链接 |
|------|--------|----------|-------------------|
| **AMD** | AMD | FY2022, FY2023, FY2024 | [搜索 AMD 10-K](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000002488&type=10-K&dateb=&owner=include&count=40&search_text=) |
| **Salesforce** | CRM | FY2023, FY2024, FY2025 | [搜索 CRM 10-K](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001108524&type=10-K&dateb=&owner=include&count=40&search_text=) |
| **Alphabet / Google** | GOOGL | 2022, 2023, 2024 | [搜索 GOOGL 10-K](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=10-K&dateb=&owner=include&count=40&search_text=) |
| **Intel** | INTC | FY2022, FY2023, FY2024 | [搜索 INTC 10-K](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000050863&type=10-K&dateb=&owner=include&count=40&search_text=) |
| **Meta** | META | 2022, 2023, 2024 | [搜索 META 10-K](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001326801&type=10-K&dateb=&owner=include&count=40&search_text=) |
| **Microsoft** | MSFT | FY2023, FY2024, FY2025 | [搜索 MSFT 10-K](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=10-K&dateb=&owner=include&count=40&search_text=) |
| **Micron** | MU | FY2022, FY2023, FY2024 | [搜索 MU 10-K](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000723125&type=10-K&dateb=&owner=include&count=40&search_text=) |
| **NVIDIA** | NVDA | FY2023, FY2024, FY2025 | [搜索 NVDA 10-K](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=10-K&dateb=&owner=include&count=40&search_text=) |
| **Oracle** | ORCL | FY2023, FY2024, FY2025 | [搜索 ORCL 10-K](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001341439&type=10-K&dateb=&owner=include&count=40&search_text=) |
| **Tesla** | TSLA | 2022, 2023, 2024 | [搜索 TSLA 10-K](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001318605&type=10-K&dateb=&owner=include&count=40&search_text=) |

**合计：10 家公司，31 个财年标注数据已就绪。**

---

## 🇨🇳 中国公司（巨潮资讯网，需人工下载）

| 公司 | 代码 | 覆盖财年 | 巨潮资讯网搜索链接 | 备注 |
|------|------|----------|-------------------|------|
| **科大讯飞** | 002230.SZ | FY2024 | [搜索 002230 年报](http://www.cninfo.com.cn/new/information/topSearch/query?keyWord=002230) | ⚠️ 自动下载失败：巨潮 API `hisAnnouncement/query` 返回 0 条公告，已尝试多种参数组合（stock/SECID/column/searchkey）及 Referer/User-Agent 均无效。需人工下载 PDF 后通过系统上传功能导入。 |
| **数据港** | 603881.SH | FY2024 | [搜索 603881 年报](http://www.cninfo.com.cn/new/information/topSearch/query?keyWord=603881) | ⚠️ 同上，自动下载失败。 |
| **寒武纪** | 688256.SH | FY2024 | [搜索 688256 年报](http://www.cninfo.com.cn/new/information/topSearch/query?keyWord=688256) | ⚠️ 同上，自动下载失败。 |
| **浪潮信息** | 000977.SZ | FY2024 | [搜索 000977 年报](http://www.cninfo.com.cn/new/information/topSearch/query?keyWord=000977) | ⚠️ 自动下载失败。**已有 PDF 文件可手动上传至系统。** |
| **中科曙光** | 603019.SH | FY2024 | [搜索 603019 年报](http://www.cninfo.com.cn/new/information/topSearch/query?keyWord=603019) | ⚠️ 同上，自动下载失败。 |
| **奥飞数据** | 300738.SZ | FY2024 | [搜索 300738 年报](http://www.cninfo.com.cn/new/information/topSearch/query?keyWord=300738) | ⚠️ 同上，自动下载失败。 |

**合计：6 家公司，6 个财年标注数据已就绪（均通过上传 PDF 方式完成）。**

---

## 🔧 下载失败原因说明（中国公司）

| 项目 | 详情 |
|------|------|
| **数据源** | 巨潮资讯网（cninfo.com.cn）——中国证监会指定信息披露平台 |
| **API 端点** | `http://www.cninfo.com.cn/new/hisAnnouncement/query` |
| **失败表现** | 无论使用 `stock` / `SECID` / `column` / `searchkey` 哪种参数组合，API 均返回 0 条公告记录 |
| **已尝试方案** | ① 更换参数格式（stock/SECID）；② 添加 Referer 头；③ 添加 User-Agent 头；④ 调整时间范围；⑤ 尝试 POST/GET 方法 |
| **根因分析** | 巨潮资讯网 API 对自动化请求有较严格的反爬/限流机制，或参数接口已变更，导致脚本层面无法稳定获取 |
| **替代方案** | 巨潮资讯网 PDF 直链（`static.cninfo.com.cn/finalpage/...`）仍可访问，但需先知道公告编号才能拼出直链，因此建议人工搜索后下载 |
| **系统支持** | Streamlit 系统 P7 已提供 **"上传 PDF 财报"** 功能，可完美替代自动下载 |

---

## 📁 标注数据存放位置

```
D:/depreciation-risk-detection/data/
├── annotated/          ← 美国公司 10 家 × 31 个财年
│   ├── AMD_FY2022_annotation.json
│   ├── ...
│   └── TSLA_2024_annotation.json
└── annotated_cn/       ← 中国公司 6 家 × 6 个财年（FY2024）
    ├── SH603019_2024_annotation.json
    ├── SH603881_2024_annotation.json
    ├── SH688256_2024_annotation.json
    ├── SZ000977_2024_annotation.json
    ├── SZ002230_2024_annotation.json
    └── SZ300738_2024_annotation.json
```

---

> 📌 **使用提示**：
> 1. 美国公司直接在 P7 界面选择已有公司，系统将自动从 SEC EDGAR 下载 10-K 财报。
> 2. 中国公司请在 P7 界面使用 **"上传 PDF 财报"** 功能，导入本地 PDF 文件。
> 3. 浪潮信息（000977.SZ）已有 PDF，可直接上传。
