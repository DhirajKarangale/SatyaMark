import { sendTraceMessage } from "../core/connectionManager";

export type TraceEventDetails = {
    jobId?: string;
    sessionId?: string;
    component: string;
    stage: string;
    event: string;
    status?: "success" | "failed" | "in_progress";
    duration_ms?: number;
    details?: Record<string, any>;
};

export function sendTraceEvent(traceEvent: TraceEventDetails): void {
    sendTraceMessage({
        type: "trace_event",
        payload: {
            ...traceEvent,
            service: "verification"
        }
    });
}

export function flushTrace(jobId: string, sessionId?: string): void {
    sendTraceMessage({
        type: "flush_trace",
        jobId,
        sessionId
    });
}
