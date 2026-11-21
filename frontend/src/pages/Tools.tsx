import { List, Typography } from "antd";
import { useEffect, useState } from "react";
import { tools } from "../services/api";

export function Tools() { const [items,setItems]=useState<Array<{name:string;permission:string}>>([]); useEffect(()=>{tools.list().then(r=>setItems(r.data)).catch(()=>setItems([]));},[]); return <><Typography.Title>Tools</Typography.Title><List dataSource={items} locale={{emptyText:"No tools available"}} renderItem={tool=><List.Item>{tool.name} · {tool.permission}</List.Item>}/></>; }
