/**
 * GenAI surface — event protocol, role-aware tool registry, agent loop, and
 * NL → request intent parser. Tools execute against the existing api.* client.
 */

import { api, API_BASE_URL } from "@/lib/api";
import { DEMO } from "@/lib/demo/flag";
import { CATEGORIES } from "@/lib/demo/fixtures";

// ──────────────────────────────────────────────── Event protocol

export type AgentEvent =
  | { type: "text"; delta: string }
  | { type: "tool_call"; id: string; name: string; args: Record<string, unknown> }
  | { type: "tool_result"; id: string; ok: boolean; data: unknown }
  | { type: "state"; status: string }
  | { type: "done" };

/** Maps a tool name to a single-word progress verb shown in the agent state. */
function stateForTool(name: string): string {
  if (name.startsWith("search_") || name.startsWith("list_")) return "Searching";
  if (
    name.startsWith("check_") ||
    name.startsWith("get_") ||
    name === "weekly_summary"
  ) {
    return "Analyzing";
  }
  if (
    name.startsWith("accept_") ||
    name.startsWith("approve_") ||
    name.startsWith("book_")
  ) {
    return "Updating";
  }
  return "Working";
}

// ──────────────────────────────────────────────── Stream helper

/**
 * Push a scripted sequence of events through a ReadableStream with random
 * inter-event jitter. Text deltas use shorter jitter (40–80ms) so streaming
 * reads like an LLM; tool events get a slightly longer "thinking" pause.
 */
export function streamScript(events: AgentEvent[]): ReadableStream<AgentEvent> {
  return new ReadableStream<AgentEvent>({
    async start(controller) {
      for (const ev of events) {
        const delay =
          ev.type === "text"
            ? 30 + Math.random() * 50
            : ev.type === "tool_call"
              ? 250 + Math.random() * 200
              : 150 + Math.random() * 150;
        await new Promise((r) => setTimeout(r, delay));
        controller.enqueue(ev);
      }
      controller.close();
    },
  });
}

/**
 * Turn a sentence into a sequence of `text` deltas, one word at a time.
 * The leading space stays attached to each word for natural rendering.
 */
export function tokenize(text: string): AgentEvent[] {
  return text
    .split(/(\s+)/)
    .filter((s) => s.length > 0)
    .map((w) => ({ type: "text" as const, delta: w }));
}

// ──────────────────────────────────────────────── Tools

export interface Tool {
  name: string;
  description: string;
  humanLabel: (args: Record<string, unknown>) => string;
  run: (args: Record<string, unknown>) => Promise<unknown>;
}

interface ServiceShape {
  id: number;
  name: string;
  category: string;
  description: string;
  base_price: number;
  time_required: number;
  is_active: boolean;
  rating?: number | null;
  review_count?: number | null;
}

interface RequestShape {
  id: number;
  service_id: number;
  service_name: string;
  customer_id: number;
  customer_name?: string | null;
  professional_id: number | null;
  professional_name?: string | null;
  service_status: string;
  scheduled_time: string | null;
  address: string;
  pincode: string;
  remarks: string | null;
  date_of_request: string;
  date_of_completion: string | null;
}

interface UserShape {
  id: number;
  email: string;
  full_name: string;
  role: string | null;
  approval_status?: string | null;
  experience?: number | null;
  service_name?: string | null;
  pincode?: string | null;
  description?: string | null;
}

interface AnalyticsShape {
  request_trends?: { date: string; count: number }[];
  service_popularity?: { name: string; count: number }[];
  user_registrations?: { date: string; count: number }[];
  professional_status?: { status: string; count: number }[];
  user_status?: { status: string; count: number }[];
}

const customerTools: Tool[] = [
  {
    name: "search_services",
    description: "Find services in the catalogue matching a free-text query.",
    humanLabel: ({ query }) =>
      query ? `Searching for "${String(query)}"` : "Browsing services",
    async run({ query }) {
      const q = String(query ?? "").toLowerCase();
      const all = await api.get<ServiceShape[]>("/api/services");
      if (!q) return all.slice(0, 6);
      return all
        .filter(
          (s) =>
            s.is_active &&
            (s.name.toLowerCase().includes(q) ||
              s.category.toLowerCase().includes(q) ||
              s.description.toLowerCase().includes(q)),
        )
        .slice(0, 6);
    },
  },
  {
    name: "list_my_requests",
    description: "List the current customer's recent service requests.",
    humanLabel: () => "Reading your booking history",
    async run() {
      const all = await api.get<RequestShape[]>("/api/requests");
      return all.slice(0, 8);
    },
  },
  {
    name: "check_request_status",
    description: "Check the status of one of the customer's requests by id.",
    humanLabel: ({ id }) => `Looking up request #${id}`,
    async run({ id }) {
      return api.get<RequestShape>(`/api/requests/${Number(id)}`);
    },
  },
  {
    name: "book_service",
    description:
      "Create a service request. Args: service_id, address, pincode, scheduled_time, remarks?",
    humanLabel: () => "Submitting your booking",
    async run(args) {
      return api.post<RequestShape>("/api/requests", args);
    },
  },
];

const professionalTools: Tool[] = [
  {
    name: "list_pending_requests",
    description: "List unassigned requests in the pro's service category.",
    humanLabel: () => "Checking your inbox",
    async run() {
      const all = await api.get<RequestShape[]>("/api/requests");
      return all.filter((r) => r.service_status === "requested");
    },
  },
  {
    name: "accept_request",
    description: "Accept a pending request by id.",
    humanLabel: ({ id }) => `Accepting request #${id}`,
    async run({ id }) {
      return api.put<RequestShape>(`/api/requests/${Number(id)}`, {
        service_status: "accepted",
      });
    },
  },
  {
    name: "weekly_summary",
    description: "Summarize the pro's recent activity.",
    humanLabel: () => "Crunching your weekly numbers",
    async run() {
      const all = await api.get<RequestShape[]>("/api/requests");
      const completed = all.filter((r) => r.service_status === "completed");
      const inFlight = all.filter((r) =>
        ["accepted", "in_progress"].includes(r.service_status),
      );
      return {
        completed_count: completed.length,
        in_flight_count: inFlight.length,
        pending_count: all.filter((r) => r.service_status === "requested").length,
      };
    },
  },
];

const adminTools: Tool[] = [
  {
    name: "get_metrics",
    description: "Fetch system-wide analytics for admin dashboards.",
    humanLabel: () => "Pulling system analytics",
    async run() {
      return api.get<AnalyticsShape>("/api/analytics/admin");
    },
  },
  {
    name: "list_pending_approvals",
    description: "List professional applicants awaiting review.",
    humanLabel: () => "Reviewing the approval queue",
    async run() {
      const all = await api.get<UserShape[]>("/api/users?role=professional");
      return all.filter((u) => (u.approval_status ?? "pending") === "pending");
    },
  },
  {
    name: "approve_professional",
    description: "Approve a pending professional by user id.",
    humanLabel: ({ id }) => `Approving professional #${id}`,
    async run({ id }) {
      return api.put<UserShape>(`/api/users/${Number(id)}/approval`, {
        approval_status: "approved",
      });
    },
  },
];

export function labelForTool(
  role: string | null | undefined,
  name: string,
  args: Record<string, unknown>,
): string {
  const tool = toolsForRole(role).find((t) => t.name === name);
  return tool ? tool.humanLabel(args) : name;
}

export function toolsForRole(role: string | null | undefined): Tool[] {
  switch (role) {
    case "admin":
      return adminTools;
    case "professional":
      return professionalTools;
    case "user":
      return customerTools;
    default:
      return [];
  }
}

function findTool(role: string | null | undefined, name: string): Tool | null {
  return toolsForRole(role).find((t) => t.name === name) ?? null;
}

let toolCallSeq = 0;
function nextToolId(): string {
  return `tc_${++toolCallSeq}_${Date.now().toString(36)}`;
}

// ──────────────────────────────────────────────── Agent loop

export interface ChatHistoryMessage {
  role: "user" | "assistant";
  text: string;
}

/**
 * Single entrypoint the chat store calls. Branches on whether the build is
 * the static demo (in-browser scripted agent) or the real app (server-side
 * Gemini via SSE). The chat UI never sees the difference — both paths emit
 * the same `AgentEvent` stream.
 */
export function runAgent(
  userMessage: string,
  role: string | null | undefined,
  history: ChatHistoryMessage[],
  modelId: string,
): ReadableStream<AgentEvent> {
  if (DEMO) return runAgentInBrowser(userMessage, role);
  return runAgentSSE(userMessage, history, modelId);
}

/**
 * POSTs to /api/agent/chat and decodes the server-sent-events response
 * into `AgentEvent`s. Uses fetch + a manual reader (not EventSource) so
 * we can send a JSON body and ride the existing cookie auth.
 *
 * The Gemini API key is read on the backend from the user's encrypted
 * record (or the server fallback); the browser never holds it.
 */
function runAgentSSE(
  userMessage: string,
  history: ChatHistoryMessage[],
  modelId: string,
): ReadableStream<AgentEvent> {
  return new ReadableStream<AgentEvent>({
    async start(controller) {
      let res: Response;
      try {
        res = await fetch(`${API_BASE_URL}/api/agent/chat`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            model_id: modelId,
            messages: history,
            message: userMessage,
          }),
        });
      } catch (err) {
        controller.enqueue({
          type: "text",
          delta: `\n\n_Network error: ${err instanceof Error ? err.message : String(err)}_`,
        });
        controller.enqueue({ type: "done" });
        controller.close();
        return;
      }

      if (!res.ok || !res.body) {
        // Surface the backend's `detail` verbatim — `agent.py` sets a
        // friendly message for the common cases (503 "AI is not configured",
        // 401 "not authenticated") so the chat can show them as-is.
        let detail = `Request failed (${res.status})`;
        try {
          const body = await res.json();
          if (typeof body?.detail === "string") detail = body.detail;
        } catch {
          // body wasn't JSON
        }
        controller.enqueue({ type: "text", delta: detail });
        controller.enqueue({ type: "done" });
        controller.close();
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      try {
        // eslint-disable-next-line no-constant-condition
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          // SSE frames are separated by a blank line. Split on \n\n, keep
          // any partial trailing frame in the buffer.
          let sep = buffer.indexOf("\n\n");
          while (sep !== -1) {
            const frame = buffer.slice(0, sep);
            buffer = buffer.slice(sep + 2);
            const event = parseSseFrame(frame);
            if (event) controller.enqueue(event);
            sep = buffer.indexOf("\n\n");
          }
        }
      } catch (err) {
        controller.enqueue({
          type: "text",
          delta: `\n\n_Stream error: ${err instanceof Error ? err.message : String(err)}_`,
        });
      } finally {
        controller.enqueue({ type: "done" });
        controller.close();
      }
    },
  });
}

function parseSseFrame(frame: string): AgentEvent | null {
  let eventType = "message";
  let data = "";
  for (const line of frame.split("\n")) {
    if (line.startsWith("event: ")) eventType = line.slice(7).trim();
    else if (line.startsWith("data: ")) data = line.slice(6);
  }
  if (!data) return null;
  try {
    const parsed = JSON.parse(data) as Record<string, unknown>;
    return { type: eventType, ...parsed } as AgentEvent;
  } catch {
    return null;
  }
}

/**
 * Demo-build agent — keyword-matches the user message, picks a script,
 * and dispatches in-browser tool calls. Used only when VITE_DEMO=1.
 */
function runAgentInBrowser(
  userMessage: string,
  role: string | null | undefined,
): ReadableStream<AgentEvent> {
  const msg = userMessage.toLowerCase();

  return new ReadableStream<AgentEvent>({
    async start(controller) {
      async function emit(ev: AgentEvent) {
        const delay =
          ev.type === "text"
            ? 25 + Math.random() * 45
            : ev.type === "tool_call"
              ? 280 + Math.random() * 220
              : ev.type === "state"
                ? 0 // state events are instant; the surrounding work is what takes time
                : 180 + Math.random() * 200;
        if (delay > 0) await new Promise((r) => setTimeout(r, delay));
        controller.enqueue(ev);
      }
      async function emitText(text: string) {
        await emit({ type: "state", status: "Writing" });
        for (const ev of tokenize(text)) await emit(ev);
      }
      async function callTool(name: string, args: Record<string, unknown>) {
        const id = nextToolId();
        await emit({ type: "state", status: stateForTool(name) });
        await emit({ type: "tool_call", id, name, args });
        const tool = findTool(role, name);
        try {
          if (!tool) throw new Error(`No tool '${name}' for role '${role}'`);
          const data = await tool.run(args);
          await emit({ type: "tool_result", id, ok: true, data });
          return data;
        } catch (err) {
          await emit({
            type: "tool_result",
            id,
            ok: false,
            data: err instanceof Error ? err.message : String(err),
          });
          return null;
        }
      }

      try {
        // Initial "Thinking" beat — the agent considers the request before
        // picking tools or starting to write.
        await emit({ type: "state", status: "Thinking" });
        await new Promise((r) => setTimeout(r, 500 + Math.random() * 400));

        if (role === "admin") {
          await runAdmin(msg, emitText, callTool);
        } else if (role === "professional") {
          await runProfessional(msg, emitText, callTool);
        } else {
          await runCustomer(msg, emitText, callTool);
        }
      } catch (err) {
        await emit({
          type: "text",
          delta: `\n\n_Something went wrong: ${err instanceof Error ? err.message : String(err)}_`,
        });
      } finally {
        await emit({ type: "done" });
        controller.close();
      }
    },
  });
}

type EmitText = (text: string) => Promise<void>;
type CallTool = (name: string, args: Record<string, unknown>) => Promise<unknown>;

async function runCustomer(msg: string, emitText: EmitText, callTool: CallTool) {
  // ─── Status / track ──────────────────────────────────────────────
  if (/status|track|where|update/.test(msg)) {
    const idMatch = msg.match(/#?(\d+)/);
    if (idMatch) {
      const id = Number(idMatch[1]);
      await emitText(`Pulling the details for request #${id}…`);
      const req = (await callTool("check_request_status", { id })) as RequestShape | null;
      if (!req) {
        await emitText(
          `\n\nI couldn't find a request with that ID under your account. Try **status** with no number and I'll list everything you have on record.`,
        );
        return;
      }
      const status = labelStatus(req.service_status);
      const sched = req.scheduled_time ? formatHuman(req.scheduled_time) : "no time set yet";
      await emitText(
        `\n\nRequest **#${req.id} · ${req.service_name}** is **${status}**.`,
      );
      if (req.professional_name) {
        await emitText(
          ` It's assigned to **${req.professional_name}**, who's scheduled to arrive ${sched} at ${req.address}, ${req.pincode}.`,
        );
      } else {
        await emitText(
          ` Nobody has claimed it yet — we're matching it with a pro for ${sched}.`,
        );
      }
      if (req.remarks) {
        await emitText(` Your note on the request: _"${req.remarks}"_.`);
      }
      await emitText(`\n\nNext step: ${nextStepForRequest(req)}`);
      return;
    }

    await emitText("Let me pull together a view of everything you have on the books…");
    const reqs = (await callTool("list_my_requests", {})) as RequestShape[] | null;
    if (!reqs?.length) {
      await emitText(
        "\n\nLooks like you don't have any service requests on record yet. Browse the catalogue or describe what you need in plain English and I'll walk you through booking your first one.",
      );
      return;
    }
    const byStatus = groupByStatus(reqs);
    const active = (byStatus.in_progress ?? []).concat(byStatus.accepted ?? []);
    const waiting = byStatus.requested ?? [];
    const done = byStatus.completed ?? [];

    await emitText(
      `\n\nYou have **${reqs.length}** request${reqs.length === 1 ? "" : "s"} on record — ${done.length} completed, ${active.length} active, ${waiting.length} waiting on a pro.`,
    );

    if (active.length) {
      await emitText(`\n\n**Active right now:**`);
      for (const r of active.slice(0, 3)) {
        await emitText(
          `\n- #${r.id} · **${r.service_name}** with ${r.professional_name ?? "an assigned pro"} — ${labelStatus(r.service_status)}, scheduled ${r.scheduled_time ? formatHuman(r.scheduled_time) : "soon"}`,
        );
      }
    }
    if (waiting.length) {
      await emitText(`\n\n**Still finding a pro:**`);
      for (const r of waiting.slice(0, 3)) {
        await emitText(
          `\n- #${r.id} · **${r.service_name}** at ${r.address.split(",")[0] || r.pincode}`,
        );
      }
    }
    await emitText(
      "\n\nWant me to dig into a specific one? Say **status #** followed by the request number.",
    );
    return;
  }

  // ─── Book / schedule ─────────────────────────────────────────────
  if (/book|schedule|order|hire/.test(msg)) {
    const intent = parseRequestIntent(msg);
    await emitText(
      `Reading that as a request for **${intent.category}** with **${intent.urgency}** urgency. Let me check what's in the catalogue…`,
    );
    const services = (await callTool("search_services", { query: intent.category })) as
      | ServiceShape[]
      | null;
    if (!services?.length) {
      await emitText(
        "\n\nNothing in the catalogue matched directly. Try a broader category like **Plumbing**, **Electrical**, **Cleaning**, or **Painting** and I'll pull up options.",
      );
      return;
    }
    const top = services[0];
    const others = services.slice(1, 3);
    await emitText(
      `\n\nThe closest fit is **${top.name}** at ₹${top.base_price} (~${top.time_required} min). ${top.description}`,
    );
    if (top.rating) {
      await emitText(
        ` It's rated **${top.rating}★** across ${top.review_count ?? "many"} bookings.`,
      );
    }
    if (others.length) {
      await emitText(
        `\n\nIf that's not quite right, also consider: ${others
          .map((s) => `**${s.name}** (₹${s.base_price})`)
          .join(" or ")}.`,
      );
    }
    await emitText(
      `\n\nI won't book without you confirming the details. Head to **Browse** and tap the service, or use the **Tell us what you need** button to pre-fill the form from your description and review before submitting.`,
    );
    return;
  }

  // ─── Search / find / recommend / fallback ────────────────────────
  const intent = parseRequestIntent(msg);
  const queryWord = pickSearchQuery(msg, intent);
  await emitText(`Searching the catalogue for **${queryWord}**…`);
  const results = (await callTool("search_services", { query: queryWord })) as
    | ServiceShape[]
    | null;
  if (!results?.length) {
    await emitText(
      `\n\nI didn't find a match for "${queryWord}". The catalogue covers ${CATEGORIES.slice(0, -1).join(", ")} and ${CATEGORIES.at(-1)} — try one of those, or describe what's wrong in plain English and I'll figure it out.`,
    );
    return;
  }
  const top = results.slice(0, 3);
  const avgPrice = Math.round(
    top.reduce((s, r) => s + r.base_price, 0) / top.length,
  );
  await emitText(
    `\n\nI found **${results.length}** option${results.length === 1 ? "" : "s"} matching that, averaging around ₹${avgPrice}. The top picks:`,
  );
  for (const s of top) {
    await emitText(
      `\n- **${s.name}** — ₹${s.base_price} · ~${s.time_required} min${
        s.rating ? ` · ${s.rating}★ (${s.review_count ?? 0} reviews)` : ""
      }\n  ${s.description}`,
    );
  }
  await emitText(
    `\n\nThe top match is what most neighbors book first. Want to go with that one, or should I narrow it down? You can also describe the situation in more detail and I'll re-rank.`,
  );
}

async function runProfessional(msg: string, emitText: EmitText, callTool: CallTool) {
  // ─── Weekly recap / earnings ─────────────────────────────────────
  if (/summary|recap|week|earning|how am i|how am i doing|stats/.test(msg)) {
    await emitText("Pulling your numbers across the last 30 days of activity…");
    const summary = (await callTool("weekly_summary", {})) as {
      completed_count: number;
      in_flight_count: number;
      pending_count: number;
    } | null;
    const reqs = (await callTool("list_pending_requests", {})) as RequestShape[] | null;
    if (!summary) {
      await emitText("\n\nCouldn't pull stats right now — try again in a moment.");
      return;
    }
    const total = summary.completed_count + summary.in_flight_count;
    const completion = total > 0
      ? Math.round((summary.completed_count / total) * 100)
      : null;

    await emitText(
      `\n\nHere's where you stand: **${summary.completed_count}** completed job${summary.completed_count === 1 ? "" : "s"}, **${summary.in_flight_count}** still in flight, and **${summary.pending_count}** fresh request${summary.pending_count === 1 ? "" : "s"} sitting in your inbox.`,
    );
    if (completion !== null) {
      await emitText(
        ` Your completion rate is sitting at **${completion}%** — ${completion >= 80 ? "above the platform average, nice work." : completion >= 50 ? "right around the average for your category." : "a bit below average; finishing in-flight jobs faster will lift this."}`,
      );
    }

    if (summary.pending_count > 0 && reqs?.length) {
      await emitText(
        `\n\nThe oldest waiting request is **#${reqs[reqs.length - 1].id}** at ${reqs[reqs.length - 1].address.split(",")[0] || reqs[reqs.length - 1].pincode}. Customers usually expect a response within 30 minutes — claim it with **accept #${reqs[reqs.length - 1].id}** if you can take it.`,
      );
    } else if (summary.pending_count === 0) {
      await emitText(
        `\n\nNo open requests in your category right now. Most pros use this window to update their bio or follow up on completed jobs for reviews.`,
      );
    }
    return;
  }

  // ─── Accept a specific request ───────────────────────────────────
  if (/accept|take|claim|grab/.test(msg)) {
    const idMatch = msg.match(/#?(\d+)/);
    if (idMatch) {
      const id = Number(idMatch[1]);
      await emitText(`Accepting request #${id} on your behalf…`);
      const result = (await callTool("accept_request", { id })) as RequestShape | null;
      if (result) {
        const sched = result.scheduled_time ? formatHuman(result.scheduled_time) : "soon";
        await emitText(
          `\n\nDone. **#${result.id} · ${result.service_name}** is now in your active queue. ${result.customer_name ?? "The customer"} is expecting you at **${result.address}, ${result.pincode}** ${sched}.`,
        );
        if (result.remarks) {
          await emitText(` Their note: _"${result.remarks}"_.`);
        }
        await emitText(
          `\n\nWhen you're on-site, switch the status to **In progress** from the Requests tab. Mark it **Completed** when you're done so the customer can leave a review.`,
        );
      } else {
        await emitText(
          `\n\nThat ID didn't accept — it may already be claimed by another pro or canceled. Say **inbox** to see what's still open.`,
        );
      }
      return;
    }
    await emitText(
      "Tell me which one to accept by number, e.g. **accept #42**. Or say **inbox** and I'll list what's open with their IDs.",
    );
    return;
  }

  // ─── Inbox / pending / fallback ──────────────────────────────────
  await emitText("Checking your inbox for unclaimed requests in your service area…");
  const reqs = (await callTool("list_pending_requests", {})) as RequestShape[] | null;
  if (!reqs?.length) {
    await emitText(
      "\n\nInbox is clear — no unclaimed requests in your category right now. New ones usually drop in the morning and after work hours, so check back in a few hours.",
    );
    return;
  }
  const oldest = reqs[reqs.length - 1];
  const newest = reqs[0];
  await emitText(
    `\n\nYou have **${reqs.length}** pending request${reqs.length === 1 ? "" : "s"} in your area. Here's the top of the queue:`,
  );
  for (const r of reqs.slice(0, 3)) {
    const sched = r.scheduled_time ? formatHuman(r.scheduled_time) : "flexible timing";
    await emitText(
      `\n- **#${r.id} · ${r.service_name}** at ${r.address.split(",")[0] || r.pincode} — ${sched}${r.remarks ? ` · _"${r.remarks}"_` : ""}`,
    );
  }
  if (reqs.length > 1) {
    await emitText(
      `\n\nOldest waiting is **#${oldest.id}** (best to grab first to keep your response time up). Newest is **#${newest.id}**. Reply with **accept #ID** and I'll claim it.`,
    );
  } else {
    await emitText(`\n\nReply with **accept #${oldest.id}** to claim it.`);
  }
}

async function runAdmin(msg: string, emitText: EmitText, callTool: CallTool) {
  // ─── Pending approvals ───────────────────────────────────────────
  if (/approval|pending|verify|application|review/.test(msg)) {
    await emitText("Pulling the approval queue and looking for risk signals…");
    const pending = (await callTool("list_pending_approvals", {})) as UserShape[] | null;
    if (!pending?.length) {
      await emitText(
        "\n\nThe approval queue is clear — no professionals waiting on review. New applications will appear here automatically.",
      );
      return;
    }
    await emitText(
      `\n\n**${pending.length}** professional${pending.length === 1 ? "" : "s"} awaiting review.`,
    );
    for (const p of pending.slice(0, 5)) {
      const tenure = p.experience ?? 0;
      const seniority = tenure >= 8 ? "veteran" : tenure >= 4 ? "experienced" : tenure >= 1 ? "junior" : "new";
      const bioIssue = !p.description || p.description.trim().length < 30;
      const flag = bioIssue
        ? " · ⚠️ thin bio"
        : tenure === 0
          ? " · ⚠️ no experience listed"
          : "";
      await emitText(
        `\n- **${p.full_name}** · ${seniority} ${p.service_name ?? "—"} in ${p.pincode ?? "unknown area"} · ${tenure} yr${tenure === 1 ? "" : "s"}${flag}`,
      );
    }
    if (pending.length > 5) {
      await emitText(`\n- _…and ${pending.length - 5} more on the Professionals tab._`);
    }
    const flagged = pending.filter(
      (p) => !p.description || p.description.trim().length < 30 || (p.experience ?? 0) === 0,
    ).length;
    if (flagged > 0) {
      await emitText(
        `\n\n**${flagged}** of these have a risk flag worth a closer look. The **AI summary** chip on each row gives you a one-glance recommendation (Approve / Request more info / Reject).`,
      );
    } else {
      await emitText(
        `\n\nNone of these have obvious risk signals — fast-approve candidates from the Professionals tab.`,
      );
    }
    return;
  }

  // ─── Metrics / overview / fallback ───────────────────────────────
  await emitText("Pulling the latest snapshot of platform activity…");
  const data = (await callTool("get_metrics", {})) as AnalyticsShape | null;
  if (!data) {
    await emitText("\n\nCouldn't fetch metrics right now — try again in a moment.");
    return;
  }
  const trends = data.request_trends ?? [];
  const total = trends.reduce((s, p) => s + p.count, 0);
  const mid = Math.floor(trends.length / 2);
  const earlier = trends.slice(0, mid).reduce((s, p) => s + p.count, 0);
  const latest = trends.slice(mid).reduce((s, p) => s + p.count, 0);
  const delta = earlier > 0 ? Math.round(((latest - earlier) / earlier) * 100) : null;
  const top3 = (data.service_popularity ?? []).slice(0, 3);
  const proPending = (data.professional_status ?? []).find((s) => s.status === "pending")?.count ?? 0;
  const userBlocked = (data.user_status ?? []).find((s) => s.status === "blocked")?.count ?? 0;
  const totalPros = (data.professional_status ?? []).reduce((s, p) => s + p.count, 0);

  await emitText(
    `\n\n**${total} lifetime requests** across the platform. `,
  );
  if (delta !== null) {
    if (delta > 10) {
      await emitText(
        `Booking volume is **up ${delta}%** vs the prior period — momentum is real, make sure professional supply keeps up.`,
      );
    } else if (delta < -10) {
      await emitText(
        `Booking volume is **down ${Math.abs(delta)}%** vs the prior period — worth investigating which categories cooled off.`,
      );
    } else {
      await emitText(
        `Volume is **steady** — within ${Math.abs(delta)}% of the prior period.`,
      );
    }
  }

  if (top3.length) {
    await emitText(`\n\n**Top categories** (last 90 days):`);
    for (const s of top3) {
      const share = total > 0 ? Math.round((s.count / total) * 100) : 0;
      await emitText(`\n- **${s.name}** — ${s.count} bookings (~${share}% of all activity)`);
    }
  }

  await emitText(`\n\n**Operations health**:`);
  await emitText(
    `\n- **${totalPros}** professionals on the roster${proPending > 0 ? `, with **${proPending}** awaiting approval` : ""}`,
  );
  if (proPending > 0) {
    await emitText(
      `\n- Approval queue: ${proPending} pending — say **show pending** to review them inline`,
    );
  }
  if (userBlocked > 0) {
    await emitText(
      `\n- ⚠️ **${userBlocked}** blocked user account${userBlocked === 1 ? "" : "s"} — review on the Users tab`,
    );
  }
  await emitText(
    `\n\nFor a deeper view, the **AI weekly digest** card on the Overview page narrates this same data and refreshes whenever you ask.`,
  );
}

// ──────────────────────────────────────────────── Helpers

function groupByStatus(reqs: RequestShape[]): Record<string, RequestShape[]> {
  const map: Record<string, RequestShape[]> = {};
  for (const r of reqs) {
    (map[r.service_status] ||= []).push(r);
  }
  return map;
}

function nextStepForRequest(r: RequestShape): string {
  switch (r.service_status) {
    case "requested":
      return "We're matching it with a pro in your area — no action needed from you yet.";
    case "accepted":
      return "Your pro is confirmed. They'll arrive at the scheduled time.";
    case "in_progress":
      return "Work is underway. You'll get a notification once it's marked complete.";
    case "completed":
      return "All done. Leave a review from the request details to help other neighbors.";
    case "cancelled":
      return "This one was cancelled. Want help booking a replacement?";
    default:
      return "—";
  }
}

function pickSearchQuery(msg: string, intent: RequestIntent): string {
  // If the message clearly mentions a category, use it.
  if (intent.category !== CATEGORIES[0] || /plumb|leak|tap|pipe|drain/.test(msg)) {
    return intent.category;
  }
  // Otherwise fall back to the most content-bearing word in the message.
  const words = msg
    .split(/\s+/)
    .filter((w) => w.length > 3 && !/^(find|need|want|looking|help|please|i'm)$/.test(w));
  return words[0] ?? intent.category;
}

function formatHuman(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const now = new Date();
  const sameDay = d.toDateString() === now.toDateString();
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  const isTomorrow = d.toDateString() === tomorrow.toDateString();
  const time = d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  if (sameDay) return `today at ${time}`;
  if (isTomorrow) return `tomorrow at ${time}`;
  return `${d.toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" })} at ${time}`;
}

// ──────────────────────────────────────────────── NL → request intent

export interface RequestIntent {
  category: string;
  urgency: "low" | "med" | "high";
  scheduledTime: string; // local datetime for <input type="datetime-local">
  scheduledLabel: string;
  summary: string;
}

const CATEGORY_KEYWORDS: Record<string, RegExp> = {
  Plumbing: /\b(plumb|leak|pipe|tap|faucet|sink|drain|toilet|geyser|water)\b/,
  Electrical: /\b(electric|wir|switch|fan|light|bulb|fuse|short circuit|inverter|ups)\b/,
  Carpentry: /\b(carpent|wood|door|window|hinge|furniture|shelf|cabinet)\b/,
  Cleaning: /\b(clean|dust|mop|sanitiz|deep clean|sofa|carpet)\b/,
  Painting: /\b(paint|wall|emulsion|texture|primer)\b/,
  "AC & Appliance": /\b(ac\b|air[- ]?conditioner|cooling|fridge|refrigerator|washing machine)\b/,
  "Pest Control": /\b(pest|cockroach|ant|termite|mosquito|rodent)\b/,
  Gardening: /\b(garden|lawn|hedge|plant|tree|mow|trim)\b/,
};

/**
 * Streams a one-sentence service description for an admin creating/editing a service.
 * Demo: returns a scripted string. Real: one-shot agent call with no history.
 */
export function generateServiceDescription(
  name: string,
  category: string,
): ReadableStream<AgentEvent> {
  if (DEMO) {
    const text = `Professional ${category.toLowerCase()} service covering ${name}, handled by vetted technicians with quality guaranteed.`;
    return streamScript(tokenize(text));
  }
  return runAgentSSE(
    `Write a single concise sentence describing the home service "${name}" (category: ${category}). Output only the sentence, no preamble.`,
    [],
    "",
  );
}

/** Maps free-form text to a structured booking draft (category, urgency, schedule). */
export function parseRequestIntent(text: string): RequestIntent {
  const lower = text.toLowerCase();

  let category: string = CATEGORIES[0];
  for (const cat of CATEGORIES) {
    if (CATEGORY_KEYWORDS[cat]?.test(lower)) {
      category = cat;
      break;
    }
  }

  let urgency: RequestIntent["urgency"] = "med";
  if (/\b(urgent|asap|emergency|right now|immediately|today)\b/.test(lower)) {
    urgency = "high";
  } else if (/\b(whenever|no rush|next week|sometime|flexible)\b/.test(lower)) {
    urgency = "low";
  }

  const now = new Date();
  const target = new Date(now);
  if (/\btoday|now|asap|urgent|emergency\b/.test(lower)) {
    target.setHours(target.getHours() + 2);
  } else if (/\btomorrow\b/.test(lower)) {
    target.setDate(target.getDate() + 1);
    target.setHours(/morning/.test(lower) ? 9 : /evening|night/.test(lower) ? 18 : 10, 0, 0, 0);
  } else if (/\bweekend|saturday\b/.test(lower)) {
    const daysToSat = (6 - target.getDay() + 7) % 7 || 7;
    target.setDate(target.getDate() + daysToSat);
    target.setHours(10, 0, 0, 0);
  } else if (/\bsunday\b/.test(lower)) {
    const daysToSun = (7 - target.getDay()) % 7 || 7;
    target.setDate(target.getDate() + daysToSun);
    target.setHours(10, 0, 0, 0);
  } else if (/\bnext week\b/.test(lower)) {
    target.setDate(target.getDate() + 7);
    target.setHours(10, 0, 0, 0);
  } else {
    target.setDate(target.getDate() + 1);
    target.setHours(10, 0, 0, 0);
  }

  const summary = capitalize(text.trim().slice(0, 200));
  return {
    category,
    urgency,
    scheduledTime: toLocalDatetimeInput(target),
    scheduledLabel: formatRelativeLabel(target),
    summary,
  };
}

function toLocalDatetimeInput(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function formatRelativeLabel(d: Date): string {
  const now = new Date();
  const diffH = (d.getTime() - now.getTime()) / 3_600_000;
  const time = d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  if (diffH < 6) return `in ~${Math.max(1, Math.round(diffH))} hour(s)`;
  if (d.toDateString() === now.toDateString()) return `today ${time}`;
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  if (d.toDateString() === tomorrow.toDateString()) return `tomorrow ${time}`;
  return d.toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" }) + ` ${time}`;
}

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function labelStatus(s: string): string {
  return s.replace("_", " ");
}
