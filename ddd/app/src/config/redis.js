const { createClient } = require('redis');
const logger = require('./logger');

const client = createClient({ url: process.env.REDIS_URL || 'redis://redis:6379' });

client.on('error', (err) => logger.error('Redis error', { err }));
client.on('ready', () => logger.info('Redis connected')); 

client.connect();

module.exports = client;
