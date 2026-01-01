require('dotenv').config();
const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const { json, urlencoded } = express;
const logger = require('./config/logger');
const pool = require('./config/database');
const redis = require('./config/redis');

const apiRoutes = require('./routes/api');
const authRoutes = require('./routes/auth');
const userRoutes = require('./routes/users');
const errorHandler = require('./middlewares/errorHandler');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(helmet());
app.use(cors());
app.use(json());
app.use(urlencoded({ extended: true }));

app.get('/health', async (_req, res) => {
  try {
    await pool.query('SELECT 1');
    res.json({ status: 'healthy', db: 'connected' });
  } catch (error) {
    logger.error('Healthcheck failed', { error });
    res.status(500).json({ status: 'unhealthy', error: error.message });
  }
});

app.use('/api', apiRoutes);
app.use('/auth', authRoutes);
app.use('/users', userRoutes);

app.use(errorHandler);

app.listen(PORT, '0.0.0.0', () => {
  logger.info(`🚀 Server listening on port ${PORT}`, { env: process.env.NODE_ENV });
});
