-- SQL patterns for validating the synthetic healthcare product profitability artifact.

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
