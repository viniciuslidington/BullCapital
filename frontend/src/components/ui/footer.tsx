import { Logo } from "./logo";
import cin from "../../assets/cin-logo.png";
export function Footer() {
  return (
    <footer className="bg-background border-border flex w-full flex-col items-center gap-12 border-t-2 p-16">
      <span className="flex items-center gap-8">
        <Logo />
        <img src={cin} alt="" />
      </span>
      <p className="max-w-[900px] text-center text-sm">
        O BullCapital não tem como objetivo a recomendação e/ou sugestão de
        compra de ativos. Nosso site possui caráter meramente informativo e
        educativo, sempre trazendo informações de fontes públicas, deste modo,
        não nos responsabilizamos por qualquer decisão que o investidor venha a
        tomar a partir das informações contidas em nosso site.
      </p>
      <div>
        <p className="text-primary flex gap-3 text-sm font-medium">
          <a className="cursor-pointer hover:underline">Termos de uso</a>/
          <a className="cursor-pointer hover:underline">
            Política de Privacidade
          </a>
          /<a className="cursor-pointer hover:underline">Contato</a>/
          <a className="cursor-pointer hover:underline">Suporte</a>
        </p>
      </div>
    </footer>
  );
}
