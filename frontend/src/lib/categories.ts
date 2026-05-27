export const CATEGORY_NAMES = [
  "Plumbing",
  "Electrical",
  "Carpentry",
  "Cleaning",
  "Painting",
  "AC & Appliance",
  "Pest Control",
  "Gardening",
] as const;

export type CategoryName = (typeof CATEGORY_NAMES)[number];
