import { useNavigate } from "react-router-dom";
import logoImg from "../../assets/logo.png";

export function Logo() {
  const navigate = useNavigate();
  return (
    <div
      className="flex cursor-pointer items-center gap-2"
      onClick={() => navigate("")}
    >
      <img src={logoImg} alt="logo" className="w-13" />
      <p className="text-accent-foreground text-2xl font-bold">BullCapital</p>
    </div>
  );
}
