import { Button, Card, Input, List, Typography } from "antd";
import { useState } from "react";
import { workflows } from "../services/api";
import type { Workflow } from "../types";

export function Workflows() { const [name,setName]=useState(""); const [workflow,setWorkflow]=useState<Workflow|null>(null); const create=async()=>{const r=await workflows.create(name,[{name:"plan"},{name:"execute",depends_on:["plan"],approval_required:true}]); const full=await workflows.get(r.data.id); setWorkflow(full.data);}; return <><Typography.Title>Workflows</Typography.Title><Input.Search value={name} onChange={e=>setName(e.target.value)} onSearch={create} enterButton="Create" placeholder="Workflow name"/>{workflow && <Card title={`${workflow.name} · ${workflow.status}`}><List dataSource={workflow.steps} renderItem={step=><List.Item>{step.name} · {step.status} {step.approval_required && <Button onClick={()=>workflows.approve(workflow.id,step.id,"approved")}>Approve</Button>}</List.Item>}/></Card>}</>; }
