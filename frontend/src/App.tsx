import { useEffect, useState } from "react";
import { api, getToken, setToken, type GameId, type Me } from "./api";
import CoinFlip from "./CoinFlip";

type Tab = "games" | "leaders" | "profile";

type Game = { name: string; icon: string; id?: GameId };

const GAMES: Game[] = [
  { name: "Монетка", icon: "coin", id: "coinflip" },
  { name: "Кості", icon: "⚄" },
  { name: "Рулетка", icon: "◉" },
  { name: "Слоти", icon: "777" },
  { name: "Блекджек", icon: "♠" },
  { name: "Crash", icon: "↗" },
];

function AuthForm({ onDone }: { onDone: () => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [nickname, setNickname] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submit = async () => {
    setError("");
    try {
      const { token } = await api.auth(mode, nickname.trim(), password);
      setToken(token);
      onDone();
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <main className="screen narrow">
      <span className="coin big" aria-hidden="true" />
      <h1 className="display">Casino</h1>
      <p className="muted">Віртуальні монети, без реальних грошей.</p>
      <input placeholder="Нік" value={nickname} onChange={(e) => setNickname(e.target.value)} />
      <input
        placeholder="Пароль (від 6 символів)"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p className="error">{error}</p>}
      <button className="primary" onClick={submit}>
        {mode === "login" ? "Увійти" : "Створити акаунт"}
      </button>
      <button className="link" onClick={() => setMode(mode === "login" ? "register" : "login")}>
        {mode === "login" ? "Немає акаунта? Зареєструватися" : "Уже є акаунт? Увійти"}
      </button>
    </main>
  );
}

function BonusCard({ me, setMe }: { me: Me; setMe: (m: Me) => void }) {
  const [busy, setBusy] = useState(false);
  const { can_claim, streak, amount } = me.bonus;
  const current = Math.min(streak, 7);
  const claim = async () => {
    setBusy(true);
    try {
      setMe(await api.claimBonus());
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="card bonus">
      <div className="bonus-head">
        <div>
          <h2 className="display">Щоденний бонус</h2>
          <p className="muted">
            {can_claim ? `День ${streak}: +${amount} монет` : `Отримано. Завтра +${amount} монет`}
          </p>
        </div>
        <button className="primary" disabled={!can_claim || busy} onClick={claim}>
          Забрати
        </button>
      </div>
      <ol className="days" aria-label="Серія днів">
        {Array.from({ length: 7 }, (_, i) => i + 1).map((d) => {
          const done = can_claim ? d < current : d <= current;
          const now = can_claim && d === current;
          return (
            <li key={d} className={done ? "done" : now ? "now" : ""}>
              <span className="dot" />
              <span className="muted">{d}</span>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

function GamesTab({ me, setMe, onOpen }: { me: Me; setMe: (m: Me) => void; onOpen: (id: GameId) => void }) {
  return (
    <>
      <BonusCard me={me} setMe={setMe} />
      <h2 className="display section">Ігри</h2>
      <section className="games">
        {GAMES.map((g) => {
          const icon =
            g.icon === "coin" ? (
              <span className="coin" aria-hidden="true" />
            ) : (
              <span className="glyph" aria-hidden="true">{g.icon}</span>
            );
          return g.id ? (
            <button key={g.name} className="card game playable" onClick={() => onOpen(g.id!)}>
              {icon}
              <h3>{g.name}</h3>
              <p className="muted">Грати</p>
            </button>
          ) : (
            <div key={g.name} className="card game" aria-disabled="true">
              {icon}
              <h3>{g.name}</h3>
              <p className="muted">Скоро</p>
            </div>
          );
        })}
      </section>
    </>
  );
}

function Soon({ title }: { title: string }) {
  return (
    <section className="card empty">
      <h2 className="display">{title}</h2>
      <p className="muted">Цей розділ з’явиться після перших ігор.</p>
    </section>
  );
}

function Profile({ me, logout }: { me: Me; logout: () => void }) {
  return (
    <section className="card empty">
      <span className="avatar big">{me.nickname[0]?.toUpperCase()}</span>
      <h2 className="display">{me.nickname}</h2>
      <button className="ghost" onClick={logout}>Вийти з акаунта</button>
    </section>
  );
}

const TABS: { id: Tab; label: string }[] = [
  { id: "games", label: "Ігри" },
  { id: "leaders", label: "Рейтинг" },
  { id: "profile", label: "Профіль" },
];

function Lobby({ me, setMe, logout }: { me: Me; setMe: (m: Me) => void; logout: () => void }) {
  const [tab, setTab] = useState<Tab>("games");
  const [game, setGame] = useState<GameId | null>(null);
  if (game === "coinflip") return <CoinFlip me={me} setMe={setMe} onBack={() => setGame(null)} />;
  return (
    <>
      <main className="screen with-nav">
        <header className="topbar">
          <span className="avatar">{me.nickname[0]?.toUpperCase()}</span>
          <span className="nick">{me.nickname}</span>
          <span className="pill">
            <span className="coin" aria-hidden="true" />
            <strong>{me.balance.toLocaleString("uk-UA")}</strong>
          </span>
        </header>
        {tab === "games" && <GamesTab me={me} setMe={setMe} onOpen={setGame} />}
        {tab === "leaders" && <Soon title="Рейтинг" />}
        {tab === "profile" && <Profile me={me} logout={logout} />}
      </main>
      <nav className="tabbar">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={t.id === tab ? "active" : ""}
            aria-current={t.id === tab ? "page" : undefined}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </nav>
    </>
  );
}

export default function App() {
  const [authed, setAuthed] = useState(!!getToken());
  const [me, setMe] = useState<Me | null>(null);

  const logout = () => {
    setToken(null);
    setMe(null);
    setAuthed(false);
  };

  useEffect(() => {
    if (!authed) return;
    api.me().then(setMe).catch((e) => e.status === 401 && logout());
  }, [authed]);

  if (!authed) return <AuthForm onDone={() => setAuthed(true)} />;
  if (!me) return <main className="screen"><p className="muted">Завантаження…</p></main>;
  return <Lobby me={me} setMe={setMe} logout={logout} />;
}
