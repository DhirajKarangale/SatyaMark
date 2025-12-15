export const MARK_META: Record<
  string,
  { label: string; icon: string; color: string }
> = {
  Correct: {
    label: "Correct",
    icon: "/correct.png",
    color: "text-green-400",
  },
  Incorrect: {
    label: "Incorrect",
    icon: "/incorrect.png",
    color: "text-red-400",
  },
  "AI-Generated": {
    label: "AI-Generated",
    icon: "/ai.png",
    color: "text-purple-400",
  },
  Real: {
    label: "Real",
    icon: "/real.png",
    color: "text-cyan-400",
  },
  Pending: {
    label: "Pending",
    icon: "/pending.png",
    color: "text-yellow-400",
  },
  subjective: {
    label: "Subjective",
    icon: "/subjective.png",
    color: "text-blue-400",
  },
  Insufficient: {
    label: "Insufficient",
    icon: "/insufficient.png",
    color: "text-zinc-400",
  },
};