const pool = require('../config/database');

exports.me = async (req, res, next) => {
  try {
    const { rows } = await pool.query('SELECT id, email, username, created_at FROM users WHERE id = $1', [req.user.id]);
    res.json(rows[0]);
  } catch (error) {
    next(error);
  }
};

exports.list = async (_req, res, next) => {
  try {
    const { rows } = await pool.query('SELECT id, email, username FROM users ORDER BY created_at DESC LIMIT 50');
    res.json(rows);
  } catch (error) {
    next(error);
  }
};
