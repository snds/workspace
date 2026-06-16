---
name: ds-forecasting
description: >
  Time series modeling, demand and churn forecasting, anomaly detection, and forecast
  evaluation for enterprise SaaS. Use this skill whenever the conversation touches:
  time series analysis, time series decomposition, trend analysis, seasonality, ARIMA,
  SARIMA, ETS, Holt-Winters, Prophet, N-BEATS, Temporal Fusion Transformer, XGBoost
  for time series, lag features, rolling statistics, forecasting revenue, forecasting
  usage, churn prediction, survival analysis, Kaplan-Meier, Cox Proportional Hazards,
  anomaly detection, Isolation Forest, CUSUM, z-score anomaly, contextual anomaly,
  collective anomaly, forecast evaluation, MAE, RMSE, MAPE, SMAPE, MASE, prediction
  intervals, or any question about predicting future values from time-ordered data.
  This skill covers forecasting and anomaly detection — not general regression or
  classification (ds-ml-engineering), not retention cohort analysis (ds-product-analytics).
aliases: [ds-forecasting]
spec_version: "2.0"
---

# DS: Forecasting

Specialist lens for time series forecasting, churn prediction, and anomaly detection in
enterprise SaaS. Part of the lead-data-scientist skill network.

---

## Domain Boundary

This skill owns **time-ordered prediction and anomaly detection**.

- **Churn scoring as a classification model** → `ds-ml-engineering` (if the output is a
  real-time score, not a survival curve)
- **Retention cohort analysis** → `ds-product-analytics`
- **Roadmap inputs from usage forecasts** → also engage `pm-roadmap-strategy`
- **Serving a forecast model as an API** → `ds-ml-engineering`

---

## Time Series Decomposition

Before modeling, decompose the series to understand its components. Modeling without
decomposition means the model is doing decomposition implicitly with no transparency.

### Additive vs. Multiplicative

- **Additive**: Y_t = Trend_t + Seasonal_t + Residual_t
  Use when: seasonal variation is roughly constant in absolute terms across the series
- **Multiplicative**: Y_t = Trend_t × Seasonal_t × Residual_t
  Use when: seasonal variation grows proportionally with the level of the series
  (common for revenue and usage metrics that grow exponentially)

Diagnostic: plot the series; if seasonal swings grow larger as the series grows, use
multiplicative or log-transform the series to make it additive.

### STL Decomposition (Seasonal and Trend Decomposition using Loess)

STL is the most robust classical decomposition method:
- Handles any type of seasonality (not just integer periods)
- Robust to outliers (won't let a single outlier destroy the seasonal estimate)
- Two parameters: seasonal smoothing window, trend smoothing window — larger = smoother

Use STL as an exploratory step before model selection. Examine the residual component:
if residuals have remaining structure, the model hasn't captured all the signal.

ACF/PACF of residuals: if either shows significant autocorrelation, the decomposition
or model is incomplete.

---

## Statistical Models

### ARIMA/SARIMA

Box-Jenkins methodology: Identify → Estimate → Diagnose.

**Identify**:
- Is the series stationary? Apply ADF or KPSS test. If not, difference (d=1 typically
  sufficient; d=2 for series with trend in trend).
- ACF (Autocorrelation Function): significant spike at lag k → MA(k) component
- PACF (Partial Autocorrelation Function): significant spike at lag k → AR(k) component
- For seasonal data: ACF/PACF at seasonal lags (12 for monthly, 7 for daily-with-weekly)
  indicate seasonal AR/MA

**SARIMA notation**: ARIMA(p,d,q)(P,D,Q)_s
- Lowercase = non-seasonal; uppercase = seasonal; s = seasonal period

**Estimate**: `statsmodels.tsa.statespace.sarimax.SARIMAX`; use AIC/BIC for model selection
among candidate orders; lower is better.

**Diagnose**: Ljung-Box test on residuals (H0: residuals are white noise); Q-Q plot;
standardized residuals should show no autocorrelation.

**Limitations**: ARIMA is univariate and assumes linearity and stationarity. It does not
naturally incorporate exogenous covariates (use ARIMAX or regress separately).

### ETS (Exponential Smoothing State Space Model)

ETS models error (E), trend (T), and seasonality (S) components each as additive (A),
multiplicative (M), or none (N).

| Specification | Use When |
|--------------|---------|
| ETS(A,N,N) | Constant level, no trend, no seasonality (simple exponential smoothing) |
| ETS(A,A,N) | Linear trend, no seasonality (Holt's linear) |
| ETS(A,A,A) | Linear trend, additive seasonality |
| ETS(A,M,M) | Multiplicative trend and seasonality (good for growing seasonal series) |

ETS frequently outperforms ARIMA on short series and series with strong seasonality,
particularly at shorter forecast horizons. Worth including in any model comparison.

`statsmodels.tsa.holtwinters.ExponentialSmoothing` for implementation.

### Holt-Winters

A specific ETS specification with trend and seasonality. Additive and multiplicative
variants correspond to ETS(A,A,A) and ETS(A,M,M) respectively.

Additive seasonality: use when seasonal amplitude is stable.
Multiplicative seasonality: use when seasonal amplitude grows with the series level.

---

## ML Models for Tabular Forecasting

### XGBoost/LightGBM with Lag Features

Frame the forecasting problem as supervised regression: predict Y_t from features
computed at time t.

Feature engineering categories:
- **Lag features**: Y_{t-1}, Y_{t-7}, Y_{t-14}, Y_{t-28}, Y_{t-365} — direct observation history
- **Rolling statistics**: rolling_mean(7), rolling_std(7), rolling_max(28) — smoothed signal
- **Expanding statistics**: expanding_mean() — long-run baseline
- **Calendar features**: day-of-week (cyclically encoded with sin/cos), month, week-of-year,
  is_holiday, days-since-holiday, quarter-end indicator (critical for SaaS)
- **Target encoding of categorical covariates**: vertical, contract tier, geo region —
  encode with group-level mean of target, with regularization to prevent leakage

**Point-in-time correctness**: Every feature must use only data available before time t.
Test this explicitly: compute features for a historical date and verify no future data leaks in.

### Direct vs. Recursive Multi-Step Forecasting

For H-step-ahead forecasting:
- **Recursive**: train a one-step model; use predictions as inputs for subsequent steps.
  Error accumulates with horizon. Better for short horizons.
- **Direct**: train a separate model for each forecast horizon h=1, 2, ..., H. No error
  accumulation. Better for longer horizons but requires H models.
- **MIMO (Multi-Input Multi-Output)**: single model with vector output [Y_{t+1}, ..., Y_{t+H}].
  Captures correlation between forecast horizons. Best approach for structured models.

At horizons beyond ~7 steps, recursive forecast quality degrades meaningfully. Switch
to direct or MIMO.

---

## Deep Learning Forecasting Models

### Prophet (Meta/Facebook)

Prophet fits an additive model: Y(t) = g(t) + s(t) + h(t) + ε

- g(t): piecewise linear or logistic trend with automatic changepoint detection
- s(t): Fourier-series seasonality (yearly, weekly, daily configurable)
- h(t): user-supplied holiday effects

**Strengths**: Fast to implement, interpretable components, handles missing data, automatic
changepoint detection is useful for exploratory analysis.

**Weaknesses**: Poor on complex multivariate relationships; not competitive with tuned ML
models on benchmarks; the additive assumption and limited trend flexibility make it brittle
for fast-growing or irregular series.

**Enterprise use case**: Good baseline and fast EDA tool. Don't ship it as the primary
production model without comparison against alternatives.

### N-BEATS (Neural Basis Expansion Analysis for Time Series)

Pure deep learning approach: stacked doubly residual neural network with basis functions
for trend and seasonality. No hand-crafted features required.

- Strong on univariate benchmarks (M4, M5 competitions)
- Interpretable variant (N-BEATS-I) decomposes output into trend + seasonality like
  classical models
- Requires more data than statistical models (~2+ full seasonal cycles minimum)
- Less straightforward to incorporate exogenous regressors than ML tabular approach

`neuralforecast` library for implementation; also available in `darts`.

### Temporal Fusion Transformer (TFT)

Attention-based multi-horizon forecasting model designed for mixed data types:
- Static covariates (account tier, industry — time-invariant)
- Known future inputs (holidays, planned promotions — time-varying but known ahead)
- Observed inputs (past values of the target and other time-varying features)

TFT outputs quantile forecasts (e.g., P10, P50, P90) natively — excellent for uncertainty
quantification. Interpretability via variable importance and attention weights.

Requires significant data: typically 1000+ time series or a single long series.
Implemented in PyTorch Forecasting, `neuralforecast`, `darts`.

---

## Churn Prediction as Survival Analysis

Framing churn as a classification problem (will this account churn in the next 30 days?)
is valid for operational scoring. Framing it as survival analysis answers richer questions:
when will they churn, and what features predict time-to-churn?

### Kaplan-Meier Estimator

Non-parametric survival curve estimation: S(t) = P(survival > t).

Use for:
- Descriptive analysis of retention by cohort, segment, or acquisition channel
- Comparing survival curves between groups (log-rank test for significance)
- Understanding the distribution of customer lifetime

No covariates — purely descriptive. Use as the first step before modeling.

### Cox Proportional Hazards Model

Semi-parametric model: h(t|X) = h_0(t) × exp(β · X)

- h_0(t) = baseline hazard (non-parametric, estimated from data)
- β = covariate effects (interpretable as hazard ratios)
- Proportional hazards assumption: the ratio of hazard rates between individuals is
  constant over time. Test with Schoenfeld residuals.

Use for: feature importance in churn prediction, understanding which account
characteristics are most predictive of churn timing, segmenting by relative risk.

Implemented in `lifelines.CoxPHFitter`.

### Discrete-Time Hazard Models for Operational Scoring

For production churn scoring, frame as a binary classification at each time period:
"given that the account survived to time t, what is the probability of churning
in period t+1?"

Features: current values of behavioral metrics (usage trends, engagement scores,
support escalations, contract renewal proximity). Train with logistic regression or
gradient boosting on panel data (each account × time period is a row).

This produces a calibrated churn probability score per account per period, suitable for
CS workflow integration.

---

## Anomaly Detection

### Contextual vs. Point vs. Collective Anomalies

| Type | Description | Example |
|------|-------------|---------|
| Point anomaly | Single observation is anomalous relative to the overall distribution | Sudden revenue spike on a single day |
| Contextual anomaly | Observation is anomalous in context but normal globally | Sunday traffic at Monday levels |
| Collective anomaly | A sequence of observations is anomalous even if individual points are not | Gradual feature adoption decline across 2 weeks |

Contextual and collective anomalies require temporal modeling; point anomaly detection
methods will miss them.

### Statistical Methods

- **Z-score**: flag observations > k standard deviations from mean. Sensitive to non-normality
  and outliers in the estimation window. Use rolling z-score for non-stationary series.
- **IQR method**: flag observations beyond Q3 + 1.5×IQR or Q1 - 1.5×IQR. Robust to
  outliers in the estimation sample.
- **CUSUM (Cumulative Sum Control Chart)**: detects persistent shifts in mean. Accumulates
  deviations from target; signals when cumulative sum exceeds threshold. Better for
  detecting sustained changes than point anomalies.
- **Seasonal Decomposition Residuals**: after STL decomposition, apply z-score or IQR to
  residuals only — removes trend and seasonal signal before anomaly detection.

### ML Methods

- **Isolation Forest**: partitions data by random feature splits; anomalies are isolated
  in fewer splits. Contamination parameter sets expected anomaly fraction. Effective for
  high-dimensional tabular anomaly detection.
- **Local Outlier Factor (LOF)**: density-based; anomalies are points in low-density
  neighborhoods. Sensitive to hyperparameter k (neighborhood size). Better for
  density-varying distributions.
- **Autoencoder Reconstruction Error**: train an autoencoder on normal data; anomalies
  produce high reconstruction error. Requires a clean training set and threshold selection.
  Good for time series with complex patterns that statistical methods miss.

---

## Forecast Evaluation

Never evaluate a forecast by eyeballing the chart.

| Metric | Formula | Notes |
|--------|---------|-------|
| MAE | mean(|Y - Ŷ|) | Interpretable; same units as target; not scale-free |
| RMSE | sqrt(mean((Y - Ŷ)²)) | Penalizes large errors more than MAE; same units |
| MAPE | mean(|Y - Ŷ| / |Y|) × 100 | **Undefined when Y=0**; biased for small values; avoid for SaaS metrics that can be zero |
| SMAPE | mean(|Y - Ŷ| / ((|Y| + |Ŷ|)/2)) × 100 | Bounded; still undefined when both are zero; symmetric |
| MASE | MAE / MAE_naive | Scale-free; compares to naive forecast (random walk); preferred for cross-series comparison |

**Prediction interval coverage**: If you produce an 80% prediction interval, ~80% of
actuals should fall within it. Under-coverage means the model is overconfident; over-
coverage means the intervals are too wide. Report coverage explicitly.

**Evaluation window**: Always evaluate on a holdout that is chronologically after training
data. Never use random splits for time series — it leaks future information into training.

---

## Cross-Hub References

- For roadmap inputs from usage and growth forecasts → `pm-roadmap-strategy`
- For serving forecast models as APIs → `ds-ml-engineering`
- For leading indicators from product behavior → `ds-product-analytics`
