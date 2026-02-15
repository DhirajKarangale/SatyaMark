import { encrypt, decrypt } from "../utils/satyamark_encryption";
import { setCookie, getCookie } from "../utils/satyamark_storage";

async function getSessionId(): Promise<string> {
  const raw = getCookie("satya_session");
  if (!raw) return "";

  try {
    return await decrypt(raw);
  } catch {
    return "";
  }
}

async function setSessionId(sessionId: string) {
  const encrypted = await encrypt(sessionId);
  setCookie("satya_session", encrypted);
}

function clearSession() {
  setCookie("satya_session", "", -1);
}

export { getSessionId, setSessionId, clearSession }