const logger = require('../config/logger');

module.exports = (err, _req, res, _next) => {
  logger.error('Unhandled error', { err });
  res.status(500).json({ error: 'Something went wrong' });
};
