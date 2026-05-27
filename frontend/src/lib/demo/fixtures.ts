/**
 * Static demo fixtures for the VITE_DEMO=1 build.
 * Generated once via deterministic loops; no Math.random at module load,
 * so the same seed reloads to the same state.
 */

import { type CategoryName as Category } from "@/lib/categories";

export interface DemoService {
  id: number;
  name: string;
  category: Category;
  description: string;
  base_price: number;
  time_required: number;
  is_active: boolean;
  image_url: string;
  rating: number;
  review_count: number;
}

export interface DemoUser {
  id: number;
  email: string;
  role: "admin" | "professional" | "user";
  full_name: string;
  address: string | null;
  pincode: string | null;
  is_blocked: boolean;
  active: boolean;
  service_id?: number | null;
  service_name?: string | null;
  approval_status?: string | null;
  experience?: number | null;
  description?: string | null;
  avatar_url: string;
  rating?: number;
  review_count?: number;
}

export interface DemoRequest {
  id: number;
  service_id: number;
  service_name: string;
  customer_id: number;
  customer_name: string;
  professional_id: number | null;
  professional_name?: string | null;
  date_of_request: string; // YYYY-MM-DD
  date_of_completion: string | null;
  service_status: "requested" | "accepted" | "in_progress" | "completed" | "cancelled";
  scheduled_time: string | null; // ISO
  address: string;
  pincode: string;
  remarks: string | null;
}

export interface DemoReview {
  id: number;
  request_id: number;
  author_id: number;
  author_name: string;
  professional_id: number;
  service_id: number;
  rating: number;
  comment: string;
  date: string; // YYYY-MM-DD
}

export interface DemoState {
  version: string;
  users: DemoUser[];
  services: DemoService[];
  requests: DemoRequest[];
  reviews: DemoReview[];
  currentUserId: number | null;
  nextRequestId: number;
  nextUserId: number;
  exports: Record<string, { startedAt: number; filename: string }>;
}

// Tied to the git SHA injected via vite.config.ts so every deploy invalidates
// cached fixtures in localStorage. Falls back to "dev" in
// repos without git history.
// Bump the suffix (e.g. "dev.3") whenever fixtures change so dev sessions
// reseed automatically. Production uses VITE_BUILD_ID (the git SHA) which
// invalidates on every deploy.
export const DEMO_STATE_VERSION = import.meta.env.VITE_BUILD_ID ?? "dev.2";

// Base width sized for the smallest realistic card slot (~390 px mobile);
// ServiceCard derives a srcset from this URL for retina + larger viewports.
const photo = (id: string) =>
  `https://images.unsplash.com/photo-${id}?w=480&q=75&auto=format&fit=crop`;
const avatar = (seed: string) =>
  `https://api.dicebear.com/9.x/notionists/svg?seed=${encodeURIComponent(seed)}`;

const IMAGES: Record<Category, string[]> = {
  Plumbing: [photo("1585704032915-c3400ca199e7"), photo("1607472586893-edb57bdc0e39")],
  Electrical: [photo("1565608087341-404b25492fee"), photo("1558002038-1055907df827")],
  Carpentry: [photo("1504148455328-c376907d081c"), photo("1567538096630-e0c55bd6374c")],
  Cleaning: [photo("1581578731548-c64695cc6952"), photo("1527515637462-cff94eecc1ac")],
  Painting: [photo("1562259949-e8e7689d7828"), photo("1589939705384-5185137a7f0f")],
  "AC & Appliance": [photo("1505691938895-1758d7feb511"), photo("1599619351208-3e6c839d6828")],
  "Pest Control": [photo("1593696140826-c58b021acf8b"), photo("1583947215259-38e31be8751f")],
  Gardening: [photo("1416879595882-3373a0480b5b"), photo("1523348837708-15d4a09cfac2")],
};

const SERVICE_DEFS: Array<Omit<DemoService, "id" | "image_url" | "rating" | "review_count">> = [
  // Plumbing
  {
    name: "Tap & Pipe Repair",
    category: "Plumbing",
    description: "Fix leaks, replace faucets, and resolve pressure issues. Same-day service.",
    base_price: 199,
    time_required: 60,
    is_active: true,
  },
  {
    name: "Bathroom Fitting",
    category: "Plumbing",
    description: "Toilet, basin, shower installation and replacement by certified plumbers.",
    base_price: 549,
    time_required: 120,
    is_active: true,
  },
  {
    name: "Water Tank Cleaning",
    category: "Plumbing",
    description: "Mechanical scrubbing and chlorine treatment for overhead and underground tanks.",
    base_price: 799,
    time_required: 180,
    is_active: true,
  },
  // Electrical
  {
    name: "Wiring & Switches",
    category: "Electrical",
    description: "Switchboard repair, new wiring runs, and earthing checks. Licensed work.",
    base_price: 249,
    time_required: 75,
    is_active: true,
  },
  {
    name: "Fan & Light Installation",
    category: "Electrical",
    description: "Ceiling fans, chandeliers, and LED panel installation with cleanup.",
    base_price: 299,
    time_required: 60,
    is_active: true,
  },
  {
    name: "Inverter & UPS Service",
    category: "Electrical",
    description: "Battery health check, inverter installation, and load balancing.",
    base_price: 449,
    time_required: 90,
    is_active: true,
  },
  // Carpentry
  {
    name: "Furniture Assembly",
    category: "Carpentry",
    description: "Flat-pack assembly, modular kitchen fittings, and on-site adjustments.",
    base_price: 349,
    time_required: 90,
    is_active: true,
  },
  {
    name: "Door & Window Repair",
    category: "Carpentry",
    description: "Hinge replacement, alignment fixes, locks and handle replacement.",
    base_price: 249,
    time_required: 60,
    is_active: true,
  },
  {
    name: "Custom Shelving",
    category: "Carpentry",
    description: "Made-to-measure shelves, wall units, and storage solutions in wood or MDF.",
    base_price: 1499,
    time_required: 240,
    is_active: true,
  },
  // Cleaning
  {
    name: "Deep Home Cleaning",
    category: "Cleaning",
    description: "Full-home deep clean: dusting, mopping, kitchen and bathroom sanitization.",
    base_price: 1899,
    time_required: 300,
    is_active: true,
  },
  {
    name: "Bathroom Cleaning",
    category: "Cleaning",
    description: "Tile descaling, fixture polishing, and grout treatment for sparkling results.",
    base_price: 499,
    time_required: 90,
    is_active: true,
  },
  {
    name: "Sofa & Carpet Cleaning",
    category: "Cleaning",
    description: "Shampoo extraction and steam cleaning for upholstery, sofas, and rugs.",
    base_price: 899,
    time_required: 120,
    is_active: true,
  },
  // Painting
  {
    name: "Interior Painting",
    category: "Painting",
    description: "Per-room interior painting with premium emulsion. Includes prep and cleanup.",
    base_price: 2499,
    time_required: 480,
    is_active: true,
  },
  {
    name: "Exterior & Texture Painting",
    category: "Painting",
    description: "Weatherproof exterior coats and decorative textures by experienced painters.",
    base_price: 4999,
    time_required: 720,
    is_active: true,
  },
  // AC & Appliance
  {
    name: "AC Service & Repair",
    category: "AC & Appliance",
    description: "Filter clean, gas top-up, leak fix. Split and window AC supported.",
    base_price: 549,
    time_required: 90,
    is_active: true,
  },
  {
    name: "Refrigerator & Washing Machine Repair",
    category: "AC & Appliance",
    description: "On-site diagnosis and repair for major appliance brands.",
    base_price: 449,
    time_required: 60,
    is_active: true,
  },
  // Pest Control
  {
    name: "Cockroach & Ant Treatment",
    category: "Pest Control",
    description: "Odourless gel-based treatment safe for kids and pets. 3-month warranty.",
    base_price: 899,
    time_required: 90,
    is_active: true,
  },
  // Gardening
  {
    name: "Lawn & Garden Care",
    category: "Gardening",
    description: "Mowing, hedge trimming, weeding, and seasonal planting recommendations.",
    base_price: 699,
    time_required: 120,
    is_active: true,
  },
];

const PRO_NAMES = [
  "Ravi Kumar", "Priya Sharma", "Arjun Reddy", "Sunita Iyer",
  "Vikram Singh", "Kavya Menon", "Rohan Desai", "Lakshmi Nair",
  "Aditya Rao", "Meena Pillai", "Karthik Patel", "Anjali Krishnan",
  "Suresh Mehta", "Divya Bhat", "Nitin Joshi", "Sneha Kulkarni",
  "Rajesh Pillai", "Pooja Hegde", "Manoj Verma", "Shreya Murthy",
  "Ashok Naidu", "Geeta Rao", "Yogesh Kapoor", "Rekha Shenoy",
  "Devendra Achar", "Latha Rao", "Hemant Bhatt", "Madhuri Pai",
  "Surya Prasad", "Anita Kamath",
];

const CUSTOMER_NAMES = [
  "Aakash Gupta", "Nisha Banerjee", "Tarun Saxena", "Ishita Roy",
  "Varun Kashyap", "Tanvi Malhotra", "Sanjay Bose", "Pranita Joshi",
  "Aravind Krishnamurthy",
];

const BIOS = [
  "Certified specialist with a focus on residential work and clean finishes.",
  "Started as an apprentice at 18, now leads small teams across Bangalore.",
  "Known for tidy workspaces and clear before-after explanations to customers.",
  "Trained at NSDC; carries own equipment and follows safety protocols strictly.",
  "Friendly, on-time, and patient. Speaks Kannada, English, and Hindi.",
  "Worked with a major service brand for 4+ years before going independent.",
  "Specializes in quick turnaround jobs without compromising on quality.",
  "Background in commercial maintenance; brings industrial-grade precision to homes.",
  "Honest pricing, no upselling. Prefers to fix rather than replace when possible.",
  "Repeat customers across HSR Layout and Indiranagar; rated highly for follow-ups.",
];

const AREAS = [
  { area: "Indiranagar", pin: "560038" },
  { area: "Koramangala", pin: "560034" },
  { area: "HSR Layout", pin: "560102" },
  { area: "Whitefield", pin: "560066" },
  { area: "Jayanagar", pin: "560011" },
  { area: "Marathahalli", pin: "560037" },
  { area: "BTM Layout", pin: "560029" },
  { area: "Electronic City", pin: "560100" },
];

const REVIEW_TEXTS = [
  "On time and very polite. Job done right the first time.",
  "Quick fix, fair price. Will book again.",
  "Did a thorough job. Cleaned up after himself.",
  "Genuinely knowledgeable. Explained the issue clearly.",
  "Took a bit longer than expected but the result is great.",
  "Brought the right tools and parts. No drama.",
  "Booking to job done in under 4 hours. Impressive.",
  "Friendly, careful with our furniture. Recommended.",
  "Honest about what needed replacing vs. what could be repaired.",
  "Punctual and professional. Worth the price.",
];

function buildServices(): DemoService[] {
  return SERVICE_DEFS.map((def, i) => {
    const id = i + 1;
    const images = IMAGES[def.category];
    const image_url = images[i % images.length];
    const rating = Number((3.9 + ((id * 7) % 11) * 0.1).toFixed(1));
    const review_count = 24 + ((id * 37) % 360);
    return { id, ...def, image_url, rating, review_count };
  });
}

function buildUsers(services: DemoService[]): DemoUser[] {
  const users: DemoUser[] = [];

  // Admin (id 1) — primary demo admin
  users.push({
    id: 1,
    email: "admin@demo.local",
    role: "admin",
    full_name: "Riya Goel",
    address: null,
    pincode: null,
    is_blocked: false,
    active: true,
    avatar_url: avatar("Riya Goel"),
  });

  // Demo customer (id 2)
  users.push({
    id: 2,
    email: "customer@demo.local",
    role: "user",
    full_name: "Aakash Gupta",
    address: "12, 4th Cross, Indiranagar",
    pincode: "560038",
    is_blocked: false,
    active: true,
    avatar_url: avatar("Aakash Gupta"),
  });

  // Other customers (id 3..10) — used as authors of historical requests
  for (let i = 1; i < CUSTOMER_NAMES.length; i++) {
    const name = CUSTOMER_NAMES[i];
    const area = AREAS[i % AREAS.length];
    users.push({
      id: i + 2,
      email: `${name.toLowerCase().replace(/\s+/g, ".")}@demo.local`,
      role: "user",
      full_name: name,
      address: `${10 + i * 3}, ${area.area}`,
      pincode: area.pin,
      is_blocked: false,
      active: true,
      avatar_url: avatar(name),
    });
  }

  // Demo professional (id 100) — first plumber, used by "Login as Professional"
  const firstPlumbing = services.find((s) => s.category === "Plumbing")!;
  users.push({
    id: 100,
    email: "pro@demo.local",
    role: "professional",
    full_name: "Ravi Kumar",
    address: "B-204, 4th Block, Koramangala",
    pincode: "560034",
    is_blocked: false,
    active: true,
    service_id: firstPlumbing.id,
    service_name: firstPlumbing.name,
    approval_status: "approved",
    experience: 8,
    description: BIOS[0],
    avatar_url: avatar("Ravi Kumar"),
    rating: 4.8,
    review_count: 142,
  });

  // Other professionals (id 101..129)
  let proId = 101;
  for (let i = 1; i < PRO_NAMES.length; i++) {
    const name = PRO_NAMES[i];
    // Distribute across services roughly evenly
    const service = services[(i + 2) % services.length];
    const area = AREAS[i % AREAS.length];
    let approval: string;
    if (i >= PRO_NAMES.length - 4) approval = "pending";
    else if (i >= PRO_NAMES.length - 6) approval = "rejected";
    else approval = "approved";
    users.push({
      id: proId,
      email: `${name.toLowerCase().replace(/\s+/g, ".")}@demo.local`,
      role: "professional",
      full_name: name,
      address: `${20 + i * 5}, ${area.area}`,
      pincode: area.pin,
      is_blocked: false,
      active: true,
      service_id: service.id,
      service_name: service.name,
      approval_status: approval,
      experience: 1 + ((i * 7) % 12),
      description: BIOS[i % BIOS.length],
      avatar_url: avatar(name),
      rating: Number((3.8 + ((i * 11) % 12) * 0.1).toFixed(1)),
      review_count: 8 + ((i * 17) % 332),
    });
    proId++;
  }

  return users;
}

function isoDateNDaysAgo(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10);
}

function isoDateTimeNDaysFromNow(n: number, hour = 10): string {
  const d = new Date();
  d.setDate(d.getDate() + n);
  d.setHours(hour, 0, 0, 0);
  return d.toISOString();
}

const REMARK_POOL: (string | null)[] = [
  "Please call before arriving.",
  "Apartment is on the 3rd floor — lift available.",
  "Building gate code: 4521. Park in B2 visitor spot.",
  "Pet-friendly please — we have a small dog.",
  "Issue started yesterday, gets worse in the evening.",
  "Bring your own safety gear, balcony work involved.",
  "Materials are already on-site, just need labor.",
  "Need it sorted before family visit on the weekend.",
  null,
  null,
  null,
  "Quote me before starting any extra work.",
  "Previous attempt didn't fix it — needs proper diagnosis.",
];

function buildRequests(users: DemoUser[], services: DemoService[]): DemoRequest[] {
  const customers = users.filter((u) => u.role === "user");
  const pros = users.filter((u) => u.role === "professional" && u.approval_status === "approved");
  const requests: DemoRequest[] = [];
  const statusPlan: DemoRequest["service_status"][] = [
    ...Array(50).fill("completed") as DemoRequest["service_status"][],
    ...Array(4).fill("in_progress") as DemoRequest["service_status"][],
    ...Array(12).fill("accepted") as DemoRequest["service_status"][],
    ...Array(11).fill("requested") as DemoRequest["service_status"][],
    ...Array(8).fill("cancelled") as DemoRequest["service_status"][],
  ];

  for (let i = 0; i < statusPlan.length; i++) {
    const status = statusPlan[i];
    const skew = (i * 7) % services.length;
    const service = services[skew];
    const customer = customers[i % customers.length];
    const matchingPros = pros.filter((p) => p.service_id === service.id);
    const pro =
      status === "requested" || status === "cancelled"
        ? null
        : (matchingPros[i % Math.max(1, matchingPros.length)] ?? pros[i % pros.length]);
    const daysAgo =
      status === "completed"
        ? 2 + ((i * 5) % 150) // spread across ~5 months for trend lines
        : status === "cancelled"
          ? 4 + ((i * 7) % 90)
          : status === "in_progress"
            ? (i % 3) + 1
            : status === "accepted"
              ? (i % 5) + 1
              : (i % 4) + 1;
    const date_of_request = isoDateNDaysAgo(daysAgo);
    const date_of_completion =
      status === "completed" ? isoDateNDaysAgo(Math.max(0, daysAgo - 1)) : null;
    const scheduled_time =
      status === "requested"
        ? isoDateTimeNDaysFromNow((i % 5) + 1, 10 + (i % 8))
        : isoDateTimeNDaysFromNow(-daysAgo + (status === "completed" ? -1 : 0), 10 + (i % 8));
    const area = AREAS[i % AREAS.length];
    requests.push({
      id: i + 1,
      service_id: service.id,
      service_name: service.name,
      customer_id: customer.id,
      customer_name: customer.full_name,
      professional_id: pro?.id ?? null,
      professional_name: pro?.full_name ?? null,
      date_of_request,
      date_of_completion,
      service_status: status,
      scheduled_time,
      address: customer.address ?? `${10 + i}, ${area.area}`,
      pincode: customer.pincode ?? area.pin,
      remarks: REMARK_POOL[i % REMARK_POOL.length],
    });
  }

  return requests;
}

function buildReviews(
  requests: DemoRequest[],
  users: DemoUser[],
): DemoReview[] {
  const completed = requests.filter((r) => r.service_status === "completed");
  const reviews: DemoReview[] = [];
  let id = 1;
  for (const req of completed) {
    if (!req.professional_id) continue;
    const customer = users.find((u) => u.id === req.customer_id);
    if (!customer) continue;
    const ratingPool = [5, 5, 5, 4, 4, 4, 3];
    const rating = ratingPool[(req.id * 3) % ratingPool.length];
    reviews.push({
      id: id++,
      request_id: req.id,
      author_id: customer.id,
      author_name: customer.full_name,
      professional_id: req.professional_id,
      service_id: req.service_id,
      rating,
      comment: REVIEW_TEXTS[(req.id * 7) % REVIEW_TEXTS.length],
      date: req.date_of_completion ?? req.date_of_request,
    });
  }

  // Add a second review for ~half of completed requests for richer counts
  for (const req of completed) {
    if (!req.professional_id) continue;
    if (req.id % 2 !== 0) continue;
    const customer = users.find((u) => u.id === req.customer_id);
    if (!customer) continue;
    reviews.push({
      id: id++,
      request_id: req.id,
      author_id: customer.id,
      author_name: customer.full_name,
      professional_id: req.professional_id,
      service_id: req.service_id,
      rating: 4,
      comment: REVIEW_TEXTS[(req.id * 13 + 4) % REVIEW_TEXTS.length],
      date: req.date_of_completion ?? req.date_of_request,
    });
  }

  return reviews;
}

export function buildSeedState(): DemoState {
  const services = buildServices();
  const users = buildUsers(services);
  const requests = buildRequests(users, services);
  const reviews = buildReviews(requests, users);
  return {
    version: DEMO_STATE_VERSION,
    users,
    services,
    requests,
    reviews,
    currentUserId: null,
    nextRequestId: requests.length + 1,
    nextUserId: 200,
    exports: {},
  };
}

export const DEMO_ACCOUNT_IDS = {
  admin: 1,
  customer: 2,
  professional: 100,
} as const;
