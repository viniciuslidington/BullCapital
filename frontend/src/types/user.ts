export type UserProfile = {
  id: string;
  nome_completo: string;
  data_nascimento: string; // pode ser Date se já vier como objeto Date
  email: string;
  created_at: string; // ou Date
  updated_at: string; // ou Date
  profile_picture: string | null; // caso a imagem possa ser nula
};

export type RegisterPayload = {
  nome_completo: string;
  cpf: string;
  data_nascimento: string; // Formato "YYYY-MM-DD"
  email: string;
  senha: string;
};

export type LoginPayload = {
  email: string;
  senha: string;
};
