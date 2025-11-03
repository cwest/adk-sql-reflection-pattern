# Test Cases: Dataplex Integration

### Test Case 1: Business Rule Application
- **User Query:** "What was the total cost of refunds last quarter?"
- **Gold Standard SQL:** 
  ```sql
  SELECT
    SUM(t.refund_amount + 15.00) AS total_refund_cost
  FROM
    `sales_domain.transactions` AS t
  WHERE
    t.txn_ts >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), QUARTER, -1)
    AND t.txn_ts < TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), QUARTER)
    AND t.refund_amount > 0
  ```

### Test Case 2: Obscure Column Name Resolution
- **User Query:** "Show me the average customer satisfaction score."
- **Gold Standard SQL:**
  ```sql
  SELECT
    AVG(f.rating) AS average_satisfaction_score
  FROM
    `customer_domain.feedback` AS f
  ```

### Test Case 3: Multiple Obscure Terms
- **User Query:** "How many new customers signed up each month?"
- **Gold Standard SQL:**
  ```sql
  SELECT
    EXTRACT(YEAR FROM c.signup_dt) AS signup_year,
    EXTRACT(MONTH FROM c.signup_dt) AS signup_month,
    COUNT(c.cust_id) AS new_customer_count
  FROM
    `customer_domain.customers` AS c
  GROUP BY
    1, 2
  ORDER BY
    1, 2
  ```
