<div align="center">
  <img src="assets/hero_banner.jpg" alt="Sentinel Hero Banner" width="100%" style="border-radius:16px; margin-bottom: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
  
  <br>

  <h1 align="center">🛡️ Sentinel | Real-Time Fraud Detection Engine</h1>

  <!-- Animated Typing SVG -->
  [![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1000&color=10B981&center=true&vCenter=true&width=435&lines=Detecting+Fraud+in+Real-Time...;LightGBM+%7C+FastAPI+%7C+DVC+%7C+MLflow)](https://git.io/typing-svg)
  
  [![Live Demo](https://img.shields.io/badge/🔴_Live_Demo-Access_Dashboard-FF4136?style=for-the-badge&logo=appveyor)](https://tinyurl.com/38rtjatu)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

</div>

<br>

## 🌐 Live Dashboard
Experience the real-time scoring engine via our live interactive dashboard. The dashboard features micro-animations, real-time gauges, and dynamic metrics updates.
👉 **[Access the Live Demo Here](https://tinyurl.com/38rtjatu)**

---

## 🧠 About The Project
This project is a complete end-to-end Machine Learning pipeline that identifies fraudulent credit card transactions in real-time. Evolving from the Kaggle IEEE-CIS Fraud Detection dataset, it implements the **1st-place winning "Magic Features"** (47+ Client UID aggregations) to achieve state-of-the-art predictive performance.

### 🌟 Key Features
- **Real-Time Scoring API**: Ultra-fast predictions served via a containerized FastAPI backend.
- **Kaggle Magic Features**: Time-series grouping and frequency encoding across unique Client UIDs to link historical behavior.
- **MLOps Pipeline**: Fully reproducible data processing, model training, and evaluation pipelines tracked with **DVC** and **MLflow**.
- **Interactive Dashboard**: A highly polished Flask-based UI mimicking a live payment gateway investigator dashboard with HSL dark-mode aesthetics and fluid animations.

---

## 📈 Model Performance
Using a heavily tuned **LightGBM** Calibrated Classifier, the model achieves massive reductions in False Positives while aggressively catching fraud.

| Metric | Score | Impact |
| :--- | :---: | :--- |
| **ROC-AUC** | `0.932` | Top-tier distinction between fraud/legit |
| **Precision** | `66.84%` | High confidence on flagged transactions |
| **Recall (Top 5%)** | `63.73%` | Captures majority of fraud in high-risk bin |

---

## 🛠️ Tech Stack
<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/LightGBM-F37021?style=for-the-badge&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/DVC-945DD6?style=for-the-badge&logo=data-version-control&logoColor=white" />
  <img src="https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white" />
</div>

---

## 🚀 Quick Start (Local Setup)

Want to run the full stack locally on your own machine?

1. **Clone the repository**
   ```bash
   git clone https://github.com/vyash0048-bit/Fraud_Detection.git
   cd Fraud_Detection
   ```

2. **Pull the Model Weights via DVC**
   ```bash
   dvc pull
   ```

3. **Spin up the Environment via Docker**
   ```bash
   docker-compose up --build -d
   ```
   *The FastAPI server will boot up on `localhost:8000` and the interactive Dashboard on `localhost:5000`.*

---

## 🏗️ Architecture

```mermaid
graph LR
    A[Transaction Payload] -->|JSON| B(Flask Dashboard)
    B -->|REST API POST| C{FastAPI Backend}
    C -->|Feature Parsing & Coercion| D[LightGBM Calibrated CV]
    D -->|Prob=0.92| C
    C -->|Thresholding Engine| C
    C -->|Decision: DECLINE| B
    
    style A fill:#1e1e1e,stroke:#333,stroke-width:2px,color:#fff
    style B fill:#000000,stroke:#10B981,stroke-width:2px,color:#fff
    style C fill:#009688,stroke:#00796B,stroke-width:2px,color:#fff
    style D fill:#F37021,stroke:#D84315,stroke-width:2px,color:#fff
```

---
<div align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1000&color=10B981&center=true&vCenter=true&width=350&lines=Built+with+passion+for+security.;Stopping+bad+actors+in+real-time." alt="Typing Footer" />
</div>
