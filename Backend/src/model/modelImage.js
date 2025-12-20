const db = require('./db');

const tableName = "image_results";

async function GetImage(image_url, image_hash) {
    const result = await db.query(`SELECT * FROM ${tableName} WHERE image_url = $1 OR image_hash = $2 LIMIT 1`, [image_url, image_hash]);
    return result.rows[0];
}

async function GetImageById(Id) {
    const result = await db.query(`SELECT * FROM ${tableName} WHERE id = $1`, [Id]);
    return result.rows[0];
}

async function DeleteImageById(Id) {
    const result = await db.query(`DELETE FROM ${tableName} WHERE id = $1 RETURNING *`, [Id]);
    return result.rows[0];
}

async function PostImage(data) {
    const { image_hash, image_url, mark, reason, confidence } = data;

    const query = `
        INSERT INTO ${tableName}
        (image_hash, image_url, mark, reason, confidence)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *;
    `;

    const values = [
        image_hash,
        image_url,
        mark,
        reason,
        confidence,
    ];

    const result = await db.query(query, values);
    return result.rows[0];
}

module.exports = { GetImage, GetImageById, DeleteImageById, PostImage };