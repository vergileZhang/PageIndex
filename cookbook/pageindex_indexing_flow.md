# PageIndex 建索引流程简明说明

这份文档说明 `pageindex/page_index.py` 里 PDF 索引是怎么构建的。

PageIndex 建的不是向量索引，而是一棵结构化的文档树。最终索引大致包含：

- `title`: 章节标题
- `start_index`: 章节开始页
- `end_index`: 章节结束页
- `nodes`: 子章节
- `node_id`: 节点编号
- `summary`: 节点摘要

## 1. 读取 PDF

入口是 `page_index()`，它会加载配置，然后进入 `page_index_main()`。

`page_index_main()` 首先把 PDF 按页解析成：

```text
第 1 页文本 + token 数
第 2 页文本 + token 数
第 3 页文本 + token 数
...
```

这些页文本会被用于目录检测、章节定位、accuracy 检查和后续摘要生成。

## 2. 检测目录

接着进入 `tree_parser()`。

它会先调用 `check_toc()`，默认检查前 20 页，看有没有目录页。

每一页会交给 LLM 判断：

```text
这一页是不是 table of contents？
```

如果找到目录页，就把目录页文本合并起来，并继续判断目录中是否带页码。

## 3. 目录可用时

如果目录存在，并且目录里带页码，例如：

```text
Introduction .... 1
Method .... 5
Experiments .... 12
```

PageIndex 会先用 `toc_transformer()` 把目录转成结构化列表：

```json
[
  {"structure": "1", "title": "Introduction", "page": 1},
  {"structure": "2", "title": "Method", "page": 5}
]
```

这里的 `page` 是目录中写的页码，不一定等于 PDF 文件的真实页码。

所以它会再到正文中寻找这些标题实际出现的 PDF 物理页，计算目录页码和真实页码之间的偏移量，然后把所有目录页码校准成 `physical_index`。

## 4. 没有可用目录时

如果没有目录，或者目录不可用，PageIndex 会从正文直接抽章节树。

它会给每页正文加页码标签：

```text
<physical_index_5>
这一页正文内容
<physical_index_5>
```

然后按 token 把正文分组，交给 LLM 抽取章节结构：

```json
[
  {"structure": "1", "title": "Introduction", "physical_index": 1},
  {"structure": "2", "title": "Method", "physical_index": 5}
]
```

其中 `structure` 表示章节层级，例如 `1`、`1.1`、`2.3`；`physical_index` 表示真实 PDF 页码。

## 5. 得到平铺章节列表

不管是从目录构建，还是从正文抽取，系统都会先得到一个平铺列表：

```text
1 Introduction -> 第 1 页
2 Method -> 第 5 页
2.1 Model -> 第 6 页
3 Experiments -> 第 12 页
```

这时还不是最终树，只是带层级编号和页码的章节列表。

## 6. accuracy 自检

随后 `meta_processor()` 会调用 `verify_toc()` 检查页码是否靠谱。

例如索引说：

```text
Method 从第 5 页开始
```

系统就取出第 5 页正文，让 LLM 判断：

```text
“Method” 这个标题是不是出现在第 5 页？
```

如果回答 yes，说明这个章节页码正确；如果回答 no，就记为错误。

最终：

```text
accuracy = 页码正确的章节数 / 被检查的章节数
```

这个 accuracy 只表示章节起始页定位是否准确，不是问答准确率，也不是检索准确率。

## 7. 修正或换方案

如果 `accuracy == 1.0`，说明章节页码都通过检查，直接接受。

如果 `accuracy > 0.6`，说明大部分页码是对的，少量错误会进入修正流程：

```text
在前一个正确章节和后一个正确章节之间，重新让 LLM 找错误章节的起始页。
```

如果 `accuracy <= 0.6`，说明当前方法不可靠，系统会换方案重建：

```text
目录页码方案失败 -> 尝试重新补页码
补页码失败 -> 从正文直接抽章节树
正文抽树还失败 -> 报错
```

## 8. 转成树索引

通过检查后，PageIndex 会把平铺列表转成嵌套树，并计算每个节点的：

- `start_index`
- `end_index`
- `nodes`

`end_index` 通常由下一个章节的起始页推出来。

如果某个节点仍然太大，超过配置中的页数和 token 阈值，系统会对这个节点内部再次运行正文抽树流程，把它继续拆成更细的子节点。

## 9. 添加节点信息

最后根据配置补充节点信息：

- `node_id`: 给每个节点编号
- `text`: 可选，保存节点覆盖的正文
- `summary`: 给每个节点生成摘要
- `doc_description`: 可选，生成整篇文档描述

默认配置会添加 `node_id` 和 `summary`，但不会在最终结构里保留完整正文 `text`。

## 总结

PageIndex 的 PDF 建索引流程可以概括为：

```text
读取 PDF
-> 检测目录
-> 用目录或正文生成章节列表
-> 检查章节页码 accuracy
-> 修正错误或换方案重建
-> 转成带 start/end 页码的树结构
-> 添加 node_id 和 summary
```

核心思想是：

```text
先用 LLM 把长文档变成章节树，再用真实页码锚点校验和修正，最后得到可检索的 JSON Tree。
```
