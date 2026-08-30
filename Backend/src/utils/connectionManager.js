const EventEmitter = require('events');

const DEFAULT_TIMEOUT_MS = 60000;

class ConnectionManager extends EventEmitter {
    constructor() {
        super();
        this.states = new Map();
    }

    _initState(serviceName) {
        if (!this.states.has(serviceName)) {
            this.states.set(serviceName, { status: 'disconnected' });
        }
    }

    setStatus(serviceName, status) {
        this._initState(serviceName);
        const state = this.states.get(serviceName);
        
        if (state.status !== status) {
            state.status = status;
            console.log(`[ConnectionManager] ${serviceName} is now ${status}`);
            if (status === 'connected') {
                this.emit(`${serviceName}:connected`);
            }
        }
    }

    getStatus(serviceName) {
        this._initState(serviceName);
        return this.states.get(serviceName).status;
    }

    isConnected(serviceName) {
        return this.getStatus(serviceName) === 'connected';
    }

    async ensureConnection(serviceName, triggerConnectFn = null, timeoutMs = DEFAULT_TIMEOUT_MS) {
        this._initState(serviceName);
        const state = this.states.get(serviceName);

        if (state.status === 'connected') {
            return; // Fast path
        }

        console.log(`[ConnectionManager] Operation paused for ${serviceName}. Current status: ${state.status}`);

        if (state.status === 'disconnected') {
            this.setStatus(serviceName, 'connecting');
            if (triggerConnectFn) {
                try {
                    await triggerConnectFn();
                } catch (error) {
                    console.log(`[ConnectionManager] Connection trigger failed for ${serviceName}:`, error.message);
                }
            }
        }

        // Wait until it becomes connected, with timeout to prevent infinite blocking
        if (this.states.get(serviceName).status !== 'connected') {
            await new Promise((resolve, reject) => {
                const onConnect = () => {
                    clearTimeout(timer);
                    this.removeListener(`${serviceName}:connected`, onConnect);
                    resolve();
                };

                const timer = setTimeout(() => {
                    this.removeListener(`${serviceName}:connected`, onConnect);
                    reject(new Error(`[ConnectionManager] Timeout: ${serviceName} did not reconnect within ${timeoutMs}ms`));
                }, timeoutMs);

                this.on(`${serviceName}:connected`, onConnect);
            });
            console.log(`[ConnectionManager] Operation resumed for ${serviceName}.`);
        }
    }
}

module.exports = new ConnectionManager();
