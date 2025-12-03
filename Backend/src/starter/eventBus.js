const EventEmitter = require('events');
const bus = new EventEmitter();
bus.setMaxListeners(100);
module.exports = bus;