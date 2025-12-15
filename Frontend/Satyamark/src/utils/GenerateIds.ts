const KEY = "satyamark_user_id";

export function uniqueTimestamp() {
    const now = new Date();

    const yyyy = now.getFullYear();
    const MM = String(now.getMonth() + 1).padStart(2, "0");
    const dd = String(now.getDate()).padStart(2, "0");

    const hh = String(now.getHours()).padStart(2, "0");
    const mm = String(now.getMinutes()).padStart(2, "0");
    const ss = String(now.getSeconds()).padStart(2, "0");
    const ms = String(now.getMilliseconds()).padStart(3, "0");

    const micro = String(Math.floor(Math.random() * 1000)).padStart(3, "0");

    return `${yyyy}${MM}${dd}${hh}${mm}${ss}${ms}${micro}`;
}

export function getUserId() {
    let id = localStorage.getItem(KEY);

    if (!id) {
        const uuid = crypto.randomUUID();
        const time = uniqueTimestamp();
        id = `${uuid}_${time}`;
    }

    return id;
}

export function getDataId() {
    // const time = uniqueTimestamp();
    const rand = Math.floor(Math.random() * 9999999) + 1;
    const id = `${rand}`;

    return id;
}