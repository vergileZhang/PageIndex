# 2025 年以后 RAG 文档检索论文实验指标调研

调研日期：2026-07-09
范围：2025-01-01 以后，围绕 RAG、文档检索、文档问答、多文档/长文档检索、多模态文档 RAG、领域 RAG benchmark 的论文与预印本。
重点：只整理能在论文页面、摘要或可访问 PDF 中确认实验指标的工作。

## 一句话结论

2025 年以后 RAG 文档检索实验的指标体系基本分成五类：

1. 检索端：Recall@k、Hit@k、MRR、nDCG、MAP/mAP、Precision@k 最常见。
2. 生成端：Exact Match、Accuracy、F1、ROUGE-L、BLEU、METEOR、BERTScore、Number Match 常见。
3. 可信性与 RAG 专属质量：Faithfulness、answer relevancy、contextual precision/recall、context relevance、hallucination rate、answer coverage、correctness。
4. 长文档/多文档覆盖：coverage、ranked coverage、density、alpha-nDCG、SecCov@k、CS Recall、answer-in-context。
5. 工程效率：latency、token cost、compression ratio、retrieval rate、index/update cost、bootstrap significance。

## 指标分类速查

| 目标 | 常用指标 | 适用场景 |
|---|---|---|
| 找没找到证据 | Recall@k, Hit@k, All@K | QA、法律、医学、企业文档、multi-hop RAG |
| 证据排得靠不靠前 | MRR, MRR@k, nDCG@k, MAP, P@1 | reranker、hybrid retrieval、citation retrieval |
| 返回结果是否干净 | Precision@k, contextual precision, false positive rate | 噪声敏感 RAG、短上下文 RAG |
| 答案是否正确 | EM, Accuracy, F1, Number Match, exact value accuracy | 问答、表格/金融/数值型任务 |
| 生成文本是否相似 | ROUGE-L, BLEU, METEOR, BERTScore, BARTScore, MAUVE, cosine similarity | 摘要、长答案、开放式 QA |
| 是否忠于证据 | Faithfulness, groundedness, hallucination rate, citation/support score | 医疗、法律、企业、高风险 RAG |
| 多文档信息覆盖 | Coverage, ranked coverage, density, SecCov@k, CS Recall, answer-in-context | 长文档、报告生成、多跳、多节证据综合 |
| 部署效率 | Latency, token cost, compression ratio, retrieval rate, index size | 生产 RAG、context pruning、adaptive retrieval |

## 论文与指标汇总

| 年份 | 论文 / 方向 | 实验指标 |
|---|---|---|
| 2025 | [Enhancing Retrieval-Augmented Generation: A Study of Best Practices](https://arxiv.org/abs/2501.07391) | ROUGE-1/2/L F1, Embedding Cosine Similarity, MAUVE, FActScore |
| 2025 | [PIKE-RAG: sPecIalized KnowledgE and Rationale Augmented Generation](https://arxiv.org/abs/2501.11551) | Exact Match, F1, Precision, Recall, GPT-4-as-evaluator Accuracy |
| 2025 | [Provence: Efficient and Robust Context Pruning for RAG](https://arxiv.org/abs/2501.16214) | LLM-based evaluation, match-based Recall, compression ratio / pruning ratio |
| 2025 | [CG-RAG: Research Question Answering by Citation Graph RAG](https://arxiv.org/abs/2501.15067) | Retrieval Hit@1/Hit@3; multiple-choice MRR, Hit@k; True/False Accuracy; generation Coherence, Consistency, Relevance |
| 2025 | [Self-Routing RAG](https://arxiv.org/abs/2504.01018) | Accuracy, retrieval reduction / retrieval rate, knowledge-source selection accuracy |
| 2025 | [Controlled Retrieval-Augmented Context Evaluation for Long-form RAG / CRUX](https://arxiv.org/abs/2506.20051) | Coverage, ranked coverage / alpha-nDCG, Density; final RAG result coverage |
| 2025 | [RAGentA: Multi-Agent RAG for Attributed QA](https://arxiv.org/abs/2506.16988) | Recall@20, LLM-as-judge Correctness, Faithfulness |
| 2025 | [Rationale-Augmented Retrieval with Constrained LLM Re-Ranking](https://arxiv.org/abs/2510.05131) | Hit@K, Precision@K, Recall@K, MRR; online query success, zero-result rate, dwell-time proxy, latency |
| 2025 | [RAGSmith](https://arxiv.org/abs/2511.01386) | Retrieval: recall@k, mAP, nDCG, MRR; generation: LLM-Judge, semantic similarity |
| 2025 | [Local Hybrid Retrieval-Augmented Document QA](https://arxiv.org/abs/2511.10297) | Recall@K/Hit@K, MRR, mean/median rank, Rank-1 count; EM, Answer Coverage; Hallucination Rate, Faithfulness, Confidence, Success |
| 2025 | [CRUD-RAG](https://dl.acm.org/doi/10.1145/3701228) | BLEU, ROUGE-L, BERTScore, RAGQuestEval |
| 2025 | [NitiBench: Thai Legal QA](https://arxiv.org/abs/2502.10868) | Hit Rate / Multi-HitRate, Recall, MRR / Multi-MRR; Recall difference, Hallucination Rate |
| 2025 | [End-to-End Optimization for Multimodal RAG](https://aclanthology.org/2025.findings-emnlp.24.pdf) | Generator: Accuracy, F1, Fluency, EM, BARTScore; retriever: Recall@1/3/5/10/20/50/100; reranker: NDCG, MAP, MRR, P@1 |
| 2025 | [SafeRAG](https://arxiv.org/abs/2501.18636) | Attack-specific metrics, F1 variants, AFR / attack failure rate, security risk metrics |
| 2026 | [What Should I Cite? CiteRAG](https://arxiv.org/abs/2601.14949) | Retriever: Recall@k, MRR@k; Task 1: Recall@k, NDCG@k, Hit@k; Task 2: PACA@k; Citation Diversity Entropy, Hallucination Rate |
| 2026 | [From BM25 to Corrective RAG](https://arxiv.org/abs/2604.01733) | Recall@k, MRR@k, nDCG@k, MAP; Number Match; token-F1, ROUGE-L, BERTScore; paired bootstrap test |
| 2026 | [CHOP: Chunkwise Context-Preserving Framework for RAG on Multi Documents](https://arxiv.org/abs/2604.15802) | Retrieval: Hit@K, MRR@K, NDCG@K; generation: F1, ROUGE-L, BERTScore |
| 2026 | [GraLC-RAG: Biomedical Literature](https://arxiv.org/abs/2603.22633) | MRR, Recall@k; SecCov@k, CS Recall; generation F1; section diversity |
| 2026 | [StratRAG](https://arxiv.org/abs/2604.22757) | Recall@1/2/5, MRR, NDCG@5 |
| 2026 | [HiKEY: Hierarchical Multimodal Retrieval for Document QA](https://arxiv.org/abs/2605.29606) | Retrieval: Recall@K, MRR@K, Hit@K, All@K; QA: EM, ANLS, ROUGE-L, METEOR |
| 2026 | [MM-BizRAG](https://arxiv.org/abs/2606.04231) | Token recall, LLM-as-judge binary metric, FastRAGEval precision/recall/F1, Faithfulness |
| 2026 | [Benchmarking Retrieval Strategies for Biomedical RAG](https://arxiv.org/abs/2605.02520) | DeepEval contextual precision, contextual recall, faithfulness, answer relevancy; composite score; 95% CI |
| 2026 | [A Comparative Study of Language Models for Khmer RAG QA](https://arxiv.org/abs/2605.22099) | Hit Rate@3, File Hit Rate@3, MRR@3, Precision@3; RAGAS-style faithfulness, answer relevance, context relevance, factual correctness, answer similarity/correctness |
| 2026 | [Qwen Goes Brrr: Ukrainian Multi-Domain Document Understanding](https://arxiv.org/abs/2605.10296) | Recall@1, answer accuracy, leaderboard score |
| 2026 | [LegalGraphRAG](https://arxiv.org/abs/2605.28120) | Accuracy/F1 for charge/articles prediction; MAE for penalty term; latency and token cost |
| 2026 | [Decomposing Retrieval Failures in Long-Document Financial QA](https://arxiv.org/abs/2602.17981) | Document/page/chunk retrieval gap; BLEU and ROUGE-L between retrieved chunks and gold chunks; answer accuracy / ROUGE-L |
| 2026 | [Multi-Field Hybrid RAG for Maritime Accident RCA](https://arxiv.org/abs/2606.13249) | Ceiling-normalized Recall, nDCG with proxy relevance; LLM-as-judge RCA quality score |
| 2026 | [Improving Access to Historical Archives with Real-time RAG](https://arxiv.org/abs/2607.03440) | OCR CER/WER; NDCG@10; answer correctness; context relevance; latency |
| 2026 | [Budget-Constrained Multi-Hop RAG Diagnostic](https://arxiv.org/abs/2607.00725) | answer-in-context diagnostic; Recall@k; EM/F1; token budget/cost |
| 2026 | [ScoreGate: Adaptive Chunk Selection](https://arxiv.org/abs/2606.14269) | MRR@10; precision/recall; false positive rate / confidence interval; token reduction; added latency |
| 2026 | [FT-RAG for Complex Table Reasoning](https://arxiv.org/abs/2605.01495) | Table-level Hit Rate, cell-level Hit Rate; exact value accuracy recall; retrieval/generation alignment metrics |
| 2026 | [Invoice Haystack](https://arxiv.org/abs/2606.25343) | Document retrieval metrics and visual QA metrics; typically Recall/MRR/nDCG/QA accuracy |
| 2026 | [EReL@MIR 2025 Multimodal Document Retrieval Challenge](https://arxiv.org/abs/2606.04240) | Multimodal document retrieval challenge metrics, mainly retrieval ranking / relevance metrics |
| 2026 | [GraphFlow / KG-based RAG with Process Reward Models](https://arxiv.org/abs/2510.16582) | MRR, Recall@20, de-duplicated Recall@k, retrieval diversity/accuracy |

## 观察与归纳

### 1. 只看 Recall@k 不够

很多 2025+ 工作开始强调：RAG 的最终读者不是人类搜索用户，而是 LLM reader。因此传统 IR 指标虽然必要，但不能完全解释生成质量。长文档与多文档任务尤其需要额外看 coverage、density、answer-in-context、SecCov@k、CS Recall 等指标。

### 2. MRR / nDCG 仍然是 reranker 与检索排序的主力

对于 reranker、hybrid retrieval、KG-RAG、citation RAG，MRR 和 nDCG 最常见。MRR 强调第一个相关文档的位置，nDCG 更适合多相关文档、分级相关性、多证据任务。

### 3. 领域 RAG 会引入任务特化指标

金融表格 RAG 常用 Number Match、exact value accuracy recall。法律 RAG 会用多标签 Hit/Recall/MRR、hallucination rate、MAE for penalty term。医学/生物医学 RAG 会更重视 faithfulness、contextual precision/recall、结构覆盖。

### 4. 生成端越来越依赖 LLM-as-judge

开放式长答案、企业问答、报告生成等任务中，EM/ROUGE/BLEU 很难覆盖答案质量，因此论文常引入 LLM-as-judge 的 correctness、faithfulness、answer relevancy、FastRAGEval precision/recall/F1 等。

### 5. 工程指标成为标配

Context pruning、adaptive retrieval、multi-modal document retrieval、enterprise RAG 都会报告 latency、token reduction、compression ratio、retrieval rate、added latency 等指标。这说明 RAG 检索论文已经从“只看精度”转向“精度、成本、稳定性一起看”。

## 建议用于自己的 RAG 文档检索实验

如果要搭一个比较完整、容易被论文审稿接受的实验指标集合，可以按下面配置。

### 最小可用版

- Retrieval: Recall@5, Recall@10, MRR@10, nDCG@10
- Generation: EM 或 Accuracy, F1, ROUGE-L
- Trustworthiness: Faithfulness, Hallucination Rate
- Efficiency: latency, token count

### 推荐完整版

- Retrieval coverage: Recall@1/5/10, Hit@5/10, All@K
- Retrieval ranking: MRR@10, nDCG@10, MAP
- Retrieval precision: Precision@k, contextual precision
- Generation correctness: EM, Accuracy, token F1, Number Match if numeric
- Generation semantic quality: ROUGE-L, BERTScore, semantic similarity
- Grounding: Faithfulness, answer relevancy, context relevance, answer coverage
- Long-document coverage: answer-in-context, coverage, density, SecCov@k if documents have sections
- Robustness: performance under noisy/counterfactual/irrelevant contexts, hallucination rate
- Efficiency: retrieval latency, generation latency, total latency, tokens/query, compression ratio, index size

### 针对不同任务的优先级

| 任务类型 | 优先指标 |
|---|---|
| 单文档 QA | Recall@k, MRR, EM/F1, Faithfulness |
| 多文档 QA | Recall@k, nDCG@k, answer coverage, Faithfulness |
| 长文档/报告生成 | Coverage, ranked coverage, density, ROUGE-L/BERTScore, LLM-as-judge correctness |
| 表格/金融 QA | Recall@k, MRR, Number Match, exact value accuracy recall |
| 法律/医学 RAG | Recall@k, Multi-MRR, Faithfulness, hallucination rate, citation/support correctness |
| 多模态文档 RAG | Recall@k, Hit@k, ANLS, EM, visual grounding/citation correctness |
| 生产系统 | Recall@k, Faithfulness, latency, token cost, compression ratio, failure rate |

## 参考来源

- https://arxiv.org/abs/2501.07391
- https://arxiv.org/abs/2501.11551
- https://arxiv.org/abs/2501.16214
- https://arxiv.org/abs/2501.15067
- https://arxiv.org/abs/2504.01018
- https://arxiv.org/abs/2506.20051
- https://arxiv.org/abs/2506.16988
- https://arxiv.org/abs/2510.05131
- https://arxiv.org/abs/2511.01386
- https://arxiv.org/abs/2511.10297
- https://dl.acm.org/doi/10.1145/3701228
- https://arxiv.org/abs/2502.10868
- https://aclanthology.org/2025.findings-emnlp.24.pdf
- https://arxiv.org/abs/2501.18636
- https://arxiv.org/abs/2601.14949
- https://arxiv.org/abs/2604.01733
- https://arxiv.org/abs/2604.15802
- https://arxiv.org/abs/2603.22633
- https://arxiv.org/abs/2604.22757
- https://arxiv.org/abs/2605.29606
- https://arxiv.org/abs/2606.04231
- https://arxiv.org/abs/2605.02520
- https://arxiv.org/abs/2605.22099
- https://arxiv.org/abs/2605.10296
- https://arxiv.org/abs/2605.28120
- https://arxiv.org/abs/2602.17981
- https://arxiv.org/abs/2606.13249
- https://arxiv.org/abs/2607.03440
- https://arxiv.org/abs/2607.00725
- https://arxiv.org/abs/2606.14269
- https://arxiv.org/abs/2605.01495
- https://arxiv.org/abs/2606.25343
- https://arxiv.org/abs/2606.04240
- https://arxiv.org/abs/2510.16582
