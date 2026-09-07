-- ============================================================
-- Telecom warehouse — star schema (dimensions + fact)
-- ============================================================

-- Dimension: subscriber
CREATE OR REPLACE TABLE dim_subscriber AS
SELECT
    subscriber_id,
    plan,
    monthly_price,
    region,
    signup_month
FROM read_csv_auto('data/raw/subscribers.csv', header=true);

-- Dimension: date (one row per billing month)
CREATE OR REPLACE TABLE dim_date AS
SELECT DISTINCT
    bill_month                                   AS month_key,
    CAST(substr(bill_month, 1, 4) AS INTEGER)    AS year,
    CAST(substr(bill_month, 6, 2) AS INTEGER)    AS month_num
FROM read_csv_auto('data/raw/billing.csv', header=true);

-- Fact: monthly billing (grain = one subscriber per month)
CREATE OR REPLACE TABLE fact_billing AS
SELECT
    b.subscriber_id,
    b.bill_month                                 AS month_key,
    b.base_charge,
    b.addons,
    b.total_billed,
    b.active
FROM read_csv_auto('data/raw/billing.csv', header=true) b;
