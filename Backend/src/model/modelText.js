const db = require('./db');

const tableName = "text_results";

async function GetText(text_hash, summary_hash) {
    const result = await db.query(`SELECT * FROM ${tableName} WHERE text_hash = $1 OR summary_hash = $2 LIMIT 1`, [text_hash, summary_hash]);
    return result.rows[0];
}

async function GetTextById(Id) {
    const result = await db.query(`SELECT * FROM ${tableName} WHERE id = $1`, [Id]);
    return result.rows[0];
}

async function PostText(data) {
    const { summary_hash, text_hash, mark, reason, confidence, urls } = data;

    const query = `
        INSERT INTO ${tableName}
        (text_hash, summary_hash, mark, reason, confidence, urls)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING *;
    `;

    const values = [
        text_hash,
        summary_hash,
        mark,
        reason,
        confidence,
        urls || null
    ];

    const result = await db.query(query, values);
    return result.rows[0];
}

module.exports = { GetText, GetTextById, PostText };