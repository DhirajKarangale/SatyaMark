export const ICON_URLS = {
  correct: "https://res.cloudinary.com/dfamljkyo/image/upload/v1768325442/correct_gjiadc.png",
  incorrect: "https://res.cloudinary.com/dfamljkyo/image/upload/v1768325442/incorrect_lb9yfb.png",
  insufficient: "https://res.cloudinary.com/dfamljkyo/image/upload/v1768325442/insufficient_lvtzjc.png",
  uncertain: "https://res.cloudinary.com/dfamljkyo/image/upload/v1768325441/uncertain_fq5d2c.png",
  ai: "https://res.cloudinary.com/dfamljkyo/image/upload/v1768325441/ai_dlykbo.png",
  nonai: "https://res.cloudinary.com/dfamljkyo/image/upload/v1768325441/nonai_coy4w5.png",
  verifyable: "https://res.cloudinary.com/dfamljkyo/image/upload/v1768325441/verifyable_jugvwe.png",
  unverifyable: "https://res.cloudinary.com/dfamljkyo/image/upload/v1768325441/unverifyable_yzm5se.png",
  pending: "https://res.cloudinary.com/dfamljkyo/image/upload/v1768325440/pending_gpqshq.png",
} as const;

export type IconKey = keyof typeof ICON_URLS;