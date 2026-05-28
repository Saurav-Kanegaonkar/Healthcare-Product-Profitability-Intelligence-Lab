const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  notation: "compact",
  maximumFractionDigits: 1
});

const number = new Intl.NumberFormat("en-US");
const pct = new Intl.NumberFormat("en-US", {
  style: "percent",
  maximumFractionDigits: 1
});

const laneClass = {
  Invest: "lane-invest",
  "Fix economics": "lane-fix",
  Validate: "lane-validate",
  Monitor: "lane-monitor"
};

function qs(selector) {
  return document.querySelector(selector);
}

function formatMoney(value) {
  return currency.format(Number(value));
}

function progressBar(value, max = 100) {
  const width = Math.max(4, Math.min(100, Number(value) / max * 100));
  return `<span class="bar"><span style="width:${width}%"></span></span>`;
}

function setText(selector, value) {
  qs(selector).textContent = value;
}

function renderSummary(summary) {
  setText("#latest-month", summary.latest_month);
  setText("#portfolio-arr", formatMoney(summary.total_arr));
  setText("#annual-profit", formatMoney(summary.annualized_profit));
  setText("#product-count", `${summary.products} modules`);
  setText("#invest-count", summary.invest_count);
  setText("#avg-readiness", summary.avg_readiness_score);
  setText("#high-voc", summary.high_voc_items);
  setText("#control-findings", number.format(summary.open_control_findings));
}

function renderProfitability(queue) {
  qs("#profitabilityRows").innerHTML = queue.map((row) => `
    <tr data-product="${row.product_id}">
      <td>${row.rank}</td>
      <td>
        <strong>${row.product_name}</strong>
        <span>${row.recommended_next_step}</span>
      </td>
      <td>${row.customer_segment}</td>
      <td>${formatMoney(row.annualized_profit)}</td>
      <td>
        ${row.priority_score}
        ${progressBar(row.priority_score, 300)}
      </td>
      <td><mark class="${laneClass[row.decision_lane]}">${row.decision_lane}</mark></td>
    </tr>
  `).join("");

  const focus = queue[0];
  qs("#profitabilityDetail").innerHTML = `
    <p class="eyebrow">Top decision</p>
    <h3>${focus.product_name}</h3>
    <dl>
      <div><dt>ARR</dt><dd>${formatMoney(focus.arr)}</dd></div>
      <div><dt>Pipeline</dt><dd>${formatMoney(focus.sales_pipeline)}</dd></div>
      <div><dt>Backlog ROI</dt><dd>${(focus.revenue_lift_backlog / focus.launch_cost_backlog).toFixed(1)}x</dd></div>
      <div><dt>Churn risk</dt><dd>${pct.format(focus.churn_risk)}</dd></div>
      <div><dt>VOC risk</dt><dd>${formatMoney(focus.voc_revenue_at_risk)}</dd></div>
    </dl>
    <p>${focus.recommended_next_step}.</p>
  `;
}

function renderMarket(queue) {
  qs("#marketCards").innerHTML = queue.map((row) => `
    <article class="market-card">
      <div class="card-topline">
        <span>${row.customer_segment}</span>
        <strong>${row.market_score}</strong>
      </div>
      <h3>${row.product_name}</h3>
      <div class="metric-pair">
        <span>Market</span>
        <b>$${row.market_size_b}B</b>
      </div>
      <div class="metric-pair">
        <span>CAGR</span>
        <b>${pct.format(row.market_cagr)}</b>
      </div>
      <div class="metric-pair">
        <span>Price position</span>
        <b>${pct.format(row.price_position_vs_market)}</b>
      </div>
      <div class="metric-pair">
        <span>Competitors</span>
        <b>${row.competitor_count}</b>
      </div>
      ${progressBar(row.buyer_urgency_score)}
      <p>${row.pricing_action}</p>
    </article>
  `).join("");
}

function renderResearch(themes) {
  qs("#themeBoard").innerHTML = themes.map((row, index) => `
    <article class="theme-card ${index === 0 ? "theme-card-primary" : ""}">
      <div class="card-topline">
        <span>${row.feedback_count} observations</span>
        <strong>${formatMoney(row.revenue_at_risk)}</strong>
      </div>
      <h3>${row.theme}</h3>
      <div class="theme-stats">
        <span><b>${row.high_severity_count}</b> high severity</span>
        <span><b>${row.avg_task_completion_minutes}</b> min task time</span>
      </div>
      <p>${row.research_recommendation}</p>
    </article>
  `).join("");
}

function renderLaunch(readiness) {
  qs("#launchList").innerHTML = readiness.map((row) => `
    <article class="launch-row">
      <div>
        <span>${row.release_recommendation}</span>
        <h3>${row.product_name}</h3>
      </div>
      <div class="launch-metrics">
        <span>Score <b>${row.release_readiness_score}</b></span>
        <span>PRD <b>${row.approved_prd_sections}</b></span>
        <span>Blocked <b>${row.blocked_jira_items}</b></span>
        <span>ROI <b>${row.backlog_roi}x</b></span>
      </div>
      ${progressBar(row.release_readiness_score)}
    </article>
  `).join("");
}

function wireTabs() {
  document.querySelectorAll(".tabs button").forEach((button) => {
    button.addEventListener("click", () => {
      const view = button.dataset.view;
      document.querySelectorAll(".tabs button").forEach((item) => item.classList.toggle("active", item === button));
      document.querySelectorAll(".view").forEach((section) => {
        section.classList.toggle("active", section.id === `${view}View`);
      });
    });
  });
}

async function init() {
  const response = await fetch("analysis/outputs/app_payload.json");
  const state = await response.json();
  renderSummary(state.summary);
  renderProfitability(state.profitability_queue);
  renderMarket(state.market_queue);
  renderResearch(state.research_themes);
  renderLaunch(state.launch_readiness);
  wireTabs();
}

init();
