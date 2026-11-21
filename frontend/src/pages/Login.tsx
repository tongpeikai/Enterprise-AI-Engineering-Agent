import { Form, Input, Button, Card, message } from "antd";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../stores/auth";

export function Login() { const login = useAuth((s) => s.login); const navigate = useNavigate(); const submit = async (values: {email:string;password:string}) => { try { await login(values.email, values.password); navigate("/"); } catch { message.error("Login failed"); } }; return <Card title="Enterprise Agent Login" style={{ maxWidth: 420, margin: "80px auto" }}><Form onFinish={submit}><Form.Item name="email" rules={[{required:true,type:"email"}]}><Input placeholder="Email" /></Form.Item><Form.Item name="password" rules={[{required:true}]}><Input.Password placeholder="Password" /></Form.Item><Button type="primary" htmlType="submit" block>Sign in</Button></Form></Card>; }
