import { Button, Input, List, Tag, Typography } from "antd";
import { useEffect, useState } from "react";
import { tasks } from "../services/api";
import type { Task } from "../types";

export function Tasks() { const [items,setItems]=useState<Task[]>([]); const [title,setTitle]=useState(""); const load=()=>tasks.list().then(r=>setItems(r.data)); useEffect(()=>{void load();},[]); const create=async()=>{if(title.trim()){await tasks.create(title);setTitle("");void load();}}; return <><Typography.Title>Tasks</Typography.Title><Input.Search value={title} onChange={e=>setTitle(e.target.value)} onSearch={create} enterButton="Create" placeholder="Task title"/><List dataSource={items} renderItem={item=><List.Item actions={[item.status === "running" ? <Button onClick={()=>tasks.transition(item.id,"cancelled")}>Cancel</Button>:null]}><List.Item.Meta title={item.title} description={item.conversation_id || "Not started"}/><Tag>{item.status}</Tag></List.Item>}/></>; }
