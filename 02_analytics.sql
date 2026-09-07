-- ============================================================
-- Analytics marts: ARPU, churn, retention  (customer-care & marketing)
-- ============================================================

-- ARPU (Average Revenue Per User) per month, joined to the subscriber dim
CREATE OR REPLACE TABLE mart_arpu AS
SELECT
    f.month_key,
    d.plan,
    d.region,
    COUNT(*) FILTER (WHERE f.active = 1)                         AS active_subs,
    ROUND(SUM(f.total_billed), 2)                               AS revenue,
    ROUND(SUM(f.total_billed) / NULLIF(COUNT(*) FILTER (WHERE f.active = 1), 0), 2) AS arpu
FROM fact_billing f
JOIN dim_subscriber d USING (subscriber_id)
GROUP BY f.month_key, d.plan, d.region
ORDER BY f.month_key, d.plan, d.region;

-- Churn: subscribers active last month but inactive this month
CREATE OR REPLACE TABLE mart_churn AS
WITH monthly AS (
    SELECT subscriber_id, month_key, active,
           LAG(active) OVER (PARTITION BY subscriber_id ORDER BY month_key) AS prev_active
    FROM fact_billing
)
SELECT
    month_key,
    COUNT(*) FILTER (WHERE prev_active = 1)                              AS base,
    COUNT(*) FILTER (WHERE prev_active = 1 AND active = 0)               AS churned,
    ROUND(100.0 * COUNT(*) FILTER (WHERE prev_active = 1 AND active = 0)
          / NULLIF(COUNT(*) FILTER (WHERE prev_active = 1), 0), 2)       AS churn_rate_pct
FROM monthly
WHERE prev_active IS NOT NULL
GROUP BY month_key
ORDER BY month_key;

-- Retention curve by signup cohort
CREATE OR REPLACE TABLE mart_retention AS
SELECT
    d.signup_month                                              AS cohort,
    f.month_key,
    ROUND(100.0 * COUNT(*) FILTER (WHERE f.active = 1) / COUNT(*), 1) AS retained_pct
FROM fact_billing f
JOIN dim_subscriber d USING (subscriber_id)
GROUP BY d.signup_month, f.month_key
ORDER BY cohort, month_key;
