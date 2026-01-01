const { Router } = require('express');
const pool = require('../config/database');
const logger = require('../config/logger');

const router = Router();

router.get('/users', async (_req, res, next) => {
  try {
    const result = await pool.query('SELECT id, username, email, created_at FROM users LIMIT 20');
    res.json(result.rows);
  } catch (error) {
    logger.error('Failed to list users', { error });
    next(error);
  }
});

module.exports = router;
