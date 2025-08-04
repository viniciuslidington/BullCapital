import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8002/api/v1/frontend", // ou sua URL pública
});
