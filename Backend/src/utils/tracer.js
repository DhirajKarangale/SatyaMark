const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const isTraceEnabled = process.env.ENABLE_TRACE === 'true';

// We store pending traces in memory, indexed by jobId
const activeTraces = new Map();

// Traces directory at the root level of the project
const TRACES_DIR = path.resolve(__dirname, '../../../traces');

// Utility to ensure directory exists
function ensureTraceDir() {
    if (!fs.existsSync(TRACES_DIR)) {
        fs.mkdirSync(TRACES_DIR, { recursive: true });
    }
}

// Utility to find the next available trace file number
function getNextTraceId() {
    ensureTraceDir();
    
    let counter = 1;
    let traceId;
    let filePath;
    
    do {
        traceId = `trace_satyamark_${counter}`;
        filePath = path.join(TRACES_DIR, `${traceId}.json`);
        counter++;
    } while (fs.existsSync(filePath));
    
    return traceId;
}

/**
 * Initializes a new trace session
 */
function createTrace(jobId, sessionId) {
    if (!isTraceEnabled) return null;
    if (activeTraces.has(jobId)) return activeTraces.get(jobId).traceId;

    const traceId = getNextTraceId();
    
    const traceSession = {
        trace_id: traceId,
        session_id: sessionId,
        job_id: jobId,
        started_at: new Date().toISOString(),
        completed_at: null,
        status: "in_progress",
        events: [],
        final_result: null,
        total_duration_ms: 0,
        startTime: Date.now(),
        fallbackTimer: null
    };

    activeTraces.set(jobId, traceSession);
    return traceId;
}

/**
 * Records a new event in the trace
 */
function traceEvent({ jobId, sessionId, component, service = 'verification', stage, event, status = 'success', duration_ms = null, details = {} }) {
    if (!isTraceEnabled) return;

    let traceSession = activeTraces.get(jobId);
    
    // If trace wasn't explicitly created (e.g., frontend sent an event early), create it
    if (!traceSession) {
        if (jobId) {
            createTrace(jobId, sessionId);
            traceSession = activeTraces.get(jobId);
        } else {
            console.warn("[Tracer] Cannot record event without jobId:", event);
            return;
        }
    }
    
    // Safety check - never log secrets
    const sanitizedDetails = { ...details };
    delete sanitizedDetails.password;
    delete sanitizedDetails.secret;
    delete sanitizedDetails.token;
    delete sanitizedDetails.api_key;
    delete sanitizedDetails.hmac;

    const eventRecord = {
        timestamp: details.timestamp || new Date().toISOString(), // Use client timestamp if provided
        trace_id: traceSession.trace_id,
        session_id: sessionId || traceSession.session_id,
        job_id: jobId,
        component,
        service,
        stage,
        event,
        status,
        duration_ms: duration_ms !== undefined ? duration_ms : null,
        details: sanitizedDetails
    };

    traceSession.events.push(eventRecord);

    // If this is the final AI callback event, start a fallback timer to flush
    if (event === "backend_callback_received" || event === "final_result_generated") {
        if (traceSession.fallbackTimer) clearTimeout(traceSession.fallbackTimer);
        traceSession.fallbackTimer = setTimeout(() => {
            console.log(`[Tracer] Fallback timer triggered for job ${jobId}`);
            flushTrace(jobId, "fallback_timeout");
        }, 5000);
    }
}

/**
 * Finalizes and writes the trace file
 */
function flushTrace(jobId, reason = "frontend_flush") {
    if (!isTraceEnabled) return;

    const traceSession = activeTraces.get(jobId);
    if (!traceSession) return;

    if (traceSession.fallbackTimer) {
        clearTimeout(traceSession.fallbackTimer);
        traceSession.fallbackTimer = null;
    }

    traceSession.completed_at = new Date().toISOString();
    traceSession.total_duration_ms = Date.now() - traceSession.startTime;
    traceSession.status = "completed";
    
    // Extract final result if available
    const callbackEvent = traceSession.events.find(e => e.event === "backend_callback_received" || e.event === "final_result_generated");
    if (callbackEvent && callbackEvent.details) {
        traceSession.final_result = callbackEvent.details;
    }

    // Add finalizing event
    traceSession.events.push({
        timestamp: new Date().toISOString(),
        trace_id: traceSession.trace_id,
        session_id: traceSession.session_id,
        job_id: jobId,
        component: "tracer",
        service: "tracing",
        stage: "finalization",
        event: "trace_finalized",
        status: "success",
        duration_ms: 0,
        details: { reason }
    });

    // Sort all events chronologically by timestamp
    traceSession.events.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

    // Assign sequential numbers
    traceSession.events.forEach((evt, idx) => {
        evt.sequence_number = idx + 1;
    });

    ensureTraceDir();
    // Delete internal tracking props before serializing
    const output = { ...traceSession };
    delete output.startTime;
    delete output.fallbackTimer;

    // Write file safely
    let counter = parseInt(traceSession.trace_id.split('_').pop()) || 1;
    let filePath;
    let finalTraceId;

    while (true) {
        finalTraceId = `trace_satyamark_${counter}`;
        filePath = path.join(TRACES_DIR, `${finalTraceId}.json`);
        try {
            output.trace_id = finalTraceId;
            output.events.forEach(e => e.trace_id = finalTraceId);
            
            fs.writeFileSync(filePath, JSON.stringify(output, null, 2), { flag: 'wx' });
            console.log(`[Tracer] Successfully wrote trace file: ${finalTraceId}.json`);
            break;
        } catch (err) {
            if (err.code === 'EEXIST') {
                counter++;
            } else {
                console.error(`[Tracer] Failed to write trace file ${filePath}:`, err);
                break;
            }
        }
    }

    // Remove from memory
    activeTraces.delete(jobId);
}

module.exports = {
    isTraceEnabled,
    createTrace,
    traceEvent,
    flushTrace
};
