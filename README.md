<div align="center">

# 🐛 Bug-Bounty-AI

**An autonomous, AI-powered bug bounty intelligence system for ethical hackers and security researchers.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-purple?style=flat-square&logo=linux)](https://kali.org)
[![Tests](https://img.shields.io/badge/tests-7%2F7%20passing-brightgreen?style=flat-square)](./test_system.py)
[![Last Commit](https://img.shields.io/github/last-commit/Sycosmile/Bug-bounty-ai?style=flat-square)](https://github.com/Sycosmile/Bug-bounty-ai/commits)
[![Stars](https://img.shields.io/github/stars/Sycosmile/Bug-bounty-ai?style=flat-square)](https://github.com/Sycosmile/Bug-bounty-ai/stargazers)

> ⚠️ **Authorized use only.** Only test targets you have explicit permission to assess. Unauthorized use violates the Nigeria Cybercrimes Act 2015 and equivalent laws worldwide.

</div>

---

## 🤔 Why Not Just Use Nuclei or Burp? 

Most tools give you **raw output** — you still have to manually decide what to run, in what order, and what findings actually matter. Bug-Bounty-AI is different:

- **Nuclei** is a scanner. It runs templates. You decide the strategy.
- **Burp Suite** is a proxy. Powerful, but manual-heavy and paid for serious use.
- **Bug-Bounty-AI** has an **AI planning engine** that reads your target context and *decides the attack sequence for you* — passive recon → fingerprinting → active scanning → exploitation → POC → report. One command, full chain.

It's not a replacement for these tools. It **orchestrates** them.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 AI Planning Engine | Sequences skills intelligently based on target context |
| 🔍 Passive Recon | Subdomain discovery, OSINT, DNS enumeration |
| 🌐 Web Scanning | Vuln detection via Nikto, header analysis, TLS checks |
| 💉 SQLi Detection | Automated SQL injection testing with payload generation |
| 🔐 Auth Testing | Authentication bypass and session analysis |
| 🔌 API Analysis | Endpoint discovery, parameter fuzzing, API security testing |
| 📄 POC Generator | Auto-generates proof-of-concept for discovered vulnerabilities |
| 📊 Report Submission | Structured bug report generation and export (JSON/Markdown) |
| 🎯 Smart Inspector | Pattern recognition and risk scoring engine |
| ⚡ Dynamic Skill Loading | Drop new `.py` files into `skills/` and they auto-register |

---

## ⚡ Quick Start

### Prerequisites

- Python 3.10+
- Kali Linux (recommended) or any Linux distro
- Optional but recommended: `subfinder`, `nmap`, `nikto`, `httpx`, `nuclei`

### Install

```bash
git clone https://github.com/Sycosmile/Bug-bounty-ai.git
cd Bug-bounty-ai
pip install -r requirements.txt
cp .env.example .env
```

### Run

```bash
python main.py
```

Enter your target domain when prompted.

### 🧪 Try It Safely First

Want to test without touching a real program? Use these **authorized practice targets**:
testphp.vulnweb.com        # Acunetix authorized test site

demo.testfire.net          # IBM Altoro Mutual demo

juice-shop.herokuapp.com   # OWASP Juice Shop

---

## 🔄 How It Works

Target Input       →   Provide a domain or IP
Skill Discovery    →   Loader auto-discovers all skills in skills/
AI Planning        →   Planner selects optimal skill sequence for the target
Execution          →   Skills run in sequence, updating shared context
Scoring            →   Each finding is risk-scored (Critical / High / Medium / Low)
POC Generation     →   Exploitable findings get POC templates
Report             →   Full findings exported as structured report


---

## 🗂️ Architecture
bug-bounty-ai/

├── main.py                  # Entry point

├── core/

│   ├── engine.py            # Orchestration engine

│   ├── async_engine.py      # Async execution support

│   ├── autonomy.py          # Autonomous decision logic

│   ├── registry.py          # Skill registration

│   ├── loader.py            # Dynamic skill discovery

│   ├── context.py           # Target state management

│   ├── scoring.py           # Vulnerability scoring

│   └── memory.py            # Session memory

├── skills/

│   ├── passive_recon.py     # OSINT & subdomain enum

│   ├── web_scan.py          # Web vulnerability scanning

│   ├── sqli_detect.py       # SQL injection detection

│   ├── auth_test.py         # Authentication testing

│   ├── api_scan.py          # API endpoint discovery

│   ├── api_tester.py        # API behavior analysis

│   ├── tech_fingerprint.py  # Technology fingerprinting

│   ├── exposure.py          # Service exposure analysis

│   ├── inspector.py         # Pattern analysis & insights

│   ├── poc_generator.py     # POC generation

│   ├── report_submit.py     # Report submission

│   └── report.py            # Summary generation

├── tools/

│   ├── nmap.py              # Nmap wrapper

│   ├── nikto.py             # Nikto wrapper

│   ├── subfinder.py         # Subfinder wrapper

│   ├── httpx.py             # HTTPX wrapper

│   └── nuclei.py            # Nuclei wrapper

├── verify/

│   ├── headers.py           # Security header checks

│   ├── tls_check.py         # TLS/SSL analysis

│   ├── clickjacking.py      # Clickjacking detection

│   └── confirm.py           # Vulnerability confirmation

├── ai/

│   ├── planner.py           # AI skill sequencing

│   └── llm_scorer.py        # LLM-based risk scoring

└── reports/

└── exporter.py          # Report export (JSON/Markdown)

---

## 🧩 Adding a New Skill

The plugin system is dead simple — drop a file, it works:

```python
# skills/my_skill.py
def run(context):
    # your logic here
    context["my_findings"] = []
    return context

skill = {"name": "my_skill", "run": run}
```

Drop it in `skills/` — it auto-registers. No config, no imports, no boilerplate.

---

## 🗺️ Roadmap

- [ ] Web dashboard (FastAPI + React)
- [ ] HackerOne / Bugcrowd report auto-submit integration
- [ ] CVE enrichment via NVD API
- [ ] Slack / Telegram alert on critical findings
- [ ] Docker support for isolated execution

---

## 👤 Author

**MR SYCO** — Cybersecurity student | Bug bounty hunter | 3MTT Nigeria Cohort

[![GitHub](https://img.shields.io/badge/GitHub-Sycosmile-black?style=flat-square&logo=github)](https://github.com/Sycosmile)
[![Twitter](https://img.shields.io/badge/X-@Sycosmile-black?style=flat-square&logo=x)](https://x.com/Sycosmile)

---

## 📄 License

MIT — free to use, modify, and distribute. See [LICENSE](LICENSE) for details.

---

<div align="center">
<sub>Built with Python 🐍 on Kali Linux ☠️ | Only hack what you own or have permission to test.</sub>
</div>
