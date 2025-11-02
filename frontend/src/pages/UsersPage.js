import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "@/App";
import Layout from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";
import { Plus, Users as UsersIcon, Shield, Edit } from "lucide-react";

const UsersPage = () => {
  const [users, setUsers] = useState([]);
  const [showDialog, setShowDialog] = useState(false);
  const [showPermissionsDialog, setShowPermissionsDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const { user: currentUser } = useContext(AuthContext);

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    role: "subuser",
  });

  const [permissions, setPermissions] = useState({
    can_start_servers: false,
    can_stop_servers: false,
    can_restart_servers: false,
    can_upload_files: false,
    can_delete_files: false,
    can_view_console: true,
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (error) {
      toast.error("Failed to fetch users");
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/auth/register`, {
        ...formData,
        permissions: permissions,
      });
      toast.success("User created successfully!");
      setShowDialog(false);
      fetchUsers();
      setFormData({
        username: "",
        email: "",
        password: "",
        role: "subuser",
      });
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create user");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePermissions = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/users/${selectedUser.id}/permissions`, permissions);
      toast.success("Permissions updated successfully!");
      setShowPermissionsDialog(false);
      fetchUsers();
    } catch (error) {
      toast.error("Failed to update permissions");
    } finally {
      setLoading(false);
    }
  };

  const openPermissionsDialog = (user) => {
    setSelectedUser(user);
    setPermissions(user.permissions || {
      can_start_servers: false,
      can_stop_servers: false,
      can_restart_servers: false,
      can_upload_files: false,
      can_delete_files: false,
      can_view_console: true,
    });
    setShowPermissionsDialog(true);
  };

  if (currentUser?.role !== "admin") {
    return (
      <Layout>
        <div className="text-center py-16">
          <Shield className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Access Denied</h2>
          <p className="text-slate-400">Only administrators can manage users.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6" data-testid="users-page">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">User Management</h1>
            <p className="text-slate-400">Manage users and their permissions</p>
          </div>
          <Dialog open={showDialog} onOpenChange={setShowDialog}>
            <DialogTrigger asChild>
              <Button
                data-testid="create-user-button"
                className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add User
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-slate-800 border-slate-700 text-white" data-testid="create-user-dialog">
              <DialogHeader>
                <DialogTitle>Create New User</DialogTitle>
                <DialogDescription className="text-slate-400">
                  Add a new sub-user with custom permissions
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreateUser} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <Input
                    id="username"
                    data-testid="username-input"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    required
                    className="bg-slate-700 border-slate-600"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    data-testid="email-input"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                    className="bg-slate-700 border-slate-600"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    data-testid="password-input"
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                    className="bg-slate-700 border-slate-600"
                  />
                </div>
                <div className="space-y-3 pt-2">
                  <Label>Permissions</Label>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-2 rounded bg-slate-700/50">
                      <Label htmlFor="perm-start" className="text-sm">Can Start Servers</Label>
                      <Switch
                        id="perm-start"
                        checked={permissions.can_start_servers}
                        onCheckedChange={(checked) => setPermissions({ ...permissions, can_start_servers: checked })}
                      />
                    </div>
                    <div className="flex items-center justify-between p-2 rounded bg-slate-700/50">
                      <Label htmlFor="perm-stop" className="text-sm">Can Stop Servers</Label>
                      <Switch
                        id="perm-stop"
                        checked={permissions.can_stop_servers}
                        onCheckedChange={(checked) => setPermissions({ ...permissions, can_stop_servers: checked })}
                      />
                    </div>
                    <div className="flex items-center justify-between p-2 rounded bg-slate-700/50">
                      <Label htmlFor="perm-restart" className="text-sm">Can Restart Servers</Label>
                      <Switch
                        id="perm-restart"
                        checked={permissions.can_restart_servers}
                        onCheckedChange={(checked) => setPermissions({ ...permissions, can_restart_servers: checked })}
                      />
                    </div>
                    <div className="flex items-center justify-between p-2 rounded bg-slate-700/50">
                      <Label htmlFor="perm-upload" className="text-sm">Can Upload Files</Label>
                      <Switch
                        id="perm-upload"
                        checked={permissions.can_upload_files}
                        onCheckedChange={(checked) => setPermissions({ ...permissions, can_upload_files: checked })}
                      />
                    </div>
                  </div>
                </div>
                <Button
                  data-testid="submit-create-user"
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-orange-500 to-red-600"
                >
                  {loading ? "Creating..." : "Create User"}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {users.map((user, index) => (
            <Card
              key={user.id}
              data-testid={`user-card-${user.id}`}
              className="glass border-slate-700 card-hover animate-fade-in"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-white flex items-center space-x-2">
                      <UsersIcon className="w-5 h-5" />
                      <span>{user.username}</span>
                    </CardTitle>
                    <CardDescription className="text-slate-400">{user.email}</CardDescription>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    user.role === 'admin' ? 'bg-purple-500/20 text-purple-400' : 'bg-blue-500/20 text-blue-400'
                  }`}>
                    {user.role}
                  </span>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-2">
                  <p className="text-sm text-slate-400 font-medium">Permissions:</p>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {Object.entries(user.permissions || {}).map(([key, value]) => (
                      <div
                        key={key}
                        className={`px-2 py-1 rounded ${
                          value ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                        }`}
                      >
                        {key.replace('can_', '').replace(/_/g, ' ')}
                      </div>
                    ))}
                  </div>
                </div>

                {user.role === 'subuser' && (
                  <Button
                    data-testid={`edit-permissions-${user.id}`}
                    size="sm"
                    onClick={() => openPermissionsDialog(user)}
                    className="w-full bg-slate-700 hover:bg-slate-600"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Edit Permissions
                  </Button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>

        <Dialog open={showPermissionsDialog} onOpenChange={setShowPermissionsDialog}>
          <DialogContent className="bg-slate-800 border-slate-700 text-white" data-testid="permissions-dialog">
            <DialogHeader>
              <DialogTitle>Edit Permissions - {selectedUser?.username}</DialogTitle>
              <DialogDescription className="text-slate-400">
                Configure what this user can do
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-2">
              <div className="flex items-center justify-between p-3 rounded bg-slate-700/50">
                <Label htmlFor="edit-start" className="text-sm">Can Start Servers</Label>
                <Switch
                  id="edit-start"
                  checked={permissions.can_start_servers}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, can_start_servers: checked })}
                />
              </div>
              <div className="flex items-center justify-between p-3 rounded bg-slate-700/50">
                <Label htmlFor="edit-stop" className="text-sm">Can Stop Servers</Label>
                <Switch
                  id="edit-stop"
                  checked={permissions.can_stop_servers}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, can_stop_servers: checked })}
                />
              </div>
              <div className="flex items-center justify-between p-3 rounded bg-slate-700/50">
                <Label htmlFor="edit-restart" className="text-sm">Can Restart Servers</Label>
                <Switch
                  id="edit-restart"
                  checked={permissions.can_restart_servers}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, can_restart_servers: checked })}
                />
              </div>
              <div className="flex items-center justify-between p-3 rounded bg-slate-700/50">
                <Label htmlFor="edit-upload" className="text-sm">Can Upload Files</Label>
                <Switch
                  id="edit-upload"
                  checked={permissions.can_upload_files}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, can_upload_files: checked })}
                />
              </div>
              <div className="flex items-center justify-between p-3 rounded bg-slate-700/50">
                <Label htmlFor="edit-delete" className="text-sm">Can Delete Files</Label>
                <Switch
                  id="edit-delete"
                  checked={permissions.can_delete_files}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, can_delete_files: checked })}
                />
              </div>
              <div className="flex items-center justify-between p-3 rounded bg-slate-700/50">
                <Label htmlFor="edit-console" className="text-sm">Can View Console</Label>
                <Switch
                  id="edit-console"
                  checked={permissions.can_view_console}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, can_view_console: checked })}
                />
              </div>
            </div>
            <Button
              data-testid="save-permissions"
              onClick={handleUpdatePermissions}
              disabled={loading}
              className="w-full bg-gradient-to-r from-orange-500 to-red-600 mt-4"
            >
              {loading ? "Saving..." : "Save Permissions"}
            </Button>
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
};

export default UsersPage;