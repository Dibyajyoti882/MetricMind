module.exports = {
  dbType: process.env.CUBEJS_DB_TYPE || 'duckdb',

  apiSecret: process.env.CUBEJS_API_SECRET || 'metricmind-local-secret',

  queryRewrite: (query, { securityContext }) => {
    if (!query.limit) {
      query.limit = 5000;
    }
    return query;
  },
};