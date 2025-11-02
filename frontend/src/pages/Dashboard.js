import React, { useState, useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API, AuthContext } from "@/App";
import Layout from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Server, HardDrive, Activity, Users } from "lucide-react";

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [servers, setServers] = useState([]);
  const [nodes, setNodes] = useState([]);
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
    fetchServers();
    fetchNodes();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Failed to fetch stats", error);
    }
  };

  const fetchServers = async () => {
    try {
      const response = await axios.get(`${API}/servers`);
      setServers(response.data);
    } catch (error) {
      console.error("Failed to fetch servers", error);
    }
  };

  const fetchNodes = async () => {
    try {
      const response = await axios.get(`${API}/nodes`);
      setNodes(response.data);
    } catch (error) {
      console.error("Failed to fetch nodes", error);
    }
  };

  const statCards = [
    {
      title: "Total Servers",
      value: stats?.total_servers || 0,
      icon: Server,
      color: "from-cyan-500 to-blue-600",
      testId: "stat-total-servers"
    },
    {
      title: "Running Servers",
      value: stats?.running_servers || 0,
      icon: Activity,
      color: "from-green-500 to-emerald-600",
      testId: "stat-running-servers"
    },
    {
      title: "Total Nodes",
      value: stats?.total_nodes || 0,
      icon: HardDrive,
      color: "from-purple-500 to-violet-600",
      testId: "stat-total-nodes"
    },
    {
      title: "Total Users",
      value: stats?.total_users || 0,
      icon: Users,
      color: "from-orange-500 to-red-600",
      testId: "stat-total-users"
    },
  ];

  return (
    <Layout>
      <div className="space-y-8" data-testid="dashboard-page">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">Welcome back, {user?.username}!</h1>
          <p className="text-slate-400">Here's an overview of your game server infrastructure</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <Card
                key={index}
                data-testid={stat.testId}
                className="glass border-slate-700 card-hover animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-slate-300">
                    {stat.title}
                  </CardTitle>
                  <div className={`p-2 rounded-lg bg-gradient-to-br ${stat.color}`}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-white">{stat.value}</div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="glass border-slate-700" data-testid="recent-servers-card">
            <CardHeader>
              <CardTitle className="text-white">Recent Servers</CardTitle>
              <CardDescription className="text-slate-400">Your latest game servers</CardDescription>
            </CardHeader>
            <CardContent>
              {servers.length === 0 ? (
                <p className="text-slate-400 text-center py-8">No servers yet. Create one to get started!</p>
              ) : (
                <div className="space-y-3">
                  {servers.slice(0, 5).map((server) => (
                    <div
                      key={server.id}
                      data-testid={`server-item-${server.id}`}
                      className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition cursor-pointer"
                      onClick={() => navigate("/servers")}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`status-dot ${
                          server.status === 'running' ? 'status-online' :
                          server.status === 'stopped' ? 'status-offline' : 'status-warning'
                        }`}></div>
                        <div>
                          <p className="font-medium text-white">{server.name}</p>
                          <p className="text-sm text-slate-400">{server.game_type.toUpperCase()}</p>
                        </div>
                      </div>
                      <span className="text-xs px-2 py-1 rounded-full bg-slate-700 text-slate-300">
                        {server.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="glass border-slate-700" data-testid="nodes-status-card">
            <CardHeader>
              <CardTitle className="text-white">Node Status</CardTitle>
              <CardDescription className="text-slate-400">Server node health overview</CardDescription>
            </CardHeader>
            <CardContent>
              {nodes.length === 0 ? (
                <p className="text-slate-400 text-center py-8">No nodes configured. Add one to start hosting servers!</p>
              ) : (
                <div className="space-y-3">
                  {nodes.map((node) => (
                    <div
                      key={node.id}
                      data-testid={`node-item-${node.id}`}
                      className="p-3 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition cursor-pointer"
                      onClick={() => navigate("/nodes")}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <div className={`status-dot ${
                            node.status === 'online' ? 'status-online' : 'status-offline'
                          }`}></div>
                          <span className="font-medium text-white">{node.name}</span>
                        </div>
                        <span className="text-xs px-2 py-1 rounded-full bg-slate-700 text-slate-300">
                          {node.status}
                        </span>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        <div>
                          <p className="text-slate-400">CPU</p>
                          <p className="text-white font-medium">{node.used_cpu}/{node.cpu_cores}</p>
                        </div>
                        <div>
                          <p className="text-slate-400">RAM</p>
                          <p className="text-white font-medium">{node.used_ram}/{node.ram_gb}GB</p>
                        </div>
                        <div>
                          <p className="text-slate-400">Storage</p>
                          <p className="text-white font-medium">{node.used_storage}/{node.storage_gb}GB</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;