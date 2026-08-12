<div align="center">
  <img src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExbnlyMTlsYjQzMWwyaHlybHVnMnBocW9tOHZtcTVxeGpsZmdxcHUxaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Yq5yq5W28FvP1EehQn/giphy.webp" alt="Radar GIF" width="150" style="border-radius:50%">

  # 🛡️ Real-Time Fraud Detection Engine

  [![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1000&color=10B981&center=true&vCenter=true&width=435&lines=Detecting+Fraud+in+Real-Time...;Kaggle+1st+Place+Magic+Features;LightGBM+%7C+FastAPI+%7C+DVC+%7C+MLflow)](https://git.io/typing-svg)
  
  [![Live Demo](https://img.shields.io/badge/🔴_Live_Demo-Access_Dashboard-FF4136?style=for-the-badge&logo=appveyor)](https://tinyurl.com/38rtjatu)

</div>

<br>

## 🌐 Live Dashboard
Experience the real-time scoring engine via our live interactive dashboard:
👉 **[Access the Live Demo Here](https://tinyurl.com/38rtjatu)**

---

## 🧠 About The Project
This project is a complete end-to-end Machine Learning pipeline that identifies fraudulent credit card transactions in real-time. Evolving from the Kaggle IEEE-CIS Fraud Detection dataset, it implements the **1st-place winning "Magic Features"** (47+ Client UID aggregations) to achieve state-of-the-art predictive performance.

### 🌟 Key Features
- **Real-Time Scoring API**: Ultra-fast predictions served via a containerized FastAPI backend.
- **Kaggle Magic Features**: Time-series grouping and frequency encoding across unique Client UIDs to link historical behavior.
- **MLOps Pipeline**: Fully reproducible data processing, model training, and evaluation pipelines tracked with **DVC** and **MLflow**.
- **Interactive Dashboard**: A Flask-based UI mimicking a live payment gateway investigator dashboard.

---

## 📈 Model Performance
Using a heavily tuned **LightGBM** Calibrated Classifier, the model achieves massive reductions in False Positives while aggressively catching fraud.

* **ROC-AUC**: `0.932`
* **Precision (at best F1)**: `66.84%`
* **Recall (Top 5% Risk)**: `63.73%`

---

## 🛠️ Tech Stack
<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/LightGBM-F37021?style=for-the-badge&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/DVC-945DD6?style=for-the-badge&logo=data-version-control&logoColor=white" />
  <img src="https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white" />
</p>

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
```

---
<div align="center">
  <i>Built with ❤️ for catching bad actors.</i>
</div>
