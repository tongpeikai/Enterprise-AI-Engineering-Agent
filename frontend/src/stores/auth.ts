import { create } from "zustand";
import { auth } from "../services/api";

type State = { user: Record<string, string> | null; loading: boolean; login: (email: string, password: string) => Promise<void>; logout: () => void; restore: () => Promise<void>; };
export const useAuth = create<State>((set) => ({ user: null, loading: false, login: async (email, password) => { set({ loading: true }); const result = await auth.login(email, password); sessionStorage.setItem("access_token", result.data.access_token); if (result.data.refresh_token) sessionStorage.setItem("refresh_token", result.data.refresh_token); const me = await auth.me(); set({ user: me.data, loading: false }); }, logout: () => { sessionStorage.clear(); set({ user: null }); }, restore: async () => { if (!sessionStorage.getItem("access_token")) return; try { const me = await auth.me(); set({ user: me.data }); } catch { sessionStorage.clear(); } } }));
