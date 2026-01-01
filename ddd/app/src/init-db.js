const { Pool } = require('pg');
const { readFile } = require('fs/promises');
const path = require('path');

async function initDatabase() {
  const pool = new Pool({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
  });

  try {
    const migrationPath = path.join(__dirname, '../migrations/001_initial.sql');
    const sql = await readFile(migrationPath, 'utf8');
    await pool.query(sql);
    await pool.query(`
      INSERT INTO users (username, email, password_hash)
      VALUES ('admin', 'admin@example.com', '$2b$10$ExampleHash')
      ON CONFLICT (email) DO NOTHING;
    `);
    console.log('✅ Database initialised');
  } catch (error) {
    console.error('❌ Migration error', error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

initDatabase();
