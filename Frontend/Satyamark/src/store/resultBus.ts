type Listener<T> = (data: T) => void;

function createBus<T>() {
    const listeners = new Set<Listener<T>>();

    return {
        publish(data: T) {
            listeners.forEach(l => l(data));
        },
        subscribe(listener: Listener<T>) {
            listeners.add(listener);
            return () => {
                listeners.delete(listener); 
            };
        }
    };
}

export const resultBus = createBus<any>();