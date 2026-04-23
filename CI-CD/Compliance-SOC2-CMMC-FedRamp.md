# Compliance (SOC2, CMMC, FedRamp)
Here's a breakdown of these three major tech compliance frameworks — what they are, how to get them, and what they unlock.

---

## SOC 2 (System and Organization Controls 2)

**What it is:** An auditing framework created by the AICPA that evaluates how a company manages customer data based on five "Trust Service Criteria" — Security, Availability, Processing Integrity, Confidentiality, and Privacy. It's *not* a government regulation; it's a voluntary third-party audit that has become a de facto market requirement for SaaS and cloud companies.

**Type I vs Type II:** Type I is a snapshot — an auditor reviews your controls at a single point in time. Type II is the gold standard — an auditor reviews whether your controls actually *worked* over a period (typically 6–12 months). Most enterprise customers require Type II.

**What you need to do:**
- Define your scope (which systems, which Trust Service Criteria)
- Implement security controls: access management, encryption, logging, incident response, vendor management, etc.
- Undergo a readiness assessment (optional but common)
- Hire an AICPA-accredited CPA firm to conduct the audit
- Receive and maintain your SOC 2 report

**What it grants you:** Not a certification — it's a *report* that you share (typically under NDA) with prospective enterprise customers to pass security reviews and sales due diligence. Essentially table stakes for selling B2B SaaS.

**Time to complete:** Type I: 2–4 months. Type II: 6–12 months for the observation period, then ~2–3 months for audit. Reports must be renewed annually.

**Typical cost:** $20K–$80K for the first audit; less for renewals.

---

## CMMC (Cybersecurity Maturity Model Certification)

**What it is:** A DoD (Department of Defense) framework that requires any company in the Defense Industrial Base (DIB) to demonstrate cybersecurity practices before winning or renewing federal contracts. If you handle **FCI** (Federal Contract Information) or **CUI** (Controlled Unclassified Information), CMMC applies to you.

**The three levels:**
- **Level 1** — 17 basic practices (largely NIST SP 800-171 basics). Self-assessment allowed. For FCI only.
- **Level 2** — 110 practices from NIST SP 800-171. Third-party assessment (C3PAO) required for most contracts. For CUI.
- **Level 3** — 24 additional controls from NIST SP 800-172. Government-led assessment. For highly sensitive CUI on critical programs.

**What you need to do:**
- Identify which level your contracts require
- Perform a gap assessment against NIST 800-171
- Build or remediate controls across 14 domains (access control, incident response, configuration management, etc.)
- Create and maintain a System Security Plan (SSP) and Plan of Action & Milestones (POA&M)
- For Level 2+: hire a C3PAO (Certified Third-Party Assessment Organization) for your assessment
- Submit results to the CMMC database (Supplier Performance Risk System — SPRS)

**What it grants you:** Eligibility to bid on and hold DoD contracts. Without the right level, you're contractually barred. It's binary — pass or you can't work with DoD.

**Time to complete:** Level 1: 1–3 months. Level 2: 12–24 months depending on current security posture. Level 3: 18–36+ months.

**Typical cost:** Level 1: $5K–$30K. Level 2: $100K–$500K+ depending on size and gaps. Level 3 can exceed $1M.

---

## FedRAMP (Federal Risk and Authorization Management Program)

**What it is:** A U.S. government-wide program that standardizes security assessment and authorization for cloud services used by federal agencies. If you want to sell cloud software (SaaS, PaaS, IaaS) *to* the federal government, FedRAMP authorization is essentially mandatory. It's built on NIST SP 800-53 controls.

**Authorization paths:**
- **Agency ATO (Authority to Operate):** You partner with a sponsoring federal agency that champions your authorization. Faster, but requires finding a willing agency partner.
- **JAB (Joint Authorization Board) P-ATO:** Reviewed by DoD, DHS, and GSA. Highest credibility, but JAB was significantly restructured in 2023 — the "Marketplace" model now dominates.
- **FedRAMP 20X (emerging):** A new streamlined pathway announced in 2025 aimed at reducing time and cost dramatically via automation and continuous assessment.

**Impact levels:**
- **Low** — public, non-sensitive data
- **Moderate** — the most common; covers most federal SaaS
- **High** — highly sensitive data (law enforcement, emergency services, financial)

**What you need to do:**
- Choose impact level and authorization path
- Hire a FedRAMP-accredited 3PAO (Third Party Assessment Organization)
- Implement hundreds of NIST 800-53 controls (325 for Moderate, 421 for High)
- Develop a massive documentation package: SSP, SAP, SAR, POA&M, boundary diagrams
- Submit for review and receive ATO
- Maintain continuous monitoring with monthly/annual reporting forever after

**What it grants you:** Listing on the FedRAMP Marketplace — the official catalog federal agencies shop from. It dramatically accelerates agency procurement. Without it, agencies face a long, bespoke process to use your software, which most won't do.

**Time to complete:** 12–24 months for Moderate (Agency path). 18–36 months for High or JAB. Continuous monitoring is perpetual.

**Typical cost:** $500K–$2M+ for initial authorization. Ongoing compliance can run $200K–$500K/year.

---

Here's a visual summary of how they compare:---
<img width="1440" height="1436" alt="image" src="https://github.com/user-attachments/assets/9438fdcb-3038-44df-89ef-95f115633524" />

## Strategic sequencing

Most companies tackle these in this order based on what markets they're targeting:

**Commercial B2B SaaS** → Start with SOC 2 Type II. It's the cheapest and fastest entry point into enterprise sales.

**Defense contractors** → CMMC is non-negotiable. Start with a gap assessment against NIST 800-171 early — the remediation work is substantial.

**Federal/civilian agencies** → FedRAMP is the mountain. Many companies pursue SOC 2 first to build security muscle, then layer on FedRAMP. The good news: SOC 2 and FedRAMP share significant control overlap, so work done for one accelerates the other.

A practical note: the *readiness* work (building the actual security controls and policies) typically takes 60–80% of the total time. The audit itself is just the final step. Starting early and treating compliance as infrastructure — not a checkbox — is what separates companies that sail through audits from those that struggle.
