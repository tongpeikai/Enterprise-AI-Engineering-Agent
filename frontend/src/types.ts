export type Task = { id: string; title: string; status: string; conversation_id: string; };
export type Workflow = { id: string; name: string; status: string; steps: Array<{ id: string; name: string; status: string; approval_required: boolean; }>; };
export type Document = { id: string; source: string; version: number; status: string; };
