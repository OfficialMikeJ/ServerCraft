import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import Layout from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { Plus, Play, Square, RotateCw, Trash2, FolderOpen, Upload } from "lucide-react";

const ServersPage = () => {
  const [servers, setServers] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showFileDialog, setShowFileDialog] = useState(false);
  const [selectedServer, setSelectedServer] = useState(null);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    game_type: "arma3",
    node_id: "",
    port: 2302,
    cpu_limit: 2,
    ram_limit_gb: 4,
    storage_limit_gb: 50,
  });

  useEffect(() => {
    fetchServers();
    fetchNodes();
  }, []);

  const fetchServers = async () => {
    try {
      const response = await axios.get(`${API}/servers`);
      setServers(response.data);
    } catch (error) {
      toast.error("Failed to fetch servers");
    }
  };

  const fetchNodes = async () => {
    try {
      const response = await axios.get(`${API}/nodes`);
      setNodes(response.data);
    } catch (error) {
      toast.error("Failed to fetch nodes");
    }
  };

  const handleCreateServer = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/servers`, formData);
      toast.success("Server created successfully!");
      setShowCreateDialog(false);
      fetchServers();
      setFormData({
        name: "",
        game_type: "arma3",
        node_id: "",
        port: 2302,
        cpu_limit: 2,
        ram_limit_gb: 4,
        storage_limit_gb: 50,
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create server");
    } finally {
      setLoading(false);
    }
  };

  const handleServerAction = async (serverId, action) => {
    try {
      await axios.post(`${API}/servers/${serverId}/${action}`);
      toast.success(`Server ${action} successful!`);
      setTimeout(fetchServers, 1000);
    } catch (error) {
      toast.error(error.response?.data?.detail || `Failed to ${action} server`);
    }
  };

  const handleDeleteServer = async (serverId) => {
    if (!window.confirm("Are you sure you want to delete this server?")) return;
    
    try {
      await axios.delete(`${API}/servers/${serverId}`);
      toast.success("Server deleted successfully!");
      fetchServers();
    } catch (error) {
      toast.error("Failed to delete server");
    }
  };

  const gameTypes = [
    { value: "arma3", label: "Arma 3" },
    { value: "rust", label: "Rust" },
    { value: "dayz", label: "DayZ" },
    { value: "squad", label: "Squad" },
    { value: "reforger", label: "Arma Reforger" },
  ];

  return (
    <Layout>
      <div className="space-y-6" data-testid="servers-page">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Game Servers</h1>
            <p className="text-slate-400">Manage your game server instances</p>
          </div>
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button
                data-testid="create-server-button"
                className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Server
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-slate-800 border-slate-700 text-white max-w-2xl" data-testid="create-server-dialog">
              <DialogHeader>
                <DialogTitle>Create New Game Server</DialogTitle>
                <DialogDescription className="text-slate-400">
                  Configure and deploy a new game server instance
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreateServer} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="server-name">Server Name</Label>
                    <Input
                      id="server-name"
                      data-testid="server-name-input"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      required
                      className="bg-slate-700 border-slate-600"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="game-type">Game Type</Label>
                    <Select
                      value={formData.game_type}
                      onValueChange={(value) => setFormData({ ...formData, game_type: value })}
                    >
                      <SelectTrigger data-testid="game-type-select" className="bg-slate-700 border-slate-600">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-700 border-slate-600">
                        {gameTypes.map((game) => (
                          <SelectItem key={game.value} value={game.value}>
                            {game.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="node">Node</Label>
                    <Select
                      value={formData.node_id}
                      onValueChange={(value) => setFormData({ ...formData, node_id: value })}
                    >
                      <SelectTrigger data-testid="node-select" className="bg-slate-700 border-slate-600">
                        <SelectValue placeholder="Select a node" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-700 border-slate-600">
                        {nodes.map((node) => (
                          <SelectItem key={node.id} value={node.id}>
                            {node.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="port">Port</Label>
                    <Input
                      id="port"
                      data-testid="port-input"
                      type="number"
                      value={formData.port}
                      onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
                      required
                      className="bg-slate-700 border-slate-600"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cpu">CPU Cores</Label>
                    <Input
                      id="cpu"
                      data-testid="cpu-input"
                      type="number"
                      step="0.5"
                      value={formData.cpu_limit}
                      onChange={(e) => setFormData({ ...formData, cpu_limit: parseFloat(e.target.value) })}
                      required
                      className="bg-slate-700 border-slate-600"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="ram">RAM (GB)</Label>
                    <Input
                      id="ram"
                      data-testid="ram-input"
                      type="number"
                      value={formData.ram_limit_gb}
                      onChange={(e) => setFormData({ ...formData, ram_limit_gb: parseFloat(e.target.value) })}
                      required
                      className="bg-slate-700 border-slate-600"
                    />
                  </div>
                  <div className="space-y-2 col-span-2">
                    <Label htmlFor="storage">Storage (GB)</Label>
                    <Input
                      id="storage"
                      data-testid="storage-input"
                      type="number"
                      value={formData.storage_limit_gb}
                      onChange={(e) => setFormData({ ...formData, storage_limit_gb: parseFloat(e.target.value) })}
                      required
                      className="bg-slate-700 border-slate-600"
                    />
                  </div>
                </div>
                <Button
                  data-testid="submit-create-server"
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-600"
                >
                  {loading ? "Creating..." : "Create Server"}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {servers.length === 0 ? (
          <Card className="glass border-slate-700">
            <CardContent className="py-16 text-center">
              <p className="text-slate-400 mb-4">No servers yet. Create your first game server!</p>
              <Button
                onClick={() => setShowCreateDialog(true)}
                className="bg-gradient-to-r from-cyan-500 to-blue-600"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Server
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {servers.map((server, index) => (
              <Card
                key={server.id}
                data-testid={`server-card-${server.id}`}
                className="glass border-slate-700 card-hover animate-fade-in"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-white flex items-center space-x-2">
                        <span>{server.name}</span>
                        <div className={`status-dot ${
                          server.status === 'running' ? 'status-online' :
                          server.status === 'stopped' ? 'status-offline' : 'status-warning'
                        }`}></div>
                      </CardTitle>
                      <CardDescription className="text-slate-400">
                        {server.game_type.toUpperCase()} • Port {server.port}
                      </CardDescription>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      server.status === 'running' ? 'bg-green-500/20 text-green-400' :
                      server.status === 'stopped' ? 'bg-red-500/20 text-red-400' :
                      'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {server.status}
                    </span>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-3 gap-3 text-sm">
                    <div className="p-2 rounded-lg bg-slate-800/50">
                      <p className="text-slate-400 text-xs">CPU</p>
                      <p className="text-white font-medium">{server.cpu_limit} cores</p>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-800/50">
                      <p className="text-slate-400 text-xs">RAM</p>
                      <p className="text-white font-medium">{server.ram_limit_gb}GB</p>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-800/50">
                      <p className="text-slate-400 text-xs">Storage</p>
                      <p className="text-white font-medium">{server.storage_limit_gb}GB</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button
                      data-testid={`start-server-${server.id}`}
                      size="sm"
                      onClick={() => handleServerAction(server.id, 'start')}
                      disabled={server.status === 'running'}
                      className="flex-1 bg-green-600 hover:bg-green-700"
                    >
                      <Play className="w-4 h-4 mr-1" />
                      Start
                    </Button>
                    <Button
                      data-testid={`stop-server-${server.id}`}
                      size="sm"
                      onClick={() => handleServerAction(server.id, 'stop')}
                      disabled={server.status === 'stopped'}
                      className="flex-1 bg-red-600 hover:bg-red-700"
                    >
                      <Square className="w-4 h-4 mr-1" />
                      Stop
                    </Button>
                    <Button
                      data-testid={`restart-server-${server.id}`}
                      size="sm"
                      onClick={() => handleServerAction(server.id, 'restart')}
                      className="flex-1 bg-yellow-600 hover:bg-yellow-700"
                    >
                      <RotateCw className="w-4 h-4 mr-1" />
                      Restart
                    </Button>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button
                      data-testid={`files-server-${server.id}`}
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSelectedServer(server);
                        setShowFileDialog(true);
                      }}
                      className="flex-1 border-slate-600 hover:bg-slate-700"
                    >
                      <FolderOpen className="w-4 h-4 mr-1" />
                      Files
                    </Button>
                    <Button
                      data-testid={`delete-server-${server.id}`}
                      size="sm"
                      variant="outline"
                      onClick={() => handleDeleteServer(server.id)}
                      className="border-red-600 text-red-400 hover:bg-red-600/10"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default ServersPage;