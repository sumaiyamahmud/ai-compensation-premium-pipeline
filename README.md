# AI Compensation Premium Pipeline

A Bronze → Silver → Gold data pipeline analyzing AI/ML compensation vs other tech roles using Databricks SQL.

## Overview

This project answers the question: **How much more do AI/ML roles earn compared to other tech roles?**

Using 100 tech compensation survey records from Q1 2026, the pipeline transforms raw CSV data through three medallion architecture layers to calculate compensation premiums by role, state, and seniority.

## Pipeline Architecture

### 🥉 Bronze Layer (`comp_table_bronze`)
- Loads raw CSV data from Unity Catalog volume
- Source: `/Volumes/dbacademy/get_started_de/compensation_data/survey_q1_2026.csv`
- 100 records with 10 columns including salary, equity, bonus, location, and job title

### 🥈 Silver Layer (`comp_table_silver`)
- Filters: `base_salary IS NOT NULL AND base_salary > 40000`
- Categorizes job titles into role groups (AI/ML, Software Engineer, Data Analyst, Engineering Manager, Product Manager, Other)
- Calculates total compensation: `base_salary + equity_value + bonus`
- Extracts seniority (Senior vs Mid/Junior) and state from location
- Assigns compensation bands

### 🥇 Gold Layer

Two gold tables answer different facets of the business question:

**`median_comp_by_role`** — Median and average total compensation by role category, filtered to groups with 5+ records.

**`ai_premium_by_state_seniority`** — AI/ML vs Software Engineer premium controlled for both state AND seniority, giving an apples-to-apples comparison.

## Key Findings

| Role Category | Median Total Comp | Sample Size |
| --- | --- | --- |
| Product Manager | $301,658 | 14 |
| Engineering Manager | $285,633 | 10 |
| Software Engineer | $276,055 | 28 |
| Data Analyst | $253,968 | 24 |
| AI/ML | $222,209 | 24 |

**Overall AI vs SWE premium: -19.5%** — AI/ML roles actually earn *less* than Software Engineers in this dataset.

When controlling for state and seniority, premiums range from +34% (MA, Senior) to -16.5% (NY, Senior).

## Technologies

- Databricks SQL
- Unity Catalog (`dbacademy.get_started_de`)
- Delta Lake
- Medallion Architecture (Bronze → Silver → Gold)

## How to Run

1. Open the notebook in Databricks
2. Run cells in order from top to bottom
3. Ensure you have access to the `dbacademy.get_started_de` schema and the `compensation_data` volume

## Data Source

Tech compensation survey data (Q1 2026) stored in `/Volumes/dbacademy/get_started_de/compensation_data/`
