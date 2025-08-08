import type { LoginPayload, RegisterPayload, UserProfile } from "@/types/user";
import axios from "axios";

export const AuthService = {
  loginByGoogle: async (): Promise<{ auth_url: string }> => {
    const res = await axios.get(
      `http://localhost:8003/api/v1/auth/google/auth-url`,
      { withCredentials: true },
    );
    return res.data;
  },
  getUser: async (): Promise<UserProfile> => {
    const res = await axios.get(`http://localhost:8003/api/v1/auth/profile`, {
      withCredentials: true,
    });
    return res.data;
  },
  Logout: async () => {
    const res = await axios.post(`http://localhost:8003/api/v1/auth/logout`, {
      withCredentials: true,
    });
    return res.data;
  },
  Register: async (userData: RegisterPayload) => {
    const res = await axios.post(
      `http://localhost:8003/api/v1/auth/register`,
      userData,
    );
    return res.data;
  },
  Login: async (userData: LoginPayload) => {
    const res = await axios.post(
      `http://localhost:8003/api/v1/auth/login`,
      userData,
    );
    return res.data;
  },
};
