import { encrypt, decrypt } from "./encryption";
import { setCookie, getCookie } from "./storage";

type SessionData = {
  sessionId: string;
  hmacSecret: string;
};

async function getSessionData(): Promise<SessionData> {
  const raw = getCookie("satya_session");
  if (!raw) return { sessionId: "", hmacSecret: "" };

  try {
    const decrypted = await decrypt(raw);
    const data = JSON.parse(decrypted);
    return {
      sessionId: data.sessionId || "",
      hmacSecret: data.hmacSecret || "",
    };
  } catch {
    return { sessionId: "", hmacSecret: "" };
  }
}

async function setSessionData(sessionId: string, hmacSecret: string) {
  const data = JSON.stringify({ sessionId, hmacSecret });
  const encrypted = await encrypt(data);
  setCookie("satya_session", encrypted);
}

function clearSession() {
  setCookie("satya_session", "", -1);
}

export { getSessionData, setSessionData, clearSession }