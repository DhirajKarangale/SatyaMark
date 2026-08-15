const EventEmitter = require('events');

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

    async ensureConnection(serviceName, triggerConnectFn = null) {
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

        // Wait until it becomes connected
        if (this.states.get(serviceName).status !== 'connected') {
            await new Promise(resolve => {
                const onConnect = () => {
                    this.removeListener(`${serviceName}:connected`, onConnect);
                    resolve();
                };
                this.on(`${serviceName}:connected`, onConnect);
            });
            console.log(`[ConnectionManager] Operation resumed for ${serviceName}.`);
        }
    }
}

module.exports = new ConnectionManager();
