type Listener = () => void;

const STORAGE_KEY = "satyamark_pending_jobs";
const TTL = 1 * 60 * 1000; // 1 minutes

type StoredJob = {
    id: string;
    ts: number;
};

function loadJobs(): Map<string, StoredJob> {
    try {
        const raw = sessionStorage.getItem(STORAGE_KEY);
        if (!raw) return new Map();

        const arr: StoredJob[] = JSON.parse(raw);
        const now = Date.now();

        return new Map(
            arr
                .filter(j => now - j.ts < TTL) 
                .map(j => [j.id, j])
        );
    } catch {
        return new Map();
    }
}

const jobs = loadJobs();
const listeners = new Set<Listener>();

function persist() {
    sessionStorage.setItem(
        STORAGE_KEY,
        JSON.stringify([...jobs.values()])
    );
}

function cleanup() {
    const now = Date.now();
    let changed = false;

    for (const [id, job] of jobs) {
        if (now - job.ts >= TTL) {
            jobs.delete(id);
            changed = true;
        }
    }

    if (changed) persist();
}

function notify() {
    cleanup();
    persist();
    listeners.forEach(l => l());
}

export const jobStore = {
    add(jobId: string) {
        jobs.set(jobId, { id: jobId, ts: Date.now() });
        notify();
    },

    remove(jobId: string) {
        jobs.delete(jobId);
        notify();
    },

    has(jobId: string) {
        cleanup();
        return jobs.has(jobId);
    },

    list() {
        cleanup();
        return [...jobs.keys()];
    },

    hasJobs() {
        cleanup();
        return jobs.size > 0;
    },

    subscribe(listener: Listener) {
        listeners.add(listener);
        return () => {
            listeners.delete(listener);
        };
    }
};