# AI4S Papers Service

An AI-powered academic paper processing and management system that supports intelligent PDF parsing, metadata extraction, deduplication, and knowledge base construction.

## 🚀 Project Overview

AI4S Papers Service is a modern academic paper processing pipeline designed to provide automated literature management solutions for the AI for Science research community. The system implements a fully automated workflow from PDF upload to structured storage through event-driven architecture.

## 🏗️ System Architecture

**Event-Driven Microservices Architecture**

**Trigger Layer**
- Cloudflare R2 Storage + Event Listening
- Cloudflare Worker Event Processing

**Orchestration Layer**  
- Prefect Workflow Engine
- Automated Task Scheduling and Error Handling

**Computing Layer**
- Modal GPU Service (PDF Parsing)
- Google ADK Agent (AI Metadata Extraction)

**Storage Layer**
- Django REST API
- PostgreSQL Database
- Intelligent Deduplication and Version Management

**Application Layer**
- FastGPT Knowledge Base Integration
- File Browsing and Management Interface

**Data Flow**: R2 Upload Event → Prefect Workflow → Modal PDF Parsing → Google ADK Extraction → Django API Storage → FastGPT Knowledge Base

## 📁 Project Structure

### Core Services

- **`papers_db/`** - Django API Service
  - Paper data storage and management
  - RESTful API interface
  - File browsing and download
  - Intelligent deduplication

- **`prefect_workflow/`** - Prefect Workflow Service
  - Automated processing pipeline
  - PDF download and parsing orchestration
  - AI metadata extraction
  - Database storage coordination

- **`cloudflare-r2event/`** - Cloudflare Worker
  - R2 storage event monitoring
  - Automatic process triggering
  - PDF-only file processing

- **`pdf_parser_service/`** - Modal GPU Service
  - High-performance PDF parsing
  - Support for Marker and Docling engines
  - GPU-accelerated processing

### Shared Components

- **`prefect_workflow/markdown_agent/`** - AI Metadata Extraction Agent
  - Google ADK-based intelligent agent
  - Structured metadata extraction from paper content
  - Support for multiple academic information fields

## ✨ Automated Processing Workflow

1. **File Upload**: PDF files uploaded to Cloudflare R2
2. **Event Trigger**: R2 events automatically trigger Prefect workflows
3. **PDF Parsing**: Modal GPU service parses PDF to Markdown
4. **AI Extraction**: Google ADK Agent extracts paper metadata
5. **Intelligent Deduplication**: Automatic deduplication based on PDF MD5
6. **Data Storage**: Structured data stored in PostgreSQL
7. **Knowledge Base**: Optional synchronization to FastGPT knowledge base

## 🛠️ Tech Stack

### Backend Services
- **Django 4.x** - Web framework and API
- **PostgreSQL** - Primary database
- **Prefect 3.x** - Workflow orchestration
- **Modal** - Serverless GPU computing

### AI/ML Components
- **Google ADK** - AI Agent framework
- **Marker** - PDF parsing engine
- **Docling** - Alternative PDF parsing engine
- **FastGPT** - Knowledge base management

### Infrastructure
- **Cloudflare R2** - Object storage
- **Cloudflare Workers** - Edge computing
- **Docker** - Containerized deployment

---

*AI-driven academic paper management for smarter literature processing experience.*
