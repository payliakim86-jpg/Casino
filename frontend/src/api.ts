const KEY = "casino_token";

export const getToken = () => localStorage.getItem(KEY);
export const setToken = (t: string | null) =>
  t ? localStorage.setItem(KEY, t) : localStorage.removeItem(KEY);

export type Bonus = { can_claim: boolean; streak: number; amount: number };
export type GameId = "coinflip";
export type Limits = { min_bet: number; max_bet: number; coinflip_multiplier: number };
export type Me = { nickname: string; balance: number; bonus: Bonus; limits: Limits };
export type FlipResult = {
  round_id: number; pick: "heads" | "tails"; result: "heads" | "tails";
  won: boolean; bet: number; payout: number; balance: number;
};

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const res = await fetch(`/api${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = typeof body.detail === "string" ? body.detail : "Щось пішло не так";
    throw Object.assign(new Error(detail), { status: res.status });
  }
  return res.json();
}

export const api = {
  auth: (mode: "login" | "register", nickname: string, password: string) =>
    request<{ token: string }>(`/auth/${mode}`, {
      method: "POST",
      body: JSON.stringify({ nickname, password }),
    }),
  me: () => request<Me>("/me"),
  coinflip: (choice: "heads" | "tails", bet: number, requestId: string) =>
    request<FlipResult>("/games/coinflip", {
      method: "POST",
      body: JSON.stringify({ choice, bet, request_id: requestId }),
    }),
  claimBonus: () => request<Me>("/bonus/claim", { method: "POST" }),
};
