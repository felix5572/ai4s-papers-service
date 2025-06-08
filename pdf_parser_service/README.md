# PDF Parser Service 📄

简单的PDF解析微服务，使用Modal平台部署。

## 🚀 快速使用

### 1. 部署

```bash
cd pdf_parser_service
modal deploy pdf_parser.py
```

### 2. 获取API地址

部署后会显示类似地址：
```
https://yourusername--pdf-parser-parse-pdf-upload.modal.run
```

### 3. 调用API

**文件上传方式（推荐）：**
```bash
curl -X POST "https://your-endpoint.modal.run" \
  -F "file=@sample.pdf" \
  -F "engine=marker"
```

**URL方式：**
```bash
curl -X POST "https://your-endpoint.modal.run" \
  -H "Content-Type: application/json" \
  -d '{"pdf_url": "https://example.com/file.pdf", "engine": "marker"}'
```

## 📁 文件结构

```
pdf_parser_service/
├── pdf_parser.py      # 主服务代码
├── requirements.txt   # 依赖列表
└── README.md         # 说明文档
```

## 🔧 配置

- **GPU**: T4 (8GB内存)
- **引擎**: Marker (默认) / Docling
- **超时**: 10分钟
- **文件大小**: 最大50MB

## 🛠️ 开发

```bash
# 查看日志
modal logs pdf-parser

# 健康检查
curl https://your-endpoint-health.modal.run

# 重新部署
modal deploy pdf_parser.py
```

就这么简单！🎉 