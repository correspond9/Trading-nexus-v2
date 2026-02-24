--
-- Migration 025: Production Seed Data (Corrected)
-- This replaces/supplements migration 024 with safer INSERT ... ON CONFLICT logic
-- Only inserts into tables we know exist from migrations 001-023
--

-- Brokerage Plans
INSERT INTO brokerage_plans (plan_id, plan_name, description, asset_class, flat_charge, percentage_charge, created_at, updated_at, is_active) VALUES
  (1, 'PLAN_A', 'Plan A - Equity/Options - ₹20 flat', 'EQUITY_OPTIONS', 20.00, 0.000000, '2026-02-23 08:00:02.319145+00', '2026-02-23 08:00:02.319145+00', true),
  (2, 'PLAN_B', 'Plan B - Equity/Options - 0.2% turnover', 'EQUITY_OPTIONS', 0.00, 0.002000, '2026-02-23 08:00:02.319145+00', '2026-02-23 08:00:02.319145+00', true),
  (3, 'PLAN_C', 'Plan C - Equity/Options - 0.3% turnover', 'EQUITY_OPTIONS', 0.00, 0.003000, '2026-02-23 08:00:02.319145+00', '2026-02-23 08:00:02.319145+00', true),
  (4, 'PLAN_D', 'Plan D - Equity/Options - 0.4% turnover', 'EQUITY_OPTIONS', 0.00, 0.004000, '2026-02-23 08:00:02.319145+00', '2026-02-23 08:00:02.319145+00', true),
  (5, 'PLAN_E', 'Plan E - Equity/Options - 0.5% turnover', 'EQUITY_OPTIONS', 0.00, 0.005000, '2026-02-23 08:00:02.319145+00', '2026-02-23 08:00:02.319145+00', true),
  (6, 'PLAN_A_FUTURES', 'Plan A - Futures - ₹20 flat', 'FUTURES', 20.00, 0.000000, '2026-02-23 08:00:02.319145+00', '2026-02-23 08:00:02.319145+00', true),
  (7, 'PLAN_B_FUTURES', 'Plan B - Futures - 0.02% turnover', 'FUTURES', 0.00, 0.000200, '2026-02-23 08:00:02.319145+00', '2026-02-23 08:00:02.319145+00', true),
  (8, 'PLAN_C_FUTURES', 'Plan C - Futures - 0.03% turnover', 'FUTURES', 0.00, 0.000300, '2026-02-23 08:00:02.319145+00', '2026-02-23 08:00:02.319145+00', true),
  (9, 'PLAN_D_FUTURES', 'Plan D - Futures - 0.04% turnover', 'FUTURES', 0.00, 0.000400, '2026-02-23 08:00:02.319145+00', '2026-02-23 08:00:02.319145+00', true),
  (10, 'PLAN_E_FUTURES', 'Plan E - Futures - 0.05% turnover', 'FUTURES', 0.00, 0.000500, '2026-02-23 08:00:02.319145+00', '2026-02-23 08:00:02.319145+00', true),
  (51, 'PLAN_NIL', 'Plan NIL - Equity/Options - ₹0 (no brokerage)', 'EQUITY_OPTIONS', 0.00, 0.000000, '2026-02-23 09:52:53.627318+00', '2026-02-23 09:52:53.627318+00', true),
  (52, 'PLAN_NIL_FUTURES', 'Plan NIL - Futures - ₹0 (no brokerage)', 'FUTURES', 0.00, 0.000000, '2026-02-23 09:52:53.634859+00', '2026-02-23 09:52:53.634859+00', true)
ON CONFLICT (plan_id) DO UPDATE SET
  plan_name = EXCLUDED.plan_name,
  description = EXCLUDED.description,
  asset_class = EXCLUDED.asset_class,
  flat_charge = EXCLUDED.flat_charge,
  percentage_charge = EXCLUDED.percentage_charge,
  updated_at = EXCLUDED.updated_at,
  is_active = EXCLUDED.is_active;

-- If migration 024 hasn't run yet, skip it and rely on this one instead
-- This migration is idempotent and handles duplicates via ON CONFLICT
