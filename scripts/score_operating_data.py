import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis"
OUTPUTS = ANALYSIS / "outputs"

RANDOM_SEED = 20260527
random.seed(RANDOM_SEED)

MONTHS = [
    "2025-06",
    "2025-07",
    "2025-08",
    "2025-09",
    "2025-10",
    "2025-11",
    "2025-12",
    "2026-01",
    "2026-02",
    "2026-03",
    "2026-04",
    "2026-05",
]

PRODUCTS = [
    ("HPA-001", "Risk adjustment gap closure", "Payer", "Risk score accuracy", "Scale", "Maya Patel", "Claims and clinical"),
    ("HPA-002", "Quality and Stars measurement", "Payer", "Quality improvement", "Scale", "Luis Romero", "Clinical and member"),
    ("HPA-003", "Interoperability member 360", "Payer", "Longitudinal member view", "Expand", "Chen Wu", "Clinical and claims"),
    ("HPA-004", "Value-based contract analytics", "Payer", "Provider contract performance", "Pilot", "Priya Menon", "Claims and contract"),
    ("HPA-005", "Revenue cycle denials intelligence", "Provider", "Claims denial reduction", "Scale", "Jordan Ellis", "Claims and remit"),
    ("HPA-006", "Eligibility verification automation", "Provider", "Front-end revenue cycle", "Scale", "Avery Brooks", "Eligibility"),
    ("HPA-007", "Medical record review AI", "Provider", "Chart retrieval and abstraction", "Pilot", "Nora Singh", "Clinical records"),
    ("HPA-008", "Provider performance benchmarks", "Provider", "Operational benchmarking", "Expand", "Ethan Clark", "Claims and operations"),
    ("HPA-009", "Specialty pharmacy adherence", "Pharmacy", "Medication adherence", "Scale", "Sofia Martinez", "Prescription and dispense"),
    ("HPA-010", "Pharmacy claims reconciliation", "Pharmacy", "Claims adjudication", "Expand", "Mina Shah", "Pharmacy claims"),
    ("HPA-011", "Medication therapy management", "Pharmacy", "Patient intervention workflow", "Pilot", "Ravi Kapoor", "Medication profile"),
    ("HPA-012", "Prior authorization analytics", "Pharmacy", "Access and approval workflow", "Discover", "Kara Nguyen", "Authorization"),
    ("HPA-013", "Real-world evidence cohorts", "Life sciences", "RWE patient cohorts", "Scale", "Olivia Chen", "De-identified claims"),
    ("HPA-014", "Clinical trial feasibility", "Life sciences", "Site and patient discovery", "Expand", "Sam Reed", "De-identified clinical"),
    ("HPA-015", "Commercial analytics segmentation", "Life sciences", "Market access targeting", "Pilot", "Fatima Ahmed", "Claims and SDOH"),
    ("HPA-016", "Healthcare data lineage hub", "Platform", "Data quality and lineage", "Expand", "Daniel Kim", "Metadata and controls"),
]

SEGMENT_FACTORS = {
    "Payer": {"market_size": 5.8, "cagr": 0.115, "sales_cycle": 8, "regulatory": 84},
    "Provider": {"market_size": 7.2, "cagr": 0.092, "sales_cycle": 6, "regulatory": 78},
    "Pharmacy": {"market_size": 3.1, "cagr": 0.074, "sales_cycle": 5, "regulatory": 74},
    "Life sciences": {"market_size": 4.6, "cagr": 0.128, "sales_cycle": 7, "regulatory": 81},
    "Platform": {"market_size": 2.4, "cagr": 0.101, "sales_cycle": 7, "regulatory": 88},
}

STAGE_FACTORS = {
    "Discover": {"clients": 4, "arr": 0.36, "cost": 0.22, "margin": 0.48, "win": 0.18},
    "Pilot": {"clients": 9, "arr": 0.74, "cost": 0.38, "margin": 0.54, "win": 0.24},
    "Expand": {"clients": 21, "arr": 1.72, "cost": 0.78, "margin": 0.61, "win": 0.31},
    "Scale": {"clients": 42, "arr": 3.9, "cost": 1.55, "margin": 0.67, "win": 0.37},
}

THEMES = [
    ("pricing clarity", "buyers need tier and usage language that maps to budgets"),
    ("workflow integration", "users want fewer handoffs between analytics and operational queues"),
    ("metric trust", "stakeholders asked for clearer numerator, denominator, and data freshness notes"),
    ("implementation speed", "prospects care about time to first validated insight"),
    ("compliance evidence", "buyers want visible privacy, audit, and access controls before expansion"),
    ("usability friction", "users spend too long interpreting exception and next-action screens"),
    ("competitive proof", "marketing needs proof points against point solutions and internal builds"),
]

PERSONAS = [
    "VP Product",
    "Quality analytics director",
    "Revenue cycle leader",
    "Pharmacy operations director",
    "Life sciences analytics lead",
    "Data governance owner",
    "Implementation manager",
]


def clamp(value, floor, ceiling):
    return max(floor, min(ceiling, value))


def money(value):
    return round(value, 2)


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_product_modules():
    rows = []
    for idx, (product_id, name, segment, workflow, stage, owner, data_type) in enumerate(PRODUCTS, start=1):
        segment_factor = SEGMENT_FACTORS[segment]
        stage_factor = STAGE_FACTORS[stage]
        stage_noise = random.uniform(0.86, 1.18)
        clients = int(stage_factor["clients"] * random.uniform(0.82, 1.28))
        arr = money(stage_factor["arr"] * segment_factor["market_size"] * stage_noise * 1000000)
        annual_cost = money(stage_factor["cost"] * random.uniform(0.88, 1.26) * 1000000)
        gross_margin = round(clamp(stage_factor["margin"] + random.uniform(-0.08, 0.07), 0.34, 0.78), 3)
        win_rate = round(clamp(stage_factor["win"] + random.uniform(-0.06, 0.08), 0.11, 0.49), 3)
        nps = int(clamp(42 + gross_margin * 35 + random.uniform(-16, 14), 24, 78))
        retention = round(clamp(0.82 + gross_margin / 5 + random.uniform(-0.05, 0.04), 0.78, 0.96), 3)
        rows.append(
            {
                "product_id": product_id,
                "product_name": name,
                "customer_segment": segment,
                "workflow": workflow,
                "stage": stage,
                "owner": owner,
                "regulated_data_type": data_type,
                "baseline_clients": clients,
                "current_arr": arr,
                "annual_operating_cost": annual_cost,
                "gross_margin_rate": gross_margin,
                "win_rate": win_rate,
                "nps": nps,
                "retention_rate": retention,
                "target_persona": PERSONAS[idx % len(PERSONAS)],
            }
        )
    return rows


def generate_monthly_performance(products):
    rows = []
    for product in products:
        base_clients = int(product["baseline_clients"])
        base_arr = float(product["current_arr"])
        base_margin = float(product["gross_margin_rate"])
        stage = product["stage"]
        growth = {"Discover": 0.018, "Pilot": 0.025, "Expand": 0.034, "Scale": 0.022}[stage]
        for month_index, month in enumerate(MONTHS):
            seasonal = math.sin((month_index + 1) / 12 * math.pi) * 0.025
            active_clients = max(2, int(base_clients * (1 + growth * (month_index - 6)) + random.randint(-2, 3)))
            transactions = int(active_clients * random.randint(8200, 24000) * random.uniform(0.86, 1.16))
            arr = money(base_arr * (1 + growth * (month_index - 6) + seasonal + random.uniform(-0.018, 0.018)))
            implementation_cost = money(active_clients * random.uniform(11000, 38000))
            support_cost = money(active_clients * random.uniform(6200, 19000))
            dev_cost = money({"Discover": 110000, "Pilot": 210000, "Expand": 185000, "Scale": 145000}[stage] * random.uniform(0.72, 1.32))
            margin = round(clamp(base_margin + seasonal + random.uniform(-0.028, 0.025), 0.31, 0.81), 3)
            churn_risk = round(clamp(0.18 - (margin - 0.5) / 3 + random.uniform(-0.035, 0.045), 0.04, 0.31), 3)
            uptime = round(clamp(0.985 + random.uniform(-0.014, 0.011), 0.946, 0.999), 4)
            backlog_defects = int(clamp(random.gauss(9, 4) + (0.98 - uptime) * 180, 0, 28))
            hipaa_incidents = 0 if random.random() > 0.035 else 1
            pipeline = money(arr * random.uniform(0.18, 0.52))
            nrr = round(clamp(float(product["retention_rate"]) + growth + random.uniform(-0.025, 0.031), 0.79, 1.13), 3)
            rows.append(
                {
                    "month": month,
                    "product_id": product["product_id"],
                    "active_clients": active_clients,
                    "transaction_volume": transactions,
                    "arr": arr,
                    "implementation_cost": implementation_cost,
                    "support_cost": support_cost,
                    "development_cost": dev_cost,
                    "gross_margin_rate": margin,
                    "churn_risk": churn_risk,
                    "uptime_rate": uptime,
                    "backlog_defects": backlog_defects,
                    "hipaa_incidents": hipaa_incidents,
                    "sales_pipeline": pipeline,
                    "net_revenue_retention": nrr,
                }
            )
    return rows


def generate_market_signals(products):
    rows = []
    for product in products:
        segment_factor = SEGMENT_FACTORS[product["customer_segment"]]
        stage = product["stage"]
        market_size = round(segment_factor["market_size"] * random.uniform(0.62, 1.42), 2)
        cagr = round(clamp(segment_factor["cagr"] + random.uniform(-0.024, 0.031), 0.044, 0.172), 3)
        competitor_count = int(clamp(random.gauss(7, 2.5), 3, 14))
        avg_price = money(random.uniform(180000, 880000) * (1 + market_size / 12))
        our_price = money(avg_price * random.uniform(0.82, 1.18))
        price_position = round((our_price / avg_price) - 1, 3)
        differentiation = int(clamp(54 + cagr * 180 + random.uniform(-14, 18), 40, 92))
        urgency = int(clamp(48 + market_size * 5 + random.uniform(-18, 20), 32, 96))
        entry_barrier = int(clamp(segment_factor["regulatory"] + competitor_count * 1.5 + random.uniform(-12, 9), 45, 96))
        rows.append(
            {
                "product_id": product["product_id"],
                "market_size_b": market_size,
                "market_cagr": cagr,
                "competitor_count": competitor_count,
                "avg_competitor_annual_price": avg_price,
                "our_annual_price": our_price,
                "price_position_vs_market": price_position,
                "differentiation_score": differentiation,
                "buyer_urgency_score": urgency,
                "compliance_complexity_score": entry_barrier,
                "sales_cycle_months": segment_factor["sales_cycle"] + random.choice([-1, 0, 1, 2]),
                "market_motion": "Expand" if stage in {"Pilot", "Expand"} else "Defend and deepen",
            }
        )
    return rows


def generate_research_feedback(products):
    rows = []
    for idx in range(150):
        product = random.choice(products)
        theme, summary = random.choice(THEMES)
        research_type = random.choices(
            ["customer interview", "prospect interview", "usability test", "anonymous survey", "win loss review"],
            weights=[28, 18, 18, 26, 10],
        )[0]
        severity = random.choices(["High", "Medium", "Low"], weights=[22, 48, 30])[0]
        satisfaction = int(clamp(random.gauss(6.8, 1.6) - (1.2 if severity == "High" else 0), 2, 10))
        revenue_at_risk = money(random.uniform(18000, 210000) * (1.8 if severity == "High" else 1.0))
        minutes = int(clamp(random.gauss(19, 7) + (5 if theme == "usability friction" else 0), 4, 48))
        rows.append(
            {
                "feedback_id": f"VOC-{idx + 1:03d}",
                "product_id": product["product_id"],
                "research_type": research_type,
                "persona": random.choice(PERSONAS),
                "theme": theme,
                "severity": severity,
                "satisfaction_score": satisfaction,
                "requested_capability": summary,
                "revenue_at_risk": revenue_at_risk,
                "task_completion_minutes": minutes,
                "follow_up_owner": product["owner"],
            }
        )
    return rows


def generate_roadmap_items(products):
    rows = []
    sections = [
        "Problem statement",
        "Requirements",
        "Metric definition",
        "Release criteria",
        "Pricing impact",
        "Commercial enablement",
        "Compliance review",
    ]
    statuses = ["Discovery", "PRD drafted", "Ready for grooming", "In development", "UAT", "Blocked"]
    dependencies = ["Data engineering", "Security review", "Marketing enablement", "Client implementation", "Design research", "API contract"]
    for idx in range(72):
        product = random.choice(products)
        effort = random.choice([3, 5, 8, 13, 21])
        launch_cost = money(effort * random.uniform(14500, 34000))
        revenue_lift = money(launch_cost * random.uniform(1.4, 5.8))
        risk_reduction = int(clamp(random.gauss(18, 8), 3, 42))
        rows.append(
            {
                "epic_id": f"EPIC-{idx + 1:03d}",
                "product_id": product["product_id"],
                "jira_key": f"HPA-{random.randint(2400, 3899)}",
                "prd_section": random.choice(sections),
                "request": random.choice(THEMES)[1],
                "agile_status": random.choice(statuses),
                "effort_points": effort,
                "launch_cost": launch_cost,
                "expected_revenue_lift": revenue_lift,
                "risk_reduction_points": risk_reduction,
                "dependency": random.choice(dependencies),
                "release_quarter": random.choice(["2026 Q3", "2026 Q4", "2027 Q1"]),
                "confluence_status": random.choice(["Draft", "Ready for review", "Approved", "Needs source update"]),
            }
        )
    return rows


def generate_controls(products):
    rows = []
    controls = [
        ("Access audit", "Privacy and access"),
        ("Minimum necessary data", "Privacy and access"),
        ("Metric lineage", "Data quality"),
        ("Refresh SLA", "Data quality"),
        ("De-identification check", "Privacy and access"),
        ("Model output review", "Governance"),
        ("Client-facing documentation", "Release readiness"),
    ]
    for product in products:
        for control_name, area in controls:
            fail_rate = round(clamp(random.gauss(0.035, 0.028), 0, 0.14), 3)
            open_findings = int(clamp(random.gauss(1.2, 1.3) + fail_rate * 18, 0, 7))
            status = "Pass" if open_findings == 0 else ("Watch" if open_findings <= 2 else "Remediate")
            rows.append(
                {
                    "control_id": f"{product['product_id']}-{control_name.lower().replace(' ', '-')}",
                    "product_id": product["product_id"],
                    "control_name": control_name,
                    "control_area": area,
                    "status": status,
                    "failure_rate": fail_rate,
                    "open_findings": open_findings,
                    "owner": product["owner"],
                    "remediation_days": int(clamp(open_findings * random.uniform(3, 11), 0, 60)),
                    "privacy_review_required": "Yes" if area == "Privacy and access" and status != "Pass" else "No",
                }
            )
    return rows


def latest_by_product(monthly):
    latest_month = max(row["month"] for row in monthly)
    return {row["product_id"]: row for row in monthly if row["month"] == latest_month}


def score_outputs(products, monthly, market, feedback, roadmap, controls):
    latest = latest_by_product(monthly)
    market_by_product = {row["product_id"]: row for row in market}
    feedback_by_product = defaultdict(list)
    roadmap_by_product = defaultdict(list)
    controls_by_product = defaultdict(list)
    for row in feedback:
        feedback_by_product[row["product_id"]].append(row)
    for row in roadmap:
        roadmap_by_product[row["product_id"]].append(row)
    for row in controls:
        controls_by_product[row["product_id"]].append(row)

    profitability_rows = []
    market_rows = []
    launch_rows = []

    for product in products:
        product_id = product["product_id"]
        latest_row = latest[product_id]
        market_row = market_by_product[product_id]
        feedback_rows = feedback_by_product[product_id]
        roadmap_rows = roadmap_by_product[product_id]
        control_rows = controls_by_product[product_id]

        arr = float(latest_row["arr"])
        margin = float(latest_row["gross_margin_rate"])
        support = float(latest_row["support_cost"])
        dev = float(latest_row["development_cost"])
        implement = float(latest_row["implementation_cost"])
        pipeline = float(latest_row["sales_pipeline"])
        nrr = float(latest_row["net_revenue_retention"])
        churn = float(latest_row["churn_risk"])
        defect_penalty = int(latest_row["backlog_defects"]) * 8500
        privacy_penalty = sum(int(control["open_findings"]) for control in control_rows if control["control_area"] == "Privacy and access") * 22000
        annualized_profit = money(arr * margin - support * 12 - dev * 4 - implement / 2 - defect_penalty * 4 - privacy_penalty)
        revenue_lift = sum(float(item["expected_revenue_lift"]) for item in roadmap_rows)
        launch_cost = sum(float(item["launch_cost"]) for item in roadmap_rows)
        voc_risk = sum(float(row["revenue_at_risk"]) for row in feedback_rows if row["severity"] == "High")
        readiness = 100
        readiness -= int(churn * 90)
        readiness -= sum(int(control["open_findings"]) for control in control_rows) * 2
        readiness -= len([item for item in roadmap_rows if item["agile_status"] == "Blocked"]) * 5
        readiness += int((nrr - 0.85) * 50)
        readiness = int(clamp(readiness, 18, 96))
        profitability_score = round(
            (annualized_profit / 1000000) * 4
            + (pipeline / 1000000) * 8
            + (revenue_lift / max(launch_cost, 1)) * 10
            + readiness * 0.42
            - churn * 58
            - privacy_penalty / 80000,
            1,
        )
        lane = "Fix economics" if annualized_profit < 0 else ("Invest" if profitability_score >= 78 else ("Validate" if readiness < 62 else "Monitor"))
        profitability_rows.append(
            {
                "rank": 0,
                "product_id": product_id,
                "product_name": product["product_name"],
                "customer_segment": product["customer_segment"],
                "stage": product["stage"],
                "annualized_profit": annualized_profit,
                "arr": money(arr),
                "gross_margin_rate": margin,
                "sales_pipeline": money(pipeline),
                "revenue_lift_backlog": money(revenue_lift),
                "launch_cost_backlog": money(launch_cost),
                "churn_risk": churn,
                "readiness_score": readiness,
                "voc_revenue_at_risk": money(voc_risk),
                "priority_score": profitability_score,
                "decision_lane": lane,
                "recommended_next_step": next_step(lane),
            }
        )

        market_score = round(
            float(market_row["market_size_b"]) * 7
            + float(market_row["market_cagr"]) * 160
            + int(market_row["buyer_urgency_score"]) * 0.42
            + int(market_row["differentiation_score"]) * 0.31
            - int(market_row["competitor_count"]) * 1.8
            - abs(float(market_row["price_position_vs_market"])) * 35
            - int(market_row["sales_cycle_months"]) * 1.1,
            1,
        )
        pricing_action = "Raise value proof before price lift"
        if float(market_row["price_position_vs_market"]) < -0.08 and int(market_row["differentiation_score"]) >= 70:
            pricing_action = "Test packaging and price expansion"
        elif float(market_row["price_position_vs_market"]) > 0.1:
            pricing_action = "Defend premium with outcome evidence"
        market_rows.append(
            {
                "rank": 0,
                "product_id": product_id,
                "product_name": product["product_name"],
                "customer_segment": product["customer_segment"],
                "market_size_b": market_row["market_size_b"],
                "market_cagr": market_row["market_cagr"],
                "competitor_count": market_row["competitor_count"],
                "price_position_vs_market": market_row["price_position_vs_market"],
                "differentiation_score": market_row["differentiation_score"],
                "buyer_urgency_score": market_row["buyer_urgency_score"],
                "sales_cycle_months": market_row["sales_cycle_months"],
                "market_score": market_score,
                "pricing_action": pricing_action,
            }
        )

        approved_docs = len([item for item in roadmap_rows if item["confluence_status"] == "Approved"])
        blocked_items = len([item for item in roadmap_rows if item["agile_status"] == "Blocked"])
        open_findings = sum(int(row["open_findings"]) for row in control_rows)
        total_effort = sum(int(row["effort_points"]) for row in roadmap_rows)
        roi = round(revenue_lift / max(launch_cost, 1), 2)
        launch_score = int(clamp(readiness + approved_docs * 3 - blocked_items * 7 - open_findings * 2 + min(roi, 5) * 4, 12, 98))
        launch_rows.append(
            {
                "product_id": product_id,
                "product_name": product["product_name"],
                "release_readiness_score": launch_score,
                "approved_prd_sections": approved_docs,
                "blocked_jira_items": blocked_items,
                "open_control_findings": open_findings,
                "total_effort_points": total_effort,
                "expected_revenue_lift": money(revenue_lift),
                "estimated_launch_cost": money(launch_cost),
                "backlog_roi": roi,
                "release_recommendation": "Release candidate" if launch_score >= 76 else ("Needs remediation" if open_findings > 10 else "Keep in discovery"),
            }
        )

    profitability_rows = sorted(profitability_rows, key=lambda row: row["priority_score"], reverse=True)
    for idx, row in enumerate(profitability_rows, start=1):
        row["rank"] = idx

    market_rows = sorted(market_rows, key=lambda row: row["market_score"], reverse=True)
    for idx, row in enumerate(market_rows, start=1):
        row["rank"] = idx

    launch_rows = sorted(launch_rows, key=lambda row: row["release_readiness_score"], reverse=True)

    theme_rows = []
    theme_summary = defaultdict(lambda: {"count": 0, "high": 0, "risk": 0.0, "minutes": 0})
    for row in feedback:
        bucket = theme_summary[row["theme"]]
        bucket["count"] += 1
        bucket["high"] += 1 if row["severity"] == "High" else 0
        bucket["risk"] += float(row["revenue_at_risk"])
        bucket["minutes"] += int(row["task_completion_minutes"])
    for theme, bucket in sorted(theme_summary.items(), key=lambda item: item[1]["risk"], reverse=True):
        theme_rows.append(
            {
                "theme": theme,
                "feedback_count": bucket["count"],
                "high_severity_count": bucket["high"],
                "revenue_at_risk": money(bucket["risk"]),
                "avg_task_completion_minutes": round(bucket["minutes"] / bucket["count"], 1),
                "research_recommendation": theme_recommendation(theme),
            }
        )

    return profitability_rows, market_rows, theme_rows, launch_rows


def next_step(lane):
    return {
        "Invest": "Move to expansion business case with Marketing and Product",
        "Fix economics": "Review support cost, launch cost, and pricing assumptions",
        "Validate": "Run customer discovery and data quality review before build",
        "Monitor": "Keep in monthly product performance review",
    }[lane]


def theme_recommendation(theme):
    return {
        "pricing clarity": "Add package definitions and ROI proof to sales enablement",
        "workflow integration": "Prioritize integration requirements in the PRD",
        "metric trust": "Publish metric lineage, freshness, and calculation notes",
        "implementation speed": "Create launch checklist and implementation SLA",
        "compliance evidence": "Expose privacy and audit controls in readiness review",
        "usability friction": "Run task-based usability fixes before release",
        "competitive proof": "Turn win loss evidence into competitive positioning",
    }[theme]


def build_payload(products, monthly, market, feedback, roadmap, controls, profitability, market_queue, themes, launch):
    latest = latest_by_product(monthly)
    latest_month = max(row["month"] for row in monthly)
    total_arr = sum(float(row["arr"]) for row in latest.values())
    total_profit = sum(float(row["annualized_profit"]) for row in profitability)
    invest_count = len([row for row in profitability if row["decision_lane"] == "Invest"])
    remediation_count = len([row for row in launch if row["release_recommendation"] == "Needs remediation"])
    high_voc = len([row for row in feedback if row["severity"] == "High"])
    avg_readiness = round(sum(row["readiness_score"] for row in profitability) / len(profitability), 1)
    control_findings = sum(int(row["open_findings"]) for row in controls)
    segment_mix = Counter(product["customer_segment"] for product in products)

    return {
        "summary": {
            "latest_month": latest_month,
            "products": len(products),
            "monthly_rows": len(monthly),
            "research_records": len(feedback),
            "roadmap_items": len(roadmap),
            "total_arr": money(total_arr),
            "annualized_profit": money(total_profit),
            "invest_count": invest_count,
            "remediation_count": remediation_count,
            "high_voc_items": high_voc,
            "avg_readiness_score": avg_readiness,
            "open_control_findings": control_findings,
            "segment_mix": dict(segment_mix),
        },
        "profitability_queue": profitability[:8],
        "market_queue": market_queue[:8],
        "research_themes": themes,
        "launch_readiness": launch[:8],
        "top_products": products[:6],
    }


def write_markdown(summary, profitability, market_queue, themes, launch):
    top = profitability[0]
    top_market = market_queue[0]
    top_theme = themes[0]
    top_launch = launch[0]
    lane_article = "an" if top["decision_lane"][0].lower() in "aeiou" else "a"
    (ANALYSIS / "executive_findings.md").write_text(
        f"""# Executive Findings

## What I Analyzed

I modeled a healthcare analytics SaaS product portfolio with {summary['products']} product modules, {summary['monthly_rows']:,} monthly performance records, {summary['research_records']} customer research observations, {summary['roadmap_items']} roadmap items, and HIPAA-aware data quality controls.

## Findings

- The portfolio has ${summary['total_arr']:,.0f} in modeled ARR and ${summary['annualized_profit']:,.0f} in annualized contribution profit.
- {top['product_name']} is the top profitability priority with a score of {top['priority_score']} and {lane_article} {top['decision_lane']} lane.
- {top_market['product_name']} has the strongest market expansion score at {top_market['market_score']}.
- The highest value research theme is {top_theme['theme']}, with ${top_theme['revenue_at_risk']:,.0f} in modeled revenue at risk.
- {top_launch['product_name']} has the strongest launch readiness score at {top_launch['release_readiness_score']}.

## Recommendation

Use the workbench as a Product Analyst operating packet: validate the top research themes, pressure-test pricing and packaging, clear data quality blockers, then move the strongest product modules into an expansion business case.
""",
        encoding="utf-8",
    )

    (ANALYSIS / "analysis_plan.md").write_text(
        """# Analysis Plan

1. Model product modules across payer, provider, pharmacy, life sciences, and platform workflows.
2. Forecast ARR, operating cost, development cost, support cost, margin, churn risk, and pipeline by month.
3. Score market expansion using market size, CAGR, buyer urgency, competitor density, differentiation, pricing position, and sales cycle.
4. Summarize customer interviews, prospect interviews, surveys, win loss reviews, and usability tests into research themes.
5. Combine Jira-style roadmap items, Confluence documentation status, launch cost, revenue lift, and HIPAA-aware controls into release readiness.
6. Translate the outputs into product decisions: invest, validate, fix economics, or monitor.
""",
        encoding="utf-8",
    )

    (ANALYSIS / "methodology.md").write_text(
        f"""# Methodology

The data is deterministic synthetic data generated with random seed {RANDOM_SEED}. It is modeled on common healthcare analytics SaaS product management structures, including payer quality and risk workflows, provider revenue cycle workflows, pharmacy operations, life sciences real-world evidence use cases, Agile roadmap management, and HIPAA-aware data controls.

## Scoring

- Profitability priority combines annualized contribution profit, sales pipeline, backlog ROI, launch readiness, churn risk, and privacy-control penalties.
- Market expansion score combines market size, market growth, buyer urgency, differentiation, competitor density, price position, and sales cycle.
- Launch readiness combines PRD approval, blocked Jira items, control findings, effort size, and expected backlog ROI.
- Research themes aggregate interview, survey, usability, win loss, and prospect feedback into revenue at risk and task friction.

No row represents a real company, client, patient, claim, product contract, or protected health information.
""",
        encoding="utf-8",
    )


def write_readme(summary):
    readme = f"""# Healthcare Product Profitability Intelligence Lab

An interactive Product Analyst portfolio artifact for a healthcare analytics SaaS team deciding which product modules to enhance, price, validate, or hold. The workbench connects product performance, market research, competitive pricing, customer feedback, roadmap economics, and HIPAA-aware release controls into one decision packet.

![Product profitability command center](docs/images/profitability-command-center.png)

Caption: Product profitability command center ranking modules by modeled contribution profit, pipeline, backlog ROI, churn risk, readiness, and customer revenue at risk.

![Market and pricing strategy](docs/images/market-pricing-strategy.png)

Caption: Market and pricing view comparing expansion attractiveness, competitor density, price position, buyer urgency, and packaging actions.

![Research evidence](docs/images/research-evidence.png)

Caption: Customer research view showing interview themes, usability friction, high-severity feedback, modeled revenue at risk, and product recommendations.

## What This Project Demonstrates

- Product profitability analysis for healthcare analytics software modules.
- Market research synthesis, competitive pricing interpretation, and packaging recommendations.
- Voice-of-customer research using interviews, surveys, usability tests, and win loss reviews.
- Agile product documentation thinking across PRD sections, Jira epics, release readiness, and cross-functional dependencies.
- HIPAA-aware product analytics that treats privacy, access, metric lineage, and release controls as part of the product decision.

## Data

All data is deterministic synthetic data generated by `scripts/score_operating_data.py`. It does not represent real company performance, real clients, real patients, real claims, real contracts, or protected health information.

The synthetic data is modeled on common healthcare analytics SaaS structures:

- Payer workflows such as quality measurement, risk adjustment, interoperability, and value-based contract analytics.
- Provider workflows such as revenue cycle denials, eligibility verification, record review, and operational benchmarking.
- Pharmacy workflows such as adherence, claims reconciliation, medication therapy management, and prior authorization analytics.
- Life sciences workflows such as real-world evidence cohorts, clinical trial feasibility, and commercial analytics segmentation.
- Product operations artifacts such as PRD sections, Jira epics, Confluence documentation status, launch cost, revenue lift, and data quality controls.

Generated datasets include:

| File | Grain | Purpose |
|---|---|---|
| `data/product_modules.csv` | Product module | Segment, workflow, stage, owner, ARR, margin, retention, and target persona |
| `data/monthly_product_performance.csv` | Product module by month | ARR, costs, margin, transactions, churn risk, defects, pipeline, and retention |
| `data/market_competitive_signals.csv` | Product module | Market size, growth, competitor count, pricing position, and buyer urgency |
| `data/research_feedback.csv` | Research observation | Interview, survey, usability, prospect, and win loss feedback |
| `data/roadmap_prd_items.csv` | Roadmap item | Jira-style epics, PRD sections, dependencies, launch cost, and revenue lift |
| `data/data_quality_controls.csv` | Product control | HIPAA-aware privacy, access, metric lineage, refresh, and release controls |

## Analysis Outputs

| File | Purpose |
|---|---|
| `analysis/outputs/product_profitability_queue.csv` | Ranked product decision queue |
| `analysis/outputs/market_expansion_queue.csv` | Market and pricing opportunity ranking |
| `analysis/outputs/research_theme_summary.csv` | Voice-of-customer theme summary |
| `analysis/outputs/roadmap_launch_readiness.csv` | Launch readiness and roadmap economics |
| `analysis/outputs/app_payload.json` | Data powering the interactive workbench |
| `analysis/sql_checks.sql` | SQL patterns for validating portfolio, research, roadmap, and control logic |

## Role Fit

This artifact mirrors the work of a Product Analyst who must turn market research, financial forecasting, product performance, customer feedback, pricing strategy, and Agile documentation into clear recommendations for Product, Development, Marketing, and client-facing stakeholders.

## Run Locally

```bash
npm run analyze
npm start
```

Then open `http://localhost:4173`.

## Scope

This is a static portfolio artifact with reproducible synthetic data and transparent scoring. It does not connect to live healthcare systems, production analytics platforms, Jira, Confluence, billing systems, claims systems, electronic health records, client environments, or any source that contains protected health information. It shows how a Product Analyst can structure a defensible healthcare product profitability and market expansion workflow.
"""
    Path(ROOT / "README.md").write_text(readme, encoding="utf-8")


def write_data_docs():
    (DATA / "README.md").write_text(
        """# Data README

The CSV files in this folder are deterministic synthetic data for a public portfolio artifact. They do not represent real company performance, real clients, real patients, real claims, real contracts, or protected health information.

The generator models common healthcare analytics SaaS product structures across payer, provider, pharmacy, life sciences, and platform workflows. Product economics, market signals, research feedback, roadmap records, and controls are shaped to support product profitability, market research, pricing, VOC synthesis, Agile documentation, and HIPAA-aware release readiness analysis.
""",
        encoding="utf-8",
    )

    (ROOT / "data_dictionary.md").write_text(
        """# Data Dictionary

| Table | Grain | Purpose |
|---|---|---|
| `data/product_modules.csv` | Product module | Product portfolio metadata, stage, workflow, owner, baseline clients, ARR, margin, retention, and persona |
| `data/monthly_product_performance.csv` | Product module by month | Product performance, costs, margin, transaction volume, defects, HIPAA incidents, pipeline, and retention |
| `data/market_competitive_signals.csv` | Product module | Market size, CAGR, competitor density, pricing position, differentiation, buyer urgency, and sales cycle |
| `data/research_feedback.csv` | Feedback observation | Interview, survey, usability, prospect, and win loss feedback themes |
| `data/roadmap_prd_items.csv` | Roadmap item | Jira-style epics, PRD sections, Agile status, effort, launch cost, revenue lift, dependency, and documentation state |
| `data/data_quality_controls.csv` | Product control | Privacy, access, lineage, refresh, governance, and release readiness controls |
| `analysis/outputs/product_profitability_queue.csv` | Product module | Ranked decision queue for invest, validate, fix economics, or monitor recommendations |
| `analysis/outputs/market_expansion_queue.csv` | Product module | Market and pricing opportunity score |
| `analysis/outputs/research_theme_summary.csv` | Feedback theme | VOC theme summary with revenue at risk and usability friction |
| `analysis/outputs/roadmap_launch_readiness.csv` | Product module | Launch readiness, blocked work, documentation, control findings, ROI, and release recommendation |
| `analysis/outputs/app_payload.json` | App payload | Consolidated data used by the browser workbench |
""",
        encoding="utf-8",
    )


def write_sql():
    (ANALYSIS / "sql_checks.sql").write_text(
        """-- SQL patterns for validating the synthetic healthcare product profitability artifact.

-- 1. Product profitability queue inputs.
SELECT
  p.product_id,
  p.product_name,
  m.month,
  m.arr,
  m.gross_margin_rate,
  m.support_cost,
  m.development_cost,
  m.sales_pipeline,
  m.churn_risk
FROM product_modules p
JOIN monthly_product_performance m
  ON p.product_id = m.product_id
WHERE m.month = (SELECT MAX(month) FROM monthly_product_performance);

-- 2. Market and pricing opportunity.
SELECT
  p.customer_segment,
  AVG(s.market_size_b) AS avg_market_size_b,
  AVG(s.market_cagr) AS avg_market_cagr,
  AVG(s.price_position_vs_market) AS avg_price_position,
  AVG(s.buyer_urgency_score) AS avg_buyer_urgency
FROM product_modules p
JOIN market_competitive_signals s
  ON p.product_id = s.product_id
GROUP BY p.customer_segment;

-- 3. Voice-of-customer risk by theme.
SELECT
  theme,
  COUNT(*) AS feedback_count,
  SUM(CASE WHEN severity = 'High' THEN 1 ELSE 0 END) AS high_severity_count,
  SUM(revenue_at_risk) AS revenue_at_risk,
  AVG(task_completion_minutes) AS avg_task_completion_minutes
FROM research_feedback
GROUP BY theme
ORDER BY revenue_at_risk DESC;

-- 4. Launch blockers by product.
SELECT
  p.product_id,
  p.product_name,
  SUM(CASE WHEN r.agile_status = 'Blocked' THEN 1 ELSE 0 END) AS blocked_jira_items,
  SUM(c.open_findings) AS open_control_findings,
  SUM(r.expected_revenue_lift) / NULLIF(SUM(r.launch_cost), 0) AS backlog_roi
FROM product_modules p
LEFT JOIN roadmap_prd_items r
  ON p.product_id = r.product_id
LEFT JOIN data_quality_controls c
  ON p.product_id = c.product_id
GROUP BY p.product_id, p.product_name
ORDER BY open_control_findings DESC;

-- 5. HIPAA-aware control watchlist.
SELECT
  product_id,
  control_name,
  control_area,
  status,
  failure_rate,
  open_findings,
  privacy_review_required
FROM data_quality_controls
WHERE status <> 'Pass'
ORDER BY open_findings DESC, failure_rate DESC;
""",
        encoding="utf-8",
    )


def write_status(summary):
    (ROOT / "STATUS.md").write_text(
        f"""# Status

- Project: Healthcare Product Profitability Intelligence Lab
- GitHub: https://github.com/Saurav-Kanegaonkar/Healthcare-Product-Profitability-Intelligence-Lab
- Status: upgraded through the Portfolio Artifact Upgrade Workflow.
- Artifact type: healthcare analytics SaaS product profitability and market expansion workbench.
- Modeled products: {summary['products']}
- Synthetic monthly performance rows: {summary['monthly_rows']}
- Research observations: {summary['research_records']}
- Resume Link Ready: Yes, after screenshots are regenerated and changes are pushed.
""",
        encoding="utf-8",
    )


def main():
    DATA.mkdir(exist_ok=True)
    ANALYSIS.mkdir(exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    products = generate_product_modules()
    monthly = generate_monthly_performance(products)
    market = generate_market_signals(products)
    feedback = generate_research_feedback(products)
    roadmap = generate_roadmap_items(products)
    controls = generate_controls(products)
    profitability, market_queue, themes, launch = score_outputs(products, monthly, market, feedback, roadmap, controls)
    payload = build_payload(products, monthly, market, feedback, roadmap, controls, profitability, market_queue, themes, launch)
    summary = payload["summary"]

    write_csv(DATA / "product_modules.csv", products, list(products[0].keys()))
    write_csv(DATA / "monthly_product_performance.csv", monthly, list(monthly[0].keys()))
    write_csv(DATA / "market_competitive_signals.csv", market, list(market[0].keys()))
    write_csv(DATA / "research_feedback.csv", feedback, list(feedback[0].keys()))
    write_csv(DATA / "roadmap_prd_items.csv", roadmap, list(roadmap[0].keys()))
    write_csv(DATA / "data_quality_controls.csv", controls, list(controls[0].keys()))
    write_csv(OUTPUTS / "product_profitability_queue.csv", profitability, list(profitability[0].keys()))
    write_csv(OUTPUTS / "market_expansion_queue.csv", market_queue, list(market_queue[0].keys()))
    write_csv(OUTPUTS / "research_theme_summary.csv", themes, list(themes[0].keys()))
    write_csv(OUTPUTS / "roadmap_launch_readiness.csv", launch, list(launch[0].keys()))

    with (OUTPUTS / "app_payload.json").open("w") as file:
        json.dump(payload, file, indent=2)

    write_markdown(summary, profitability, market_queue, themes, launch)
    write_readme(summary)
    write_data_docs()
    write_sql()
    write_status(summary)

    print(f"Generated {summary['products']} product modules.")
    print(f"Modeled ARR: ${summary['total_arr']:,.0f}")
    print(f"Top priority: {profitability[0]['product_name']} ({profitability[0]['decision_lane']})")
    print(f"Top market opportunity: {market_queue[0]['product_name']}")


if __name__ == "__main__":
    main()
