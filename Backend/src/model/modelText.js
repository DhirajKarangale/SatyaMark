const db = require('./db');

const tableName = "text_results";

async function GetText(text_hash, summary_hash) {
    if (text_hash) {
        const byText = await db.query(
            `SELECT * FROM ${tableName} WHERE text_hash = $1 LIMIT 1`,
            [text_hash]
        );
        if (byText.rows.length) return byText.rows[0];
    }

    if (summary_hash) {
        const bySummary = await db.query(
            `SELECT * FROM ${tableName} WHERE summary_hash = $1 LIMIT 1`,
            [summary_hash]
        );
        if (bySummary.rows.length) return bySummary.rows[0];
    }

    return null;
}

async function GetTextById(Id) {
    const result = await db.query(`SELECT * FROM ${tableName} WHERE id = $1`, [Id]);
    return result.rows[0];
}

async function DeleteTextById(Id) {
    const result = await db.query(`DELETE FROM ${tableName} WHERE id = $1 RETURNING *`, [Id]);
    return result.rows[0];
}

async function PostText(data) {
    const { summary_hash, text_hash, mark, reason, confidence, summary, urls } = data;

    const query = `
        INSERT INTO ${tableName}
        (text_hash, summary_hash, mark, reason, summary, confidence, urls)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING *;
    `;

    const values = [
        text_hash,
        summary_hash,
        mark,
        reason,
        summary,
        confidence,
        urls || null
    ];

    const result = await db.query(query, values);
    return result.rows[0];
}

module.exports = { GetText, GetTextById, DeleteTextById, PostText };