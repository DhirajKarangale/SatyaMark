const fs = require("fs");
const path = require("path");

const folderPath = process.argv[2];

if (!folderPath) {
  console.error("❌ Please provide folder path");
  process.exit(1);
}

const folderName = path.basename(folderPath).replace(/\s+/g, "");

const files = fs.readdirSync(folderPath)
  .filter(f => /\.(png|jpg|jpeg|webp)$/i.test(f))
  .sort();

files.forEach((file, index) => {
  const ext = path.extname(file);
  const newName = `${folderName}_${index + 1}${ext}`;

  const oldPath = path.join(folderPath, file);
  const newPath = path.join(folderPath, newName);

  fs.renameSync(oldPath, newPath);
  console.log(`✔ ${file} → ${newName}`);
});

console.log("✅ Renaming completed");