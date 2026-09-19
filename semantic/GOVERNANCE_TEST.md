# Governance Audit — Sep 19

## Test Objective

Verify that the governed semantic layer produces identical
results across repeated queries.

## Query

- Measures: Sales.revenue, Sales.margin
- Dimensions: Sales.quarter
- Filter: Sales.region equals Europe
- Repeated Runs: 5

## Result

The same query was executed 5 times in the Cube Playground.
Revenue and margin values were identical in every run.

## Margin-Drop Validation

Europe's margin was approximately 50% in Q1/Q2
and decreased to approximately 34% in Q3.

This matches the demo story of a margin drop caused
by the Q3 shipping cost spike.

## Conclusion

The semantic layer returned consistent results across
all 5 repeated queries, confirming query consistency
for the governance test.