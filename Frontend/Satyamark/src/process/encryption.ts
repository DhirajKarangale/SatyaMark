const SECRET = "your-strong-secret";

function strToBuf(str: string) {
  return new TextEncoder().encode(str);
}

function bufToStr(buf: ArrayBuffer) {
  return new TextDecoder().decode(buf);
}

function bufToBase64(buf: ArrayBuffer) {
  return btoa(String.fromCharCode(...new Uint8Array(buf)));
}

function base64ToBuf(base64: string) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
}

async function getKey() {
  const keyMaterial = await crypto.subtle.importKey(
      "raw",
      strToBuf(SECRET),
      { name: "PBKDF2" },
      false,
      ["deriveKey"]
  );

  return crypto.subtle.deriveKey(
      {
          name: "PBKDF2",
          salt: strToBuf("satya_salt"),
          iterations: 100000,
          hash: "SHA-256"
      },
      keyMaterial,
      { name: "AES-GCM", length: 256 },
      false,
      ["encrypt", "decrypt"]
  );
}

export async function encrypt(text: string) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const key = await getKey();

  const encrypted = await crypto.subtle.encrypt(
      { name: "AES-GCM", iv },
      key,
      strToBuf(text)
  );

  const combined = new Uint8Array(iv.length + encrypted.byteLength);
  combined.set(iv);
  combined.set(new Uint8Array(encrypted), iv.length);

  return bufToBase64(combined.buffer);
}

export async function decrypt(cipherText: string) {
  const combined = new Uint8Array(base64ToBuf(cipherText));

  const iv = combined.slice(0, 12);
  const data = combined.slice(12);

  const key = await getKey();

  const decrypted = await crypto.subtle.decrypt(
      { name: "AES-GCM", iv },
      key,
      data
  );

  return bufToStr(decrypted);
}