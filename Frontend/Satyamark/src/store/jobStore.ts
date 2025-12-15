type Listener = () => void;

const pendingJobs = new Set<string>();
const listeners = new Set<Listener>();

function notify() {
    listeners.forEach(l => l());
}

export const jobStore = {
    add(jobId: string) {
        pendingJobs.add(jobId);
        notify();
    },

    remove(jobId: string) {
        pendingJobs.delete(jobId);
        notify();
    },

    list() {
        return Array.from(pendingJobs);
    },

    hasJobs() {
        return pendingJobs.size > 0;
    },

    subscribe(listener: Listener) {
        listeners.add(listener);
        return () => {
            listeners.delete(listener);
        };
    }
};