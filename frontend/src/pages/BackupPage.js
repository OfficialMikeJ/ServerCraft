import React, { useState, useEffect, useContext } from "react";
import Layout from "@/components/Layout";
import { AuthContext, API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Database, HardDrive, Download, Upload, Trash2, Shield, 
  Clock, CheckCircle, AlertTriangle, RefreshCw, Settings as SettingsIcon,
  Archive, Save, RotateCcw
} from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const BackupPage = () => {
  const { user, token } = useContext(AuthContext);
  const [backups, setBackups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [backupPassword, setBackupPassword] = useState("");
  const [backupDescription, setBackupDescription] = useState("");
  const [restorePassword, setRestorePassword] = useState("");
  const [selectedBackup, setSelectedBackup] = useState(null);
  const [config, setConfig] = useState({
    schedule: "daily",
    retention_count: 10,
    auto_backup_enabled: false
  });

  useEffect(() => {
    fetchBackups();
    fetchConfig();
  }, []);

  const fetchBackups = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/backups`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setBackups(response.data);
    } catch (error) {
      toast.error("Failed to load backups");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const fetchConfig = async () => {
    try {
      const response = await axios.get(`${API}/backups/config`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConfig(response.data);
    } catch (error) {
      console.error("Failed to load backup config:", error);
    }
  };

  const handleCreateBackup = async () => {
    if (!backupPassword) {
      toast.error("Please enter an encryption password");
      return;
    }

    setCreating(true);
    try {
      const response = await axios.post(
        `${API}/backups/create`,
        {
          description: backupDescription || "Manual backup",
          password: backupPassword,
          include_database: true,
          include_files: true,
          file_dirs: []
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success("Backup created successfully!");
      setBackupPassword("");
      setBackupDescription("");
      fetchBackups();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create backup");
    } finally {
      setCreating(false);
    }
  };

  const handleRestoreBackup = async (backupId) => {
    if (!restorePassword) {
      toast.error("Please enter the backup password");
      return;
    }

    if (!confirm("Are you sure you want to restore this backup? This will overwrite current data.")) {
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${API}/backups/${backupId}/restore`,
        {
          password: restorePassword,
          restore_database: true,
          restore_files: true
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success("Backup restored successfully! Please reload the page.");
      setRestorePassword("");
      setSelectedBackup(null);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to restore backup");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteBackup = async (backupId) => {
    if (!confirm("Are you sure you want to delete this backup? This action cannot be undone.")) {
      return;
    }

    try {
      await axios.delete(`${API}/backups/${backupId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      toast.success("Backup deleted successfully");
      fetchBackups();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to delete backup");
    }
  };

  const handleVerifyBackup = async (backupId) => {
    try {
      const response = await axios.post(
        `${API}/backups/${backupId}/verify`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.valid) {
        toast.success("Backup verification passed");
      } else {
        toast.error(`Backup verification failed: ${response.data.message}`);
      }
    } catch (error) {
      toast.error("Failed to verify backup");
    }
  };

  const handleUpdateConfig = async () => {
    try {
      await axios.post(
        `${API}/backups/config`,
        config,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success("Backup configuration updated");
    } catch (error) {
      toast.error("Failed to update configuration");
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (isoString) => {
    return new Date(isoString).toLocaleString();
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">Backup & Recovery</h1>
          <p className="text-slate-400">Protect your data with automated backups</p>
        </div>

        {/* Create Backup Section */}
        <Card className="glass border-cyan-600/50 bg-cyan-500/5">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Save className="w-5 h-5 text-cyan-400" />
              <span>Create Manual Backup</span>
            </CardTitle>
            <CardDescription className="text-slate-400">
              Create an encrypted backup of your database and files
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="backup-description" className="text-slate-200">
                Description (Optional)
              </Label>
              <Input
                id="backup-description"
                type="text"
                placeholder="e.g., Before major update"
                value={backupDescription}
                onChange={(e) => setBackupDescription(e.target.value)}
                className="bg-slate-800 border-slate-600 text-white"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="backup-password" className="text-slate-200">
                Encryption Password *
              </Label>
              <Input
                id="backup-password"
                type="password"
                placeholder="Enter a strong password"
                value={backupPassword}
                onChange={(e) => setBackupPassword(e.target.value)}
                className="bg-slate-800 border-slate-600 text-white"
              />
              <p className="text-xs text-slate-400">
                <Shield className="w-3 h-3 inline mr-1" />
                Save this password securely! You'll need it to restore the backup.
              </p>
            </div>

            <Button
              onClick={handleCreateBackup}
              disabled={creating || !backupPassword}
              className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700"
            >
              {creating ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Creating Backup...
                </>
              ) : (
                <>
                  <Database className="w-4 h-4 mr-2" />
                  Create Backup Now
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Backup Configuration */}
        <Card className="glass border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <SettingsIcon className="w-5 h-5" />
              <span>Backup Configuration</span>
            </CardTitle>
            <CardDescription className="text-slate-400">
              Configure automatic backup settings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-200">Backup Schedule</Label>
                <select
                  value={config.schedule}
                  onChange={(e) => setConfig({...config, schedule: e.target.value})}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-600 rounded-md text-white"
                >
                  <option value="disabled">Disabled</option>
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label className="text-slate-200">Keep Last N Backups</Label>
                <Input
                  type="number"
                  min="1"
                  max="100"
                  value={config.retention_count}
                  onChange={(e) => setConfig({...config, retention_count: parseInt(e.target.value)})}
                  className="bg-slate-800 border-slate-600 text-white"
                />
              </div>
            </div>

            <Button
              onClick={handleUpdateConfig}
              variant="outline"
              className="w-full"
            >
              <Save className="w-4 h-4 mr-2" />
              Save Configuration
            </Button>
          </CardContent>
        </Card>

        {/* Available Backups */}
        <Card className="glass border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Archive className="w-5 h-5" />
                <span>Available Backups</span>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={fetchBackups}
                disabled={loading}
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </Button>
            </CardTitle>
            <CardDescription className="text-slate-400">
              {backups.length} backup{backups.length !== 1 ? 's' : ''} available
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-12">
                <RefreshCw className="w-12 h-12 text-cyan-400 animate-spin mx-auto mb-4" />
                <p className="text-slate-400">Loading backups...</p>
              </div>
            ) : backups.length === 0 ? (
              <div className="text-center py-12">
                <Database className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400 mb-2">No backups available</p>
                <p className="text-slate-500 text-sm">Create your first backup above</p>
              </div>
            ) : (
              <div className="space-y-3">
                {backups.map((backup) => (
                  <div
                    key={backup.id}
                    className="p-4 rounded-lg bg-slate-800/50 border border-slate-700 hover:border-slate-600 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-white font-semibold">{backup.description || backup.id}</h3>
                          <span className="text-xs px-2 py-1 rounded-full bg-slate-700 text-slate-300">
                            {formatBytes(backup.file_size)}
                          </span>
                          {backup.database_included && (
                            <span className="flex items-center space-x-1 text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">
                              <Database className="w-3 h-3" />
                              <span>DB</span>
                            </span>
                          )}
                          {backup.files_included && (
                            <span className="flex items-center space-x-1 text-xs px-2 py-1 rounded-full bg-blue-500/20 text-blue-400">
                              <HardDrive className="w-3 h-3" />
                              <span>Files</span>
                            </span>
                          )}
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-slate-400">
                          <div className="flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>{formatDate(backup.timestamp)}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2 ml-4">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleVerifyBackup(backup.id)}
                          title="Verify backup"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => setSelectedBackup(backup)}
                          className="bg-green-600 hover:bg-green-700"
                          title="Restore backup"
                        >
                          <RotateCcw className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDeleteBackup(backup.id)}
                          className="bg-red-600 hover:bg-red-700"
                          title="Delete backup"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Restore Modal */}
        {selectedBackup && (
          <Card className="glass border-yellow-600/50 bg-yellow-500/5">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-yellow-400" />
                <span>Restore Backup</span>
              </CardTitle>
              <CardDescription className="text-slate-400">
                Restoring: {selectedBackup.description || selectedBackup.id}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
                <p className="text-red-300 text-sm">
                  <AlertTriangle className="w-4 h-4 inline mr-2" />
                  <strong>Warning:</strong> This will overwrite your current database and files. Make sure you have a recent backup before proceeding.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="restore-password" className="text-slate-200">
                  Backup Password
                </Label>
                <Input
                  id="restore-password"
                  type="password"
                  placeholder="Enter the encryption password"
                  value={restorePassword}
                  onChange={(e) => setRestorePassword(e.target.value)}
                  className="bg-slate-800 border-slate-600 text-white"
                  autoFocus
                />
              </div>

              <div className="flex space-x-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    setSelectedBackup(null);
                    setRestorePassword("");
                  }}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={() => handleRestoreBackup(selectedBackup.id)}
                  disabled={!restorePassword || loading}
                  className="flex-1 bg-yellow-600 hover:bg-yellow-700"
                >
                  {loading ? "Restoring..." : "Restore Backup"}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </Layout>
  );
};

export default BackupPage;
