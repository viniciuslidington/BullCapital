// Em /components/auth/RegisterForm.tsx

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { RegisterPayload } from "@/types/user";
import { useRegisterUser } from "@/hooks/queries/useauth";
import { DialogFooter } from "./dialog";

const initialState: RegisterPayload = {
  nome_completo: "",
  cpf: "",
  data_nascimento: "",
  email: "",
  senha: "",
};

export function RegisterForm() {
  const [formData, setFormData] = useState<RegisterPayload>(initialState);
  const { mutate: registerUser, isPending } = useRegisterUser();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    registerUser(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="grid gap-4">
      <div className="grid gap-2">
        <Label htmlFor="nome_completo">Nome completo</Label>
        <Input
          id="nome_completo"
          placeholder="Seu Nome Completo"
          onChange={handleChange}
          disabled={isPending}
          required
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="cpf">CPF</Label>
        <Input
          id="cpf"
          placeholder="000.000.000-00"
          onChange={handleChange}
          disabled={isPending}
          required
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="data_nascimento">Data de Nascimento</Label>
        <Input
          id="data_nascimento"
          type="date"
          onChange={handleChange}
          disabled={isPending}
          required
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="nome@exemplo.com"
          onChange={handleChange}
          disabled={isPending}
          required
        />
      </div>
      <div className="grid gap-2">
        <Label htmlFor="senha">Senha</Label>
        <Input
          id="senha"
          type="password"
          onChange={handleChange}
          disabled={isPending}
          required
        />
      </div>
      <DialogFooter className="pt-5">
        <Button type="submit" className="w-full" disabled={isPending}>
          {isPending ? "A criar conta..." : "Criar Conta"}
        </Button>
      </DialogFooter>
    </form>
  );
}
