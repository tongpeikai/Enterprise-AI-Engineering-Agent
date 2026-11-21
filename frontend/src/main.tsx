import "antd/dist/reset.css";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Dashboard } from "./pages/Dashboard";
import { Approvals } from "./pages/Approvals";
import { Knowledge } from "./pages/Knowledge";
import { Login } from "./pages/Login";
import { Tasks } from "./pages/Tasks";
import { Tools } from "./pages/Tools";
import { Workflows } from "./pages/Workflows";
import { Workspace } from "./pages/Workspace";
import { useAuth } from "./stores/auth";

function App() { const user = useAuth(s=>s.user); return <Routes><Route path="/login" element={<Login/>}/><Route element={user ? <Layout/> : <Navigate to="/login" replace/>}><Route path="/" element={<Dashboard/>}/><Route path="/workspace" element={<Workspace/>}/><Route path="/approvals" element={<Approvals/>}/><Route path="/tasks" element={<Tasks/>}/><Route path="/workflows" element={<Workflows/>}/><Route path="/knowledge" element={<Knowledge/>}/><Route path="/tools" element={<Tools/>}/></Route></Routes>; }
ReactDOM.createRoot(document.getElementById("root")!).render(<React.StrictMode><BrowserRouter><App/></BrowserRouter></React.StrictMode>);
