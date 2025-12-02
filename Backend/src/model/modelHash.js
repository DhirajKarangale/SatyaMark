const db = require('./db');

async function GetText(originalHash, summaryHash) {
    const result = await db.query('SELECT * FROM text_results WHERE text_hash = $1 OR summary_hash = $2 LIMIT 1', [originalHash, summaryHash]);
    return result.rows[0];
}

module.exports = { GetText };