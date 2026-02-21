const KEY = "satyamark_user_id";

export function getUserId() {
    let id = localStorage.getItem(KEY);

    if (!id) {
        const time = Date.now().toString(36);
        const random = crypto.getRandomValues(new Uint32Array(1))[0].toString(36);
        id = `${time}${random}`;
    }

    return id;
}

export function getDataId() {
    const rand = Math.floor(Math.random() * 9999999) + 1;
    const hash = rand.toString(36);
    const id = `${hash}`;

    return id;
}