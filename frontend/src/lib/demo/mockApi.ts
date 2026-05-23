import { ApiError } from "../api-error";
import { getState, mutate, persist } from "./store";
import type { DemoRequest, DemoUser } from "./fixtures";
import { DEMO_ACCOUNT_IDS } from "./fixtures";

const LATENCY_MS = 120;

function delay<T>(value: T): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), LATENCY_MS));
}

function fail(status: number, detail: string): never {
  throw new ApiError(status, detail);
}

function toLoginResponse(u: DemoUser) {
  return {
    id: u.id,
    email: u.email,
    role: u.role,
    full_name: u.full_name,
    address: u.address,
    pincode: u.pincode,
    is_blocked: u.is_blocked,
    service_id: u.service_id ?? null,
    approval_status: u.approval_status ?? null,
  };
}

function toUserRead(u: DemoUser) {
  return {
    id: u.id,
    email: u.email,
    role: u.role,
    full_name: u.full_name,
    address: u.address,
    pincode: u.pincode,
    is_blocked: u.is_blocked,
    active: u.active,
    approval_status: u.approval_status ?? null,
    experience: u.experience ?? null,
    description: u.description ?? null,
    service_id: u.service_id ?? null,
    service_name: u.service_name ?? null,
    // demo-only extensions (consumers tolerate unknown fields)
    avatar_url: u.avatar_url,
    rating: u.rating ?? null,
    review_count: u.review_count ?? null,
  };
}

function currentUser(): DemoUser | null {
  const s = getState();
  if (s.currentUserId == null) return null;
  return s.users.find((u) => u.id === s.currentUserId) ?? null;
}

export async function demoFetch<T>(
  method: string,
  rawPath: string,
  body?: unknown,
): Promise<T> {
  const url = new URL(rawPath, "http://demo.local");
  const path = url.pathname;
  const params = url.searchParams;
  const result = handle(method, path, params, body);
  return delay(result) as Promise<T>;
}

function handle(
  method: string,
  path: string,
  params: URLSearchParams,
  body: unknown,
): unknown {
  // -------------------- Health --------------------
  if (method === "GET" && path === "/healthz") return { status: "ok" };
  if (method === "GET" && path === "/api/test-redis") {
    return { task_id: "demo-redis-test" };
  }

  // -------------------- Auth --------------------
  if (method === "POST" && path === "/api/auth/login") return login(body);
  if (method === "POST" && path === "/api/auth/logout") {
    mutate((s) => {
      s.currentUserId = null;
    });
    return undefined;
  }
  if (method === "GET" && path === "/api/auth/me") {
    const u = currentUser();
    if (!u) return fail(401, "Not authenticated");
    return toLoginResponse(u);
  }
  if (method === "POST" && path === "/api/auth/register") return register(body);

  // -------------------- Users --------------------
  if (method === "GET" && path === "/api/users") {
    const role = params.get("role");
    // Customers may list approved professionals (to power the booking picker).
    // Anything else (no filter, or listing customers) is admin-only.
    if (role !== "professional") requireAdmin();
    else requireAuth();
    const all = getState().users.filter((u) => (role ? u.role === role : true));
    const visible =
      role === "professional"
        ? all.filter((u) => u.approval_status === "approved" && !u.is_blocked)
        : all;
    return visible.map(toUserRead);
  }
  if (method === "GET" && path === "/api/users/me") {
    const u = requireAuth();
    return toUserRead(u);
  }
  if (method === "PUT" && path === "/api/users/me") {
    return updateMyProfile(body as Record<string, unknown>);
  }
  if (method === "DELETE" && path === "/api/users/me") {
    const u = requireAuth();
    mutate((s) => {
      s.users = s.users.filter((x) => x.id !== u.id);
      s.currentUserId = null;
    });
    return undefined;
  }

  const userIdMatch = path.match(/^\/api\/users\/(\d+)$/);
  if (userIdMatch) {
    const id = Number(userIdMatch[1]);
    if (method === "GET") {
      const u = getState().users.find((x) => x.id === id);
      if (!u) return fail(404, "User not found");
      return toUserRead(u);
    }
    if (method === "PUT") {
      requireAdmin();
      return adminUpdateUser(id, body as Record<string, unknown>);
    }
    if (method === "DELETE") {
      requireAdmin();
      mutate((s) => {
        s.users = s.users.filter((x) => x.id !== id);
      });
      return undefined;
    }
  }

  // -------------------- Services --------------------
  if (method === "GET" && path === "/api/services") {
    return getState().services.filter((s) => s.is_active);
  }
  if (method === "POST" && path === "/api/services") {
    requireAdmin();
    return createService(body as Record<string, unknown>);
  }
  const serviceIdMatch = path.match(/^\/api\/services\/(\d+)$/);
  if (serviceIdMatch) {
    const id = Number(serviceIdMatch[1]);
    if (method === "GET") {
      const svc = getState().services.find((s) => s.id === id);
      if (!svc) return fail(404, "Service not found");
      return svc;
    }
    if (method === "PUT") {
      requireAdmin();
      return updateService(id, body as Record<string, unknown>);
    }
    if (method === "DELETE") {
      requireAdmin();
      mutate((s) => {
        s.services = s.services.filter((x) => x.id !== id);
      });
      return undefined;
    }
  }

  // -------------------- Requests --------------------
  if (method === "GET" && path === "/api/requests") return listRequests();
  if (method === "POST" && path === "/api/requests") {
    return createRequest(body as Record<string, unknown>);
  }
  const requestIdMatch = path.match(/^\/api\/requests\/(\d+)$/);
  if (requestIdMatch) {
    const id = Number(requestIdMatch[1]);
    if (method === "GET") {
      const req = getState().requests.find((r) => r.id === id);
      if (!req) return fail(404, "Request not found");
      return req;
    }
    if (method === "PUT") return updateRequest(id, body as Record<string, unknown>);
    if (method === "DELETE") {
      const u = requireAuth();
      mutate((s) => {
        s.requests = s.requests.filter(
          (r) => !(r.id === id && (u.role === "admin" || r.customer_id === u.id)),
        );
      });
      return undefined;
    }
  }

  // -------------------- Export --------------------
  if (method === "POST" && path === "/api/export-service-requests") {
    const taskId = `demo-export-${Date.now()}`;
    mutate((s) => {
      s.exports[taskId] = {
        startedAt: Date.now(),
        filename: `service_requests_${new Date().toISOString().slice(0, 10)}.csv`,
      };
    });
    return { task_id: taskId };
  }
  const statusMatch = path.match(/^\/api\/export-status\/(.+)$/);
  if (method === "GET" && statusMatch) {
    const taskId = statusMatch[1];
    const exp = getState().exports[taskId];
    if (!exp) return fail(404, "Export not found");
    const elapsed = Date.now() - exp.startedAt;
    if (elapsed < 1500) return { status: "PENDING" };
    return { status: "SUCCESS", filename: exp.filename };
  }
  const downloadMatch = path.match(/^\/api\/download-export\/(.+)$/);
  if (method === "GET" && downloadMatch) {
    return buildExportCsv();
  }

  // -------------------- Triggers --------------------
  if (
    method === "POST" &&
    (path === "/api/trigger-daily-reminders" ||
      path === "/api/trigger-monthly-reports" ||
      path === "/api/trigger-activity-reports")
  ) {
    requireAdmin();
    return { status: "ok", sent: Math.floor(getState().users.length / 3) };
  }

  // -------------------- Analytics --------------------
  if (method === "GET" && path === "/api/analytics/admin") return adminAnalytics();
  if (method === "GET" && path === "/api/analytics/professional") {
    return professionalAnalytics();
  }

  return fail(404, `mock: no handler for ${method} ${path}`);
}

// ============================================================ Handlers

function login(body: unknown) {
  const { email } = (body ?? {}) as { email?: string; password?: string };
  if (!email) return fail(400, "Email required");
  const user = getState().users.find(
    (u) => u.email.toLowerCase() === email.toLowerCase(),
  );
  if (!user) return fail(401, "Invalid credentials");
  if (user.is_blocked) return fail(403, "Account is blocked");
  mutate((s) => {
    s.currentUserId = user.id;
  });
  return toLoginResponse(user);
}

function register(body: unknown) {
  const data = (body ?? {}) as Record<string, unknown>;
  const email = String(data.email ?? "");
  if (!email) return fail(400, "Email required");
  if (getState().users.some((u) => u.email.toLowerCase() === email.toLowerCase())) {
    return fail(400, "Email already registered");
  }
  const role = (data.role === "professional" ? "professional" : "user") as
    | "user"
    | "professional";
  const newUser: DemoUser = mutate((s) => {
    const id = s.nextUserId++;
    const full_name = String(data.full_name ?? email.split("@")[0]);
    const user: DemoUser = {
      id,
      email,
      role,
      full_name,
      address: (data.address as string) ?? null,
      pincode: (data.pincode as string) ?? null,
      is_blocked: false,
      active: true,
      avatar_url: `https://api.dicebear.com/9.x/notionists/svg?seed=${encodeURIComponent(full_name)}`,
    };
    if (role === "professional") {
      const sid = Number(data.service_id);
      const svc = s.services.find((x) => x.id === sid);
      user.service_id = svc?.id ?? null;
      user.service_name = svc?.name ?? null;
      user.experience = data.experience != null ? Number(data.experience) : 1;
      user.description = (data.description as string) ?? null;
      user.approval_status = "pending";
      user.rating = 0;
      user.review_count = 0;
    }
    s.users.push(user);
    s.currentUserId = id;
    return user;
  });
  return toLoginResponse(newUser);
}

function requireAuth(): DemoUser {
  const u = currentUser();
  if (!u) return fail(401, "Not authenticated");
  return u;
}

function requireAdmin(): DemoUser {
  const u = requireAuth();
  if (u.role !== "admin") return fail(403, "Admin only");
  return u;
}

function updateMyProfile(patch: Record<string, unknown>) {
  const u = requireAuth();
  mutate((s) => {
    const target = s.users.find((x) => x.id === u.id);
    if (!target) return;
    if (patch.full_name !== undefined) target.full_name = String(patch.full_name);
    if (patch.address !== undefined) target.address = patch.address as string | null;
    if (patch.pincode !== undefined) target.pincode = patch.pincode as string | null;
  });
  const fresh = getState().users.find((x) => x.id === u.id)!;
  return toUserRead(fresh);
}

function adminUpdateUser(id: number, patch: Record<string, unknown>) {
  mutate((s) => {
    const target = s.users.find((x) => x.id === id);
    if (!target) return;
    if (patch.is_blocked !== undefined) target.is_blocked = Boolean(patch.is_blocked);
    if (patch.approval_status !== undefined) {
      target.approval_status = String(patch.approval_status);
    }
  });
  const fresh = getState().users.find((x) => x.id === id);
  if (!fresh) return fail(404, "User not found");
  return toUserRead(fresh);
}

function createService(body: Record<string, unknown>) {
  const name = String(body.name ?? "");
  if (!name) return fail(400, "Service name required");
  return mutate((s) => {
    const id = (s.services.at(-1)?.id ?? 0) + 1;
    const newService = {
      id,
      name,
      category: (body.category as string) ?? "Plumbing",
      description: (body.description as string) ?? "",
      base_price: Number(body.base_price ?? 0),
      time_required: Number(body.time_required ?? 60),
      is_active: true,
      image_url: `https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=480&q=75&auto=format&fit=crop`,
      rating: 4.5,
      review_count: 0,
    };
    s.services.push(newService as (typeof s.services)[number]);
    return newService;
  });
}

function updateService(id: number, body: Record<string, unknown>) {
  mutate((s) => {
    const svc = s.services.find((x) => x.id === id);
    if (!svc) return;
    if (body.name !== undefined) svc.name = String(body.name);
    if (body.description !== undefined) svc.description = String(body.description);
    if (body.base_price !== undefined) svc.base_price = Number(body.base_price);
    if (body.time_required !== undefined) svc.time_required = Number(body.time_required);
    if (body.category !== undefined) svc.category = body.category as never;
    if (body.is_active !== undefined) svc.is_active = Boolean(body.is_active);
  });
  const fresh = getState().services.find((x) => x.id === id);
  if (!fresh) return fail(404, "Service not found");
  return fresh;
}

function listRequests(): DemoRequest[] {
  const u = requireAuth();
  const all = getState().requests;
  if (u.role === "admin") return [...all].sort((a, b) => b.id - a.id);
  if (u.role === "professional") {
    return all
      .filter(
        (r) =>
          r.professional_id === u.id ||
          (r.professional_id == null && r.service_id === u.service_id),
      )
      .sort((a, b) => b.id - a.id);
  }
  return all.filter((r) => r.customer_id === u.id).sort((a, b) => b.id - a.id);
}

function createRequest(body: Record<string, unknown>) {
  const u = requireAuth();
  if (u.role !== "user") return fail(403, "Customers only");
  const serviceId = Number(body.service_id);
  const service = getState().services.find((s) => s.id === serviceId);
  if (!service) return fail(404, "Service not found");
  const proIdRaw = body.professional_id;
  const proId =
    proIdRaw != null && proIdRaw !== "" && !Number.isNaN(Number(proIdRaw))
      ? Number(proIdRaw)
      : null;
  const pro = proId ? getState().users.find((x) => x.id === proId) : null;
  return mutate((s) => {
    const id = s.nextRequestId++;
    const req: DemoRequest = {
      id,
      service_id: service.id,
      service_name: service.name,
      customer_id: u.id,
      customer_name: u.full_name,
      professional_id: pro?.id ?? null,
      professional_name: pro?.full_name ?? null,
      date_of_request: new Date().toISOString().slice(0, 10),
      date_of_completion: null,
      service_status: "requested",
      scheduled_time: (body.scheduled_time as string) ?? null,
      address: String(body.address ?? u.address ?? ""),
      pincode: String(body.pincode ?? u.pincode ?? ""),
      remarks: (body.remarks as string) ?? null,
    };
    s.requests.push(req);
    return req;
  });
}

function updateRequest(id: number, body: Record<string, unknown>) {
  const u = requireAuth();
  mutate((s) => {
    const req = s.requests.find((r) => r.id === id);
    if (!req) return;
    if (body.service_status !== undefined) {
      const next = String(body.service_status) as DemoRequest["service_status"];
      req.service_status = next;
      if (next === "completed") {
        req.date_of_completion = new Date().toISOString().slice(0, 10);
      }
      if ((next === "accepted" || next === "in_progress") && u.role === "professional") {
        req.professional_id = u.id;
        req.professional_name = u.full_name;
      }
    }
    if (body.scheduled_time !== undefined) {
      req.scheduled_time = body.scheduled_time as string | null;
    }
    if (body.address !== undefined) req.address = String(body.address);
    if (body.pincode !== undefined) req.pincode = String(body.pincode);
    if (body.remarks !== undefined) req.remarks = body.remarks as string | null;
    if (body.professional_id !== undefined) {
      const pid = body.professional_id == null ? null : Number(body.professional_id);
      req.professional_id = pid;
      const pro = pid ? s.users.find((x) => x.id === pid) : null;
      req.professional_name = pro?.full_name ?? null;
    }
  });
  const fresh = getState().requests.find((r) => r.id === id);
  if (!fresh) return fail(404, "Request not found");
  return fresh;
}

function buildExportCsv(): string {
  const headers = [
    "id",
    "service_name",
    "customer_name",
    "professional_name",
    "date_of_request",
    "date_of_completion",
    "service_status",
    "address",
    "pincode",
  ];
  const rows = getState().requests.map((r) => [
    r.id,
    r.service_name,
    r.customer_name,
    r.professional_name ?? "",
    r.date_of_request,
    r.date_of_completion ?? "",
    r.service_status,
    r.address.replaceAll('"', '""'),
    r.pincode,
  ]);
  return [headers, ...rows]
    .map((row) => row.map((v) => `"${v}"`).join(","))
    .join("\n");
}

// ============================================================ Analytics

function groupByMonth<T>(items: T[], dateFn: (t: T) => string) {
  const map = new Map<string, number>();
  for (const it of items) {
    const d = new Date(dateFn(it));
    if (Number.isNaN(d.getTime())) continue;
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-01`;
    map.set(key, (map.get(key) ?? 0) + 1);
  }
  return [...map.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, count]) => ({ date, count }));
}

function adminAnalytics() {
  const s = getState();
  const completed = s.requests.filter((r) => r.service_status === "completed");

  const request_trends = groupByMonth(s.requests, (r) => r.date_of_request);

  const popularityMap = new Map<string, number>();
  for (const r of s.requests) {
    popularityMap.set(r.service_name, (popularityMap.get(r.service_name) ?? 0) + 1);
  }
  const service_popularity = [...popularityMap.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  // synthesize user registrations from user IDs (no created date in fixtures)
  const monthsBack = 6;
  const today = new Date();
  const user_registrations: { date: string; count: number }[] = [];
  for (let i = monthsBack; i >= 0; i--) {
    const d = new Date(today.getFullYear(), today.getMonth() - i, 1);
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-01`;
    user_registrations.push({
      date: key,
      count: 3 + ((i * 7) % 9),
    });
  }

  const professional_status = ["approved", "pending", "rejected"].map((status) => ({
    status,
    count: s.users.filter((u) => u.role === "professional" && u.approval_status === status)
      .length,
  }));

  const user_status = [
    { status: "active", count: s.users.filter((u) => u.role === "user" && !u.is_blocked).length },
    { status: "blocked", count: s.users.filter((u) => u.role === "user" && u.is_blocked).length },
  ];

  void completed; // eslint: silence unused

  return {
    request_trends,
    service_popularity,
    user_registrations,
    professional_status,
    user_status,
  };
}

function professionalAnalytics() {
  const u = requireAuth();
  if (u.role !== "professional") return fail(403, "Professional only");
  const s = getState();
  const myRequests = s.requests.filter((r) => r.professional_id === u.id);
  const completedCount = myRequests.filter((r) => r.service_status === "completed").length;
  const completion_rate =
    myRequests.length === 0 ? 0 : (completedCount / myRequests.length) * 100;

  const earningsByMonth = new Map<string, number>();
  for (const r of myRequests.filter((x) => x.service_status === "completed")) {
    const d = new Date(r.date_of_completion ?? r.date_of_request);
    if (Number.isNaN(d.getTime())) continue;
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-01`;
    const svc = s.services.find((x) => x.id === r.service_id);
    const earned = svc?.base_price ?? 0;
    earningsByMonth.set(key, (earningsByMonth.get(key) ?? 0) + earned);
  }
  const monthly_earnings = [...earningsByMonth.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, earnings]) => ({ date, earnings }));

  const statuses = ["requested", "accepted", "in_progress", "completed", "cancelled"];
  const status_distribution = statuses
    .map((status) => ({
      status,
      count: myRequests.filter((r) => r.service_status === status).length,
    }))
    .filter((s) => s.count > 0);

  return { completion_rate, monthly_earnings, status_distribution };
}

export function loginAsRole(role: "admin" | "professional" | "user") {
  const id =
    role === "admin"
      ? DEMO_ACCOUNT_IDS.admin
      : role === "professional"
      ? DEMO_ACCOUNT_IDS.professional
      : DEMO_ACCOUNT_IDS.customer;
  mutate((s) => {
    s.currentUserId = id;
  });
  persist();
}
