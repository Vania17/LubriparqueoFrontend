type TopBarProps = {
  title: string;
};

export function TopBar({ title }: TopBarProps) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Panel de trabajo</p>
        <h1>{title}</h1>
      </div>
      <div className="user-chip" aria-label="Usuario actual">
        Gerencia
      </div>
    </header>
  );
}
