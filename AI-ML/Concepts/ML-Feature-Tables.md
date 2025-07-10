# Feature Tables
A **feature table** (also called a feature store table) is a centralized data structure that contains pre-computed, transformation-ready features for machine learning models. It serves as a bridge between raw data and ML model training/inference.

## Key Characteristics

**Structured Storage**: Feature tables organize data with each row representing an entity (like a customer, product, or transaction) and each column representing a specific feature or attribute that's relevant for ML predictions.

**Pre-processed Features**: Instead of storing raw data, feature tables contain engineered features that have been cleaned, transformed, and aggregated. For example, rather than storing individual transaction records, a feature table might contain "total_purchases_last_30_days" or "average_transaction_amount."

**Time-aware**: Many feature tables include temporal aspects, storing features at different points in time or with time-based aggregations to support both training on historical data and real-time inference.

## Common Use Cases

Feature tables are particularly valuable for:
- **Model Training**: Providing consistent, high-quality features across different ML experiments
- **Real-time Inference**: Enabling fast feature lookup during model serving
- **Feature Sharing**: Allowing multiple teams and models to reuse the same engineered features
- **Data Lineage**: Tracking how features are derived from source data

## Example Structure

A customer feature table might look like:
```
customer_id | total_orders_6m | avg_order_value | days_since_last_order | preferred_category
12345      | 8               | 67.50           | 12                   | electronics
67890      | 15              | 34.20           | 3                    | clothing
```

Feature tables are essential infrastructure in modern ML platforms, helping teams avoid duplicate feature engineering work and ensuring consistency between training and production environments.
