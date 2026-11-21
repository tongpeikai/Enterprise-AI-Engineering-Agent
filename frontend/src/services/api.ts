import axios from "axios";

export const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1" });
api.interceptors.request.use((config) => { const token = sessionStorage.getItem("access_token"); if (token) config.headers.Authorization = `Bearer ${token}`; return config; });
export const auth = {
  login: (email: string, password: string) => api.post("/auth/login", { email, password }),
  register: (email: string, password: string, organization_id: string) => api.post("/auth/register", { email, password, organization_id }),
  me: () => api.get("/auth/me"),
};
export const tasks = { list: () => api.get("/tasks"), create: (title: string) => api.post("/tasks", { title }), transition: (id: string, status: string) => api.post(`/tasks/${id}/transition`, { status }) };
export const workflows = { list: () => api.get("/workflows"), create: (name: string, steps: object[]) => api.post("/workflows", { name, steps }), get: (id: string) => api.get(`/workflows/${id}`), ready: (id: string) => api.get(`/workflows/${id}/ready`), approve: (id: string, step_id: string, decision: string) => api.post(`/workflows/${id}/approve`, { step_id, decision }), history: (id: string) => api.get(`/workflows/${id}/history`) };
export const knowledge = { list: () => api.get("/knowledge/documents"), ingest: (source: string, content: string) => api.post("/knowledge/documents", { source, content }), search: (query: string) => api.post("/knowledge/search", { query }) };
export const tools = { list: () => api.get("/tools") };
export const metrics = { summary: () => api.get("/metrics/summary"), benchmarks: () => api.get("/benchmarks"), runBenchmark: () => api.post("/benchmarks/run") };
