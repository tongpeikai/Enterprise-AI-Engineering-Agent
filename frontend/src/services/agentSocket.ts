export type AgentEvent = { id?: string; key?: string; type?: string; [key: string]: unknown };
export function acceptEvent(cursor: string, event: AgentEvent): { accepted: boolean; cursor: string } { const id = String(event.id ?? ""); return { accepted: Boolean(id && id !== cursor), cursor: id || cursor }; }

export class AgentSocket {
  private socket: WebSocket | null = null;
  private stopped = false;
  private retry = 0;
  private cursor = "";
  constructor(private readonly baseUrl: string, private readonly token: string, private readonly onEvent: (event: AgentEvent) => void, private readonly onStatus: (status: string) => void) {}
  connect(conversationId: string) { this.stopped = false; this.open(conversationId); }
  private open(conversationId: string) { if (this.stopped) return; const url = this.baseUrl.replace(/^http/, "ws") + `/sockets/events/${conversationId}`; this.onStatus("connecting"); this.socket = new WebSocket(url); this.socket.onopen = () => { this.retry = 0; this.onStatus("connected"); this.socket?.send(JSON.stringify({ type: "auth", session_api_key: this.token })); }; this.socket.onmessage = (message) => { const event = JSON.parse(message.data) as AgentEvent; const result = acceptEvent(this.cursor, event); if (!result.accepted) return; this.cursor = result.cursor; this.onEvent(event); }; this.socket.onerror = () => this.onStatus("error"); this.socket.onclose = () => { if (!this.stopped) { this.onStatus("reconnecting"); const delay = Math.min(1000 * 2 ** this.retry++, 8000); window.setTimeout(() => this.open(conversationId), delay); } }; }
  close() { this.stopped = true; this.socket?.close(); this.onStatus("closed"); }
}
