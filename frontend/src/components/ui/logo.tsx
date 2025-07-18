import logoImg from "../../assets/logo.png";

export function Logo() {
  return (
    <div className="flex items-center gap-2">
      <img src={logoImg} alt="logo" className="w-13" />
      <p className="text-accent-foreground text-2xl font-bold">BullCapital</p>
    </div>
  );
}
