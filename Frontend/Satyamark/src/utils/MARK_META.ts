export const MARK_META: Record<
  string,
  { label: string; icon: string; color: string }
> = {
  verifyable: {
    label: "Verifiable",
    icon: "/verifyable.png",
    color: "text-green-400",
  },
  unverifyable: {
    label: "Unverifiable",
    icon: "/unverifyable.png",
    color: "text-zinc-400",
  },
  insufficient: {
    label: "Insufficient",
    icon: "/insufficient.png",
    color: "text-yellow-400",
  },
  correct: {
    label: "Correct",
    icon: "/correct.png",
    color: "text-green-500",
  },
  incorrect: {
    label: "Incorrect",
    icon: "/incorrect.png",
    color: "text-red-400",
  },
  pending: {
    label: "Pending",
    icon: "/pending.png",
    color: "text-blue-400",
  },
  ai: {
    label: "AI-Generated",
    icon: "/ai.png",
    color: "text-purple-400",
  },
  nonai: {
    label: "Non AI / Human-Generated",
    icon: "/nonai.png",
    color: "text-cyan-400",
  },
};