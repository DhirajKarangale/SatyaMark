function generateJobId(app_id: string, user_id: string, dataId: string) {
  const timestamp = Date.now().toString(36);
  const random = crypto.getRandomValues(new Uint32Array(1))[0].toString(36);
  
  const jobId = `${app_id}_${user_id}_${dataId}_${timestamp}_${random}`;

  return jobId;
}

export { generateJobId };