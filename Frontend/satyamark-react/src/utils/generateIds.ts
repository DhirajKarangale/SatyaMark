function generateTimestamp() {
  const now = new Date();
  return (
    now.getFullYear().toString() +
    String(now.getMonth() + 1).padStart(2, "0") +
    String(now.getDate()).padStart(2, "0") +
    String(now.getHours()).padStart(2, "0") +
    String(now.getMinutes()).padStart(2, "0") +
    String(now.getSeconds()).padStart(2, "0") +
    String(now.getMilliseconds()).padStart(3, "0") +
    Math.floor(Math.random() * 1000)
      .toString()
      .padStart(3, "0")
  );
}

function generateJobId(app_id: string, user_id: string, dataId: string) {
  // const timestamp = generateTimestamp();
  // const jobId = `${app_id}_${user_id}_${dataId}_${timestamp}`;
  
  const timestamp = Date.now().toString(36);
  const random = crypto.getRandomValues(new Uint32Array(1))[0].toString(36);
  
  const jobId = `${app_id}_${user_id}_${dataId}_${timestamp}_${random}`;

  return jobId;
}

export { generateJobId };