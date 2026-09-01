# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Project Overview
# MAGIC %md
# MAGIC # 💰 The AI Compensation Premium — From Scratch
# MAGIC ## What Is AI Talent Worth in 2026?
# MAGIC
# MAGIC **Your Mission:** Build a Bronze → Silver → Gold data pipeline that answers: **How much more do AI/ML roles earn compared to other tech roles?**
# MAGIC
# MAGIC ### The Data (already in your volume):
# MAGIC - **100 tech compensation survey records** from Jan–Apr 2026
# MAGIC - Path: `/Volumes/dbacademy/get_started_de/compensation_data/`
# MAGIC - Columns: `response_id`, `survey_date`, `company_name`, `job_title`, `location`, `years_experience`, `base_salary`, `equity_value`, `bonus`, `submitted_at`
# MAGIC - 12 job titles including Data Scientist, ML Engineer, Software Engineer, Product Manager, Engineering Manager, Data Analyst, Business Analyst, and more
# MAGIC
# MAGIC ### What You Build:
# MAGIC 🥉 **Bronze** — Load raw data from CSV into a table  
# MAGIC 🥈 **Silver** — Clean, categorize roles (AI vs non-AI), calculate total comp  
# MAGIC 🥇 **Gold** — Calculate the AI premium by role and by location
# MAGIC
# MAGIC ### Rules:
# MAGIC - **Write all the SQL yourself** — no copy-pasting from the reference notebook
# MAGIC - Use `USE CATALOG dbacademy; USE SCHEMA get_started_de;` at the top
# MAGIC - Ask the assistant for hints if you get stuck

# COMMAND ----------

# DBTITLE 1,Step 1: Preview the Data
# MAGIC %md
# MAGIC ---
# MAGIC ## Step 1: Preview the Data
# MAGIC
# MAGIC Before building anything, explore the raw data in the volume.
# MAGIC
# MAGIC **Your task:** Write a SQL query to preview the first 10 rows from the CSV file using `read_files()`.
# MAGIC
# MAGIC Hints:
# MAGIC - Use `SELECT * FROM read_files('path', format => 'csv', header => true)`
# MAGIC - The path is: `/Volumes/dbacademy/get_started_de/compensation_data/`
# MAGIC - Use `LIMIT 10`

# COMMAND ----------

# DBTITLE 1,Step 1 - Preview Query
# MAGIC %sql
# MAGIC select * from read_files('/Volumes/dbacademy/get_started_de/compensation_data/survey_q1_2026.csv')
# MAGIC limit 10

# COMMAND ----------

# DBTITLE 1,Step 2: Bronze Layer
# MAGIC %md
# MAGIC ---
# MAGIC ## Step 2: Build the Bronze Layer
# MAGIC
# MAGIC Create a table called `compensation_bronze` that loads all records from the CSV.
# MAGIC
# MAGIC **Requirements:**
# MAGIC - Table name: `compensation_bronze`
# MAGIC - Use `CREATE OR REPLACE TABLE ... AS SELECT ... FROM read_files(...)`
# MAGIC - Select all columns: `response_id`, `survey_date`, `company_name`, `job_title`, `location`, `years_experience`, `base_salary`, `equity_value`, `bonus`, `submitted_at`
# MAGIC - Don't transform anything yet — that's Silver's job
# MAGIC - Add a `SELECT COUNT(*)` at the end to verify it loaded

# COMMAND ----------

# DBTITLE 1,Step 2 - Bronze Query
# MAGIC %sql
# MAGIC -- Set your catalog and schema
# MAGIC USE CATALOG dbacademy;
# MAGIC USE SCHEMA get_started_de;
# MAGIC
# MAGIC create or replace table comp_table_bronze as
# MAGIC select * from read_files('/Volumes/dbacademy/get_started_de/compensation_data/survey_q1_2026.csv')
# MAGIC
# MAGIC

# COMMAND ----------

# DBTITLE 1,Step 3: Silver Layer
# MAGIC %md
# MAGIC ---
# MAGIC ## Step 3: Build the Silver Layer
# MAGIC
# MAGIC Transform `compensation_bronze` into `compensation_silver` with these rules:
# MAGIC
# MAGIC 1. **Filter:** Only keep rows where `base_salary IS NOT NULL AND base_salary > 40000`
# MAGIC 2. **Categorize roles** into a `role_category` column using `CASE WHEN`:
# MAGIC    - AI/ML: job titles containing 'DATA SCIENTIST', 'ML ENGINEER', 'MACHINE LEARNING'
# MAGIC    - Software Engineering: titles containing 'SOFTWARE ENGINEER'
# MAGIC    - Engineering Manager: titles containing 'ENGINEERING MANAGER'
# MAGIC    - Product Manager: titles containing 'PRODUCT MANAGER'
# MAGIC    - Data Analyst: titles containing 'DATA ANALYST' or 'BUSINESS ANALYST'
# MAGIC    - ELSE 'Other'
# MAGIC 3. **Calculate total comp:** `base_salary + COALESCE(equity_value, 0) + COALESCE(bonus, 0) AS total_comp`
# MAGIC 4. **Clean job title:** `UPPER(TRIM(job_title)) AS job_title_clean`
# MAGIC 5. **Extract seniority** using CASE WHEN: look for 'SENIOR', 'STAFF', 'LEAD', 'PRINCIPAL' → else 'Mid/Junior'
# MAGIC 6. **Parse location:** `SPLIT(location, ',')[0] AS city`, `TRIM(SPLIT(location, ',')[1]) AS state`
# MAGIC 7. **Add comp band:** CASE WHEN total_comp < 100K → 'Under 100K', etc.
# MAGIC 8. **Add timestamp:** `CURRENT_TIMESTAMP() AS processed_at`
# MAGIC
# MAGIC **Functions you'll need:** `CASE WHEN`, `UPPER()`, `TRIM()`, `COALESCE()`, `SPLIT()`, `LIKE '%text%'`

# COMMAND ----------

# DBTITLE 1,Step 3 - Silver Query
# MAGIC %sql
# MAGIC USE CATALOG dbacademy;
# MAGIC USE SCHEMA get_started_de;
# MAGIC
# MAGIC create or replace table comp_table_silver as
# MAGIC select base_salary,
# MAGIC CASE
# MAGIC     WHEN UPPER(job_title) LIKE '%DATA SCIENTIST%'
# MAGIC       OR UPPER(job_title) LIKE '%ML ENGINEER%'
# MAGIC       OR UPPER(job_title) LIKE '%MACHINE LEARNING%'
# MAGIC     THEN 'AI/ML'
# MAGIC
# MAGIC     WHEN UPPER(job_title) LIKE '%SOFTWARE ENGINEER%'
# MAGIC       OR UPPER(job_title) LIKE '%SOFTWARE DEVELOPER%'
# MAGIC     THEN 'Software Engineer'
# MAGIC
# MAGIC     WHEN UPPER(job_title) LIKE '%DATA ENGINEER%'
# MAGIC       OR UPPER(job_title) LIKE '%DATA ANALYST%'
# MAGIC       OR UPPER(job_title) LIKE '%BUSINESS ANALYST%'
# MAGIC     THEN 'Data Analyst'
# MAGIC
# MAGIC     WHEN UPPER(job_title) LIKE '%ENGINEERING MANAGER%'
# MAGIC     THEN 'Engineering Manager'
# MAGIC
# MAGIC     WHEN UPPER(job_title) LIKE '%PRODUCT MANAGER%'
# MAGIC     THEN 'Product Manager'
# MAGIC
# MAGIC     ELSE 'Other'
# MAGIC END AS role_category, 
# MAGIC base_salary + COALESCE(equity_value, 0) + COALESCE(bonus, 0) AS total_comp,
# MAGIC UPPER(TRIM(job_title)) AS job_title_clean,
# MAGIC CASE
# MAGIC     WHEN UPPER(job_title) LIKE '%SENIOR%'
# MAGIC       OR UPPER(job_title) LIKE '%STAFF%'
# MAGIC       OR UPPER(job_title) LIKE '%LEAD%'
# MAGIC       OR UPPER(job_title) LIKE '%PRINCIPAL%'
# MAGIC     THEN 'Senior'
# MAGIC     ELSE 'Mid/Junior'
# MAGIC END AS Seniority,
# MAGIC SPLIT(location, ',')[0] AS city, TRIM(try_element_at(SPLIT(location, ','), 2)) AS state,
# MAGIC CASE
# MAGIC     WHEN total_comp < 100000 THEN 'Under $100K'
# MAGIC     WHEN total_comp < 150000 THEN '$100K–$149K'
# MAGIC     WHEN total_comp < 200000 THEN '$150K–$199K'
# MAGIC     WHEN total_comp < 250000 THEN '$200K–$249K'
# MAGIC     ELSE '$250k+'
# MAGIC END AS comp_band,
# MAGIC CURRENT_TIMESTAMP() AS processed_at
# MAGIC from comp_table_bronze
# MAGIC where base_salary is not null and base_salary > 40000
# MAGIC

# COMMAND ----------

# DBTITLE 1,Step 4: Gold Layer
# MAGIC %md
# MAGIC ---
# MAGIC ## Step 4: Build the Gold Layer
# MAGIC
# MAGIC Create TWO Gold tables that answer the business question.
# MAGIC
# MAGIC ### Gold Table 1: `ai_compensation_premium`
# MAGIC Median total compensation by role category.
# MAGIC
# MAGIC - `GROUP BY role_category`
# MAGIC - Use `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_comp)` for median
# MAGIC - Also calculate median base salary and average total comp
# MAGIC - `COUNT(*) AS sample_size`
# MAGIC - `HAVING COUNT(*) >= 5` (small dataset, so low threshold)
# MAGIC - `ORDER BY median_total_comp DESC`
# MAGIC - Add `SELECT * FROM ai_compensation_premium` at the end to see results
# MAGIC
# MAGIC ### Gold Table 2: `ai_premium_by_state_seniority`
# MAGIC What is the AI premium when controlling for BOTH state AND seniority? Compare AI/ML vs Software Engineer at the same seniority level in the same state.
# MAGIC
# MAGIC **Why this matters:** Without controlling for seniority and geography, the comparison is unfair — if AI/ML roles skew junior and SWE roles skew senior, or if they're concentrated in different states, the median will be misleading. This table gives a true apples-to-apples comparison.
# MAGIC
# MAGIC - Use two CTEs: one for AI/ML median by state AND seniority, one for Software Engineer median by state AND seniority
# MAGIC - Join them on BOTH `state` AND `Seniority`
# MAGIC - Calculate `premium_amount` (ai_median - swe_median) and `premium_percent`
# MAGIC - `HAVING COUNT(*) >= 2` in each CTE
# MAGIC - `ORDER BY premium_percent DESC`
# MAGIC - Add `SELECT * FROM ai_premium_by_state_seniority` at the end

# COMMAND ----------

# DBTITLE 1,Step 4 - Gold Table 1
# MAGIC %sql
# MAGIC USE CATALOG dbacademy;
# MAGIC USE SCHEMA get_started_de;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE median_comp_by_role AS
# MAGIC select role_category, median(total_comp) as median_total_comp, median(base_salary) AS median_base_salary, avg(total_comp) AS avg_total_comp, count(*) as sample_size
# MAGIC FROM comp_table_silver
# MAGIC group by role_category
# MAGIC HAVING COUNT(*) >= 5
# MAGIC ORDER BY median_total_comp DESC;
# MAGIC
# MAGIC SELECT * FROM median_comp_by_role

# COMMAND ----------

# DBTITLE 1,Step 4 - Gold Table 2
# MAGIC %sql
# MAGIC USE CATALOG dbacademy;
# MAGIC USE SCHEMA get_started_de;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE ai_premium_by_state_seniority AS
# MAGIC WITH ai_by_state_seniority AS (
# MAGIC   SELECT state, Seniority, median(total_comp) AS ai_median_comp, COUNT(*) AS ai_sample_size
# MAGIC   FROM comp_table_silver
# MAGIC   WHERE role_category = 'AI/ML'
# MAGIC     AND state IS NOT NULL
# MAGIC   GROUP BY state, Seniority
# MAGIC   
# MAGIC ),
# MAGIC swe_by_state_seniority AS (
# MAGIC   SELECT state, Seniority, median(total_comp) AS swe_median_comp, COUNT(*) AS swe_sample_size
# MAGIC   FROM comp_table_silver
# MAGIC   WHERE role_category = 'Software Engineer'
# MAGIC     AND state IS NOT NULL
# MAGIC   GROUP BY state, Seniority
# MAGIC  
# MAGIC )
# MAGIC SELECT 
# MAGIC   ai.state,
# MAGIC   ai.Seniority,
# MAGIC   ai.ai_median_comp,
# MAGIC   swe.swe_median_comp,
# MAGIC   (ai.ai_median_comp - swe.swe_median_comp) AS premium_amount,
# MAGIC   ROUND(((ai.ai_median_comp - swe.swe_median_comp) / swe.swe_median_comp * 100), 1) AS premium_percent,
# MAGIC   ai.ai_sample_size,
# MAGIC   swe.swe_sample_size
# MAGIC FROM ai_by_state_seniority ai
# MAGIC INNER JOIN swe_by_state_seniority swe ON ai.state = swe.state AND ai.Seniority = swe.Seniority
# MAGIC ORDER BY premium_percent DESC;
# MAGIC
# MAGIC SELECT * FROM ai_premium_by_state_seniority;
# MAGIC

# COMMAND ----------

# DBTITLE 1,Step 5: Verify Results
# MAGIC %md
# MAGIC ---
# MAGIC ## Step 5: Verify Your Results
# MAGIC
# MAGIC Write queries to check your work:
# MAGIC
# MAGIC 1. How many records are in Bronze? What companies are in the data?
# MAGIC 2. Show 10 AI/ML records from Silver — do the transformations look right?
# MAGIC 3. Show the full `ai_compensation_premium` table — what's the AI premium?
# MAGIC 4. Show `ai_premium_by_state_seniority` — which state has the biggest premium?
# MAGIC 5. **Bonus:** Calculate the exact AI vs Software Engineering premium percentage

# COMMAND ----------

# DBTITLE 1,Step 5 - Verification Queries
# MAGIC %sql
# MAGIC select * from comp_table_bronze

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 'TOTAL' AS company_name, COUNT(*) AS total_rows FROM comp_table_bronze
# MAGIC UNION ALL
# MAGIC SELECT company_name, COUNT(*) AS total_rows
# MAGIC FROM comp_table_bronze
# MAGIC GROUP BY company_name
# MAGIC ORDER BY total_rows DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from comp_table_silver
# MAGIC where role_category == 'AI/ML'
# MAGIC limit 10

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from dbacademy.get_started_de.median_comp_by_role

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from dbacademy.get_started_de.ai_premium_by_state_seniority

# COMMAND ----------

# MAGIC %sql
# MAGIC with ai_median as (
# MAGIC select median_total_comp
# MAGIC from median_comp_by_role
# MAGIC where role_category = 'AI/ML'
# MAGIC ),
# MAGIC
# MAGIC swe_median as (
# MAGIC select median_total_comp
# MAGIC from median_comp_by_role
# MAGIC where role_category = 'Software Engineer'
# MAGIC )
# MAGIC
# MAGIC select ai.median_total_comp, swe.median_total_comp, (ai.median_total_comp - swe.median_total_comp)/ swe.median_total_comp as premium_percent
# MAGIC from ai_median ai, swe_median swe