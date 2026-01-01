const { readdir, readFile } = require('fs/promises');
const path = require('path');
const pool = require('../src/config/database');

async function runMigrations() {
  const migrationsDir = path.join(__dirname);
  const files = (await readdir(migrationsDir))
    .filter((file) => file.endsWith('.sql'))
    .sort();

  for (const file of files) {
    const sql = await readFile(path.join(migrationsDir, file), 'utf8');
    await pool.query(sql);
    console.log(`Applied ${file}`);
  }

  await pool.end();
}

runMigrations().catch((error) => {
  console.error(error);
  process.exit(1);
});
