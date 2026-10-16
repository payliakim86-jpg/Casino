import { useState } from "react";
import { api, type Me } from "./api";

type Side = "heads" | "tails";
const LABEL: Record<Side, string> = { heads: "Орел", tails: "Решка" };
const CHIPS = [10, 50, 100];

export default function CoinFlip({ me, setMe, onBack }: { me: Me; setMe: (m: Me) => void; onBack: () => void }) {
  const { min_bet, max_bet, coinflip_multiplier } = me.limits;
  const [pick, setPick] = useState<Side>("heads");
  const [bet, setBet] = useState(Math.min(50, max_bet));
  const [busy, setBusy] = useState(false);
  const [rot, setRot] = useState(0);
  const [msg, setMsg] = useState<{ text: string; won: boolean } | null>(null);
  const [error, setError] = useState("");

  const clamp = (v: number) => Math.max(min_bet, Math.min(max_bet, v));
  const poor = me.balance < bet;

  const play = async () => {
    setBusy(true);
    setError("");
    setMsg(null);
    try {
      const rid = crypto.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;
      const r = await api.coinflip(pick, bet, rid);
      const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      setRot(Math.ceil(rot / 360) * 360 + 1440 + (r.result === "tails" ? 180 : 0));
      await new Promise((done) => setTimeout(done, reduce ? 0 : 1300));
      setMe({ ...me, balance: r.balance });
      setMsg(
        r.won
          ? { text: `Виграш: +${r.payout - r.bet} монет`, won: true }
          : { text: `Не пощастило: −${r.bet} монет`, won: false },
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="screen">
      <header className="topbar">
        <button className="link" onClick={onBack} disabled={busy}>‹ Назад</button>
        <h1 className="display title">Монетка</h1>
        <span className="pill">
          <span className="coin" aria-hidden="true" />
          <strong>{me.balance.toLocaleString("uk-UA")}</strong>
        </span>
      </header>

      <div className="stage">
        <div className="coin3d" style={{ transform: `rotateY(${rot}deg)` }}>
          <div className="face front">♛</div>
          <div className="face back">◈</div>
        </div>
      </div>

      <div className="sides" role="group" aria-label="Ваш вибір">
        {(["heads", "tails"] as Side[]).map((s) => (
          <button key={s} className={pick === s ? "side on" : "side"} aria-pressed={pick === s}
            disabled={busy} onClick={() => setPick(s)}>
            {LABEL[s]}
          </button>
        ))}
      </div>

      <section className="card betbox">
        <div className="stepper">
          <button className="ghost" aria-label="Менше" disabled={busy} onClick={() => setBet(clamp(bet - min_bet))}>−</button>
          <div>
            <p className="muted">Ставка</p>
            <strong className="betval">{bet}</strong>
          </div>
          <button className="ghost" aria-label="Більше" disabled={busy} onClick={() => setBet(clamp(bet + min_bet))}>+</button>
        </div>
        <div className="chips">
          {CHIPS.map((c) => (
            <button key={c} className={bet === c ? "chip on" : "chip"} disabled={busy} onClick={() => setBet(clamp(c))}>{c}</button>
          ))}
        </div>
        <p className="muted">Виплата ×{coinflip_multiplier} · ставка {min_bet}–{max_bet}</p>
      </section>

      {msg && <p className={msg.won ? "result win" : "result lose"} role="status">{msg.text}</p>}
      {error && <p className="error" role="alert">{error}</p>}
      {poor && !busy && <p className="muted">Недостатньо монет для такої ставки.</p>}

      <button className="primary wide" disabled={busy || poor} onClick={play}>
        {busy ? "Крутимо…" : "Крутити"}
      </button>
    </main>
  );
}
