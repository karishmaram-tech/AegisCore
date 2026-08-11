const { Client } = require('pg');

async function test() {
  const credentials = [
    // aegiscore options
    { user: 'aegiscore', password: 'aegiscore', database: 'postgres' },
    { user: 'aegiscore', password: 'aegiscore', database: 'litellm' },
    { user: 'aegiscore', password: 'aegis-core', database: 'postgres' },
    { user: 'aegiscore', password: 'aegis-core', database: 'litellm' },
    { user: 'aegiscore', password: '', database: 'postgres' },
    
    // aegiscore options
    { user: 'aegiscore', password: 'aegiscore', database: 'postgres' },
    { user: 'aegiscore', password: 'aegiscore', database: 'aegiscore_web' },
    { user: 'aegiscore', password: 'aegiscore', database: 'aegiscore_web' },
    { user: 'aegiscore', password: 'aegis-core', database: 'postgres' },
    
    // postgres options
    { user: 'postgres', password: 'postgres', database: 'postgres' },
    { user: 'postgres', password: 'aegiscore', database: 'postgres' },
    { user: 'postgres', password: 'aegis-core', database: 'postgres' },
    { user: 'postgres', password: '', database: 'postgres' }
  ];

  console.log("Starting expanded database connection tests...");
  let workingClient = null;
  let workingCred = null;

  for (const cred of credentials) {
    const client = new Client({
      host: 'localhost',
      port: 15432,
      user: cred.user,
      password: cred.password,
      database: cred.database,
    });

    try {
      await client.connect();
      console.log(`\x1b[32m✔ SUCCESS:\x1b[0m Connected using user: "${cred.user}", password: "${cred.password}", database: "${cred.database}"`);
      workingClient = client;
      workingCred = cred;
      break;
    } catch (err) {
      // Print detailed error (skip database-does-not-exist errors if they are different from auth-failed)
      console.log(`\x1b[31m✘ FAILED:\x1b[0m user: "${cred.user}", password: "${cred.password}", database: "${cred.database}" - ${err.message}`);
    }
  }

  if (workingClient) {
    try {
      console.log("Checking if 'aegiscore_web' database exists...");
      const res = await workingClient.query("SELECT 1 FROM pg_database WHERE datname = 'aegiscore_web'");
      if (res.rowCount === 0) {
        console.log("Database 'aegiscore_web' does not exist. Creating it now...");
        await workingClient.query("CREATE DATABASE aegiscore_web");
        try {
          await workingClient.query(`GRANT ALL PRIVILEGES ON DATABASE aegiscore_web TO ${workingCred.user}`);
        } catch (e) {
          console.log(`Could not grant privileges to ${workingCred.user}: ${e.message}`);
        }
        console.log("\x1b[32m✔ SUCCESS:\x1b[0m Database 'aegiscore_web' created successfully!");
      } else {
        console.log("Database 'aegiscore_web' already exists.");
      }
    } catch (err) {
      console.error("Error checking/creating database:", err.message);
    } finally {
      await workingClient.end();
    }
  } else {
    console.log("\x1b[31mAll connection attempts failed. Please ensure the docker container is running on port 15432.\x1b[0m");
  }
}

test();
