import React, { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import Layout from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { toast } from "sonner";
import { Plus, Server, Trash2, Edit } from "lucide-react";

const NodesPage = () => {
  const [nodes, setNodes] = useState([]);
  const [showDialog, setShowDialog] = useState(false);
  const [editingNode, setEditingNode] = useState(null);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    host: "localhost",
    port: 2375,
    cpu_cores: 4,
    ram_gb: 8,
    storage_gb: 100,
  });

  useEffect(() => {
    fetchNodes();
  }, []);

  const fetchNodes = async () => {
    try {
      const response = await axios.get(`${API}/nodes`);
      setNodes(response.data);
    } catch (error) {
      toast.error("Failed to fetch nodes");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (editingNode) {
        await axios.put(`${API}/nodes/${editingNode.id}`, formData);
        toast.success("Node updated successfully!");
      } else {
        await axios.post(`${API}/nodes`, formData);
        toast.success("Node created successfully!");
      }
      setShowDialog(false);
      fetchNodes();
      resetForm();
    } catch (error) {
      toast.error(error.response?.data?.detail || `Failed to ${editingNode ? 'update' : 'create'} node`);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (nodeId) => {
    if (!window.confirm("Are you sure you want to delete this node?")) return;
    
    try {
      await axios.delete(`${API}/nodes/${nodeId}`);
      toast.success("Node deleted successfully!");
      fetchNodes();
    } catch (error) {
      toast.error("Failed to delete node");
    }
  };

  const handleEdit = (node) => {
    setEditingNode(node);
    setFormData({
      name: node.name,
      host: node.host,
      port: node.port,
      cpu_cores: node.cpu_cores,
      ram_gb: node.ram_gb,
      storage_gb: node.storage_gb,
    });
    setShowDialog(true);
  };

  const resetForm = () => {
    setEditingNode(null);
    setFormData({
      name: "",
      host: "localhost",
      port: 2375,
      cpu_cores: 4,
      ram_gb: 8,
      storage_gb: 100,
    });
  };

  const calculateUsagePercentage = (used, total) => {
    return total > 0 ? (used / total) * 100 : 0;
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="nodes-page">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Server Nodes</h1>
            <p className="text-slate-400">Manage your infrastructure nodes</p>
          </div>
          <Dialog open={showDialog} onOpenChange={(open) => {
            setShowDialog(open);
            if (!open) resetForm();
          }}>
            <DialogTrigger asChild>
              <Button
                data-testid="create-node-button"
                className="bg-gradient-to-r from-purple-500 to-violet-600 hover:from-purple-600 hover:to-violet-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Node
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-slate-800 border-slate-700 text-white" data-testid="node-dialog">
              <DialogHeader>
                <DialogTitle>{editingNode ? 'Edit' : 'Add'} Server Node</DialogTitle>
                <DialogDescription className="text-slate-400">
                  Configure node resources and connection details
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="node-name">Node Name</Label>
                  <Input
                    id="node-name"
                    data-testid="node-name-input"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Primary Node"
                    required
                    className="bg-slate-700 border-slate-600"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="host">Host</Label>
                    <Input
                      id="host"
                      data-testid="host-input"
                      value={formData.host}
                      onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                      placeholder="localhost"
                      required
                      className="bg-slate-700 border-slate-600"
                    />
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
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cpu">CPU Cores</Label>
                  <Input
                    id="cpu"
                    data-testid="cpu-cores-input"
                    type="number"
                    value={formData.cpu_cores}
                    onChange={(e) => setFormData({ ...formData, cpu_cores: parseInt(e.target.value) })}
                    required
                    className="bg-slate-700 border-slate-600"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="ram">RAM (GB)</Label>
                  <Input
                    id="ram"
                    data-testid="ram-gb-input"
                    type="number"
                    value={formData.ram_gb}
                    onChange={(e) => setFormData({ ...formData, ram_gb: parseInt(e.target.value) })}
                    required
                    className="bg-slate-700 border-slate-600"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="storage">Storage (GB)</Label>
                  <Input
                    id="storage"
                    data-testid="storage-gb-input"
                    type="number"
                    value={formData.storage_gb}
                    onChange={(e) => setFormData({ ...formData, storage_gb: parseInt(e.target.value) })}
                    required
                    className="bg-slate-700 border-slate-600"
                  />
                </div>
                <Button
                  data-testid="submit-node"
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-purple-500 to-violet-600"
                >
                  {loading ? (editingNode ? "Updating..." : "Creating...") : (editingNode ? "Update Node" : "Create Node")}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {nodes.length === 0 ? (
          <Card className="glass border-slate-700">
            <CardContent className="py-16 text-center">
              <Server className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400 mb-4">No nodes configured. Add your first server node!</p>
              <Button
                onClick={() => setShowDialog(true)}
                className="bg-gradient-to-r from-purple-500 to-violet-600"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Node
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {nodes.map((node, index) => {
              const cpuUsage = calculateUsagePercentage(node.used_cpu, node.cpu_cores);
              const ramUsage = calculateUsagePercentage(node.used_ram, node.ram_gb);
              const storageUsage = calculateUsagePercentage(node.used_storage, node.storage_gb);

              return (
                <Card
                  key={node.id}
                  data-testid={`node-card-${node.id}`}
                  className="glass border-slate-700 card-hover animate-fade-in"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-white flex items-center space-x-2">
                          <span>{node.name}</span>
                          <div className={`status-dot ${
                            node.status === 'online' ? 'status-online' : 'status-offline'
                          }`}></div>
                        </CardTitle>
                        <CardDescription className="text-slate-400">
                          {node.host}:{node.port}
                        </CardDescription>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        node.status === 'online' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                      }`}>
                        {node.status}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-slate-400">CPU Usage</span>
                          <span className="text-white font-medium">{node.used_cpu}/{node.cpu_cores} cores</span>
                        </div>
                        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 transition-all"
                            style={{ width: `${cpuUsage}%` }}
                          ></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-slate-400">RAM Usage</span>
                          <span className="text-white font-medium">{node.used_ram}/{node.ram_gb} GB</span>
                        </div>
                        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-purple-500 to-violet-600 transition-all"
                            style={{ width: `${ramUsage}%` }}
                          ></div>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-slate-400">Storage Usage</span>
                          <span className="text-white font-medium">{node.used_storage}/{node.storage_gb} GB</span>
                        </div>
                        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-orange-500 to-red-600 transition-all"
                            style={{ width: `${storageUsage}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 pt-2">
                      <Button
                        data-testid={`edit-node-${node.id}`}
                        size="sm"
                        onClick={() => handleEdit(node)}
                        className="flex-1 bg-slate-700 hover:bg-slate-600"
                      >
                        <Edit className="w-4 h-4 mr-1" />
                        Edit
                      </Button>
                      <Button
                        data-testid={`delete-node-${node.id}`}
                        size="sm"
                        variant="outline"
                        onClick={() => handleDelete(node.id)}
                        className="border-red-600 text-red-400 hover:bg-red-600/10"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </Layout>
  );
};

export default NodesPage;