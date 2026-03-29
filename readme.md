# 🤖 Bot 02: Multi-Modal AI Business Auditor & Automated ETL Pipeline

## 📌 Project Overview
**Bot 02** is a production-ready AI automation system designed to transform unstructured business documents into structured, actionable data. Leveraging the multi-modal power of **Google Gemini 3.1 Flash-lite**, the system automatically identifies, audits, and extracts key information from **Invoices** and **Resumes** uploaded via Telegram. 

The extracted data is routed through a custom **ETL (Extract, Transform, Load)** pipeline via **Make.com** and persisted into **Google Sheets** for real-time business intelligence.

---

## 🏗️ System Architecture
The system is built on a decoupled, event-driven architecture:

1.  **Ingestion Layer**: Telegram Bot API for seamless document capture.
2.  **Processing Layer**: An asynchronous **FastAPI** backend (deployed on **Render**) managing webhooks and image data.
3.  **Intelligence Layer**: **Gemini 3.1 Flash-lite** for zero-shot document classification and JSON extraction.
4.  **Integration Layer**: **Make.com** acting as a serverless middleware for conditional routing and data filtering.
5.  **Persistence Layer**: **Google Sheets** for structured data storage and reporting.

---

## 🚀 Key Features
* **Multi-Modal Intelligence**: Seamlessly handles both images and text, automatically distinguishing between an invoice and a resume without user input.
* **Structured Data Extraction**: Converts raw pixels into high-fidelity JSON objects following strict enterprise schemas.
* **Automated Audit Logic**:
    * **Invoices**: Extracts Vendor, Amount, Currency, and Date. Assigns `audit_status` based on AI-generated `confidence_score`.
    * **Resumes**: Extracts Candidate Name, Contact, and Skills; generates a `match_score` for algorithmic talent assessment.
* **Dynamic Routing**: Implements attribute-based filtering to ensure data isolation between different business departments.
* **System Robustness**: Includes data sanitization layers to handle malformed API responses and URL encoding issues.

---

## 🛠️ Tech Stack
* **Language**: Python 3.14
* **Framework**: FastAPI
* **AI Engine**: Google Gemini 3.1 Flash-lite
* **Middleware**: Make.com (Integromat)
* **Storage**: Google Sheets API
* **Deployment**: Render (CI/CD via GitHub)
* **DevOps**: Environment Variable Management, Logging, and Asynchronous Requests.

---

## 🔧 Setup & Installation

1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/your-username/bot02.git](https://github.com/your-username/bot02.git)
    cd bot02
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**: Create a `.env` file:
    ```env
    TELEGRAM_TOKEN=your_bot_token
    GEMINI_API_KEY=your_api_key
    MAKE_WEBHOOK_URL=your_webhook_url
    ```
4.  **Deployment**:
    Push to GitHub and connect to **Render** for automatic deployment.

---

## 🧠 Engineering Insights (For Interview Deep-Dives)
* **URL Sanitization**: Solved `InvalidSchema` exceptions by implementing strict string purification for the Telegram file-downloading protocol.
* **Deterministic Schema Mapping**: Utilized header-based IDs in the persistence layer to ensure the pipeline remains robust even if the spreadsheet structure is reordered by business users.
* **Latency Optimization**: Selected the `flash-lite` model variant to balance high-speed inference with complex multi-modal reasoning.

---

## 📜 License
MIT License. Created by Junyu (俊宇) as part of an Advanced AI Integration Project.