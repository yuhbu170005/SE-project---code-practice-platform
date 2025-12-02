require("dotenv").config()
const mysql = require("mysql2/promise")
const fs = require("fs")
const path = require("path")

async function setupDatabase() {
  const connection = await mysql.createConnection({
    host: process.env.MYSQL_HOST || "localhost",
    user: process.env.MYSQL_USER || "root",
    password: process.env.MYSQL_PASSWORD || "",
  })

  try {
    console.log("Creating database and tables...")

    // Read SQL file
    const sqlFile = fs.readFileSync(path.join(__dirname, "init.sql"), "utf8")

    // Execute each statement
    const statements = sqlFile.split(";").filter((stmt) => stmt.trim())
    for (const statement of statements) {
      if (statement.trim()) {
        console.log("Executing:", statement.substring(0, 50) + "...")
        await connection.execute(statement)
      }
    }

    console.log("✓ Database setup completed successfully!")
    process.exit(0)
  } catch (error) {
    console.error("Error setting up database:", error.message)
    process.exit(1)
  } finally {
    await connection.end()
  }
}

setupDatabase()
