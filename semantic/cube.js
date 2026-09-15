module.exports = {
  dbType: process.env.CUBEJS_DB_TYPE || 'duckdb',

  queryRewrite: (query, { securityContext }) => {
    if (!query.limit) {
      query.limit = 5000;
    }
    return query;
  },
};
