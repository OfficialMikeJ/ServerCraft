import React, { useState, useEffect, useContext, useRef } from "react";
import Layout from "@/components/Layout";
import { AuthContext, API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Palette, Puzzle, Lock, AlertTriangle, Download, Shield, 
  ExternalLink, Star, Upload, Trash2, Power, PowerOff, 
  Package, CheckCircle, XCircle, Info 
} from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const ThemesPluginsPage = () => {
  const { user, token } = useContext(AuthContext);
  const [plugins, setPlugins] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  // Admin-only check
  if (user?.role !== "admin") {
    return (
      <Layout>
        <div className="text-center py-16">
          <Shield className="w-16 h-16 text-slate-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Admin Access Required</h2>
          <p className="text-slate-400">Only administrators can access Themes & Plugins.</p>
        </div>
      </Layout>
    );
  }

  const fetchPlugins = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/plugins`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPlugins(response.data);
    } catch (error) {
      toast.error("Failed to load plugins");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlugins();
  }, []);

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.zip')) {
      toast.error("Only .zip files are allowed");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error("File size exceeds 10MB limit");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/plugins/upload`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      toast.success(response.data.message);
      fetchPlugins();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to upload plugin");
      console.error(error);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const togglePlugin = async (pluginId, currentStatus) => {
    const action = currentStatus ? 'disable' : 'enable';
    try {
      await axios.put(`${API}/plugins/${pluginId}/${action}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success(`Plugin ${action}d successfully`);
      fetchPlugins();
    } catch (error) {
      toast.error(`Failed to ${action} plugin`);
      console.error(error);
    }
  };

  const deletePlugin = async (pluginId) => {
    if (!confirm('Are you sure you want to delete this plugin?')) return;

    try {
      await axios.delete(`${API}/plugins/${pluginId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success("Plugin deleted successfully");
      fetchPlugins();
    } catch (error) {
      toast.error("Failed to delete plugin");
      console.error(error);
    }
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="themes-plugins-page">
        <div className="text-center py-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 mb-6">
            <Puzzle className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">Plugins & Extensions</h1>
          <p className="text-slate-400">Extend and customize your ServerCraft experience</p>
        </div>

        {/* Upload Section */}
        <Card className="glass border-cyan-600/50 bg-cyan-500/5">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Upload className="w-5 h-5 text-cyan-400" />
              <span>Upload Plugin</span>
            </CardTitle>
            <CardDescription className="text-slate-400">
              Upload a .zip plugin file (max 10MB)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <input
              ref={fileInputRef}
              type="file"
              accept=".zip"
              onChange={handleFileUpload}
              className="hidden"
            />
            <div 
              onClick={handleFileSelect}
              className="border-2 border-dashed border-cyan-600/50 rounded-lg p-12 text-center cursor-pointer hover:border-cyan-500 hover:bg-cyan-500/5 transition-colors"
            >
              {uploading ? (
                <div className="space-y-3">
                  <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                  <p className="text-slate-300">Uploading plugin...</p>
                </div>
              ) : (
                <>
                  <Download className="w-12 h-12 text-cyan-400 mx-auto mb-4" />
                  <p className="text-slate-300 mb-2 font-medium">Drag & drop plugin file here</p>
                  <p className="text-slate-500 text-sm mb-4">or click to browse (.zip format, max 10MB)</p>
                  <Button className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700">
                    <Upload className="w-4 h-4 mr-2" />
                    Select File
                  </Button>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Installed Plugins */}
        <Card className="glass border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Package className="w-5 h-5" />
                <span>Installed Plugins</span>
              </div>
              <span className="text-sm font-normal text-slate-400">
                {plugins.length} plugin{plugins.length !== 1 ? 's' : ''}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-12">
                <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-slate-400">Loading plugins...</p>
              </div>
            ) : plugins.length === 0 ? (
              <div className="text-center py-12">
                <Package className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400 mb-2">No plugins installed</p>
                <p className="text-slate-500 text-sm">Upload a plugin to get started</p>
              </div>
            ) : (
              <div className="space-y-4">
                {plugins.map((plugin) => (
                  <div
                    key={plugin.id}
                    className="p-4 rounded-lg bg-slate-800/50 border border-slate-700 hover:border-slate-600 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-white font-semibold text-lg">{plugin.name}</h3>
                          <span className="text-xs px-2 py-1 rounded-full bg-slate-700 text-slate-300">
                            v{plugin.version}
                          </span>
                          {plugin.enabled ? (
                            <span className="flex items-center space-x-1 text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">
                              <CheckCircle className="w-3 h-3" />
                              <span>Enabled</span>
                            </span>
                          ) : (
                            <span className="flex items-center space-x-1 text-xs px-2 py-1 rounded-full bg-slate-700 text-slate-400">
                              <XCircle className="w-3 h-3" />
                              <span>Disabled</span>
                            </span>
                          )}
                        </div>
                        <p className="text-slate-400 text-sm mb-2">{plugin.description}</p>
                        {plugin.author && (
                          <p className="text-slate-500 text-xs">by {plugin.author}</p>
                        )}
                        {plugin.manifest?.ui?.enabled && (
                          <div className="mt-2 flex items-center space-x-2 text-xs text-cyan-400">
                            <Info className="w-3 h-3" />
                            <span>Adds "{plugin.manifest.ui.tab_name}" tab</span>
                          </div>
                        )}
                      </div>
                      <div className="flex items-center space-x-2 ml-4">
                        <Button
                          size="sm"
                          variant={plugin.enabled ? "destructive" : "default"}
                          onClick={() => togglePlugin(plugin.id, plugin.enabled)}
                          className={plugin.enabled ? 
                            "bg-red-600 hover:bg-red-700" : 
                            "bg-green-600 hover:bg-green-700"
                          }
                        >
                          {plugin.enabled ? (
                            <>
                              <PowerOff className="w-4 h-4 mr-1" />
                              Disable
                            </>
                          ) : (
                            <>
                              <Power className="w-4 h-4 mr-1" />
                              Enable
                            </>
                          )}
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => deletePlugin(plugin.id)}
                          className="bg-red-600 hover:bg-red-700"
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

        {/* Plugin Template Info */}
        <Card className="glass border-purple-600/50 bg-purple-500/5">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Palette className="w-5 h-5 text-purple-400" />
              <span>Create Your Own Plugin</span>
            </CardTitle>
            <CardDescription className="text-slate-400">
              Use our plugin template to build custom extensions
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 rounded-lg bg-slate-800/50">
              <p className="text-slate-300 mb-3">
                Two example plugins are included in your ServerCraft installation:
              </p>
              <div className="space-y-2 text-sm">
                <div className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-cyan-500 mt-2"></div>
                  <div>
                    <p className="text-white font-medium">Server Billing Plugin</p>
                    <p className="text-slate-400">Add billing and subscription management</p>
                  </div>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-2"></div>
                  <div>
                    <p className="text-white font-medium">Enhanced Sub-User Management</p>
                    <p className="text-slate-400">Advanced permissions and access control</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
              <p className="text-cyan-300 text-sm">
                <strong>Developer Docs:</strong> Check <code className="px-1.5 py-0.5 rounded bg-slate-800 text-cyan-400">/plugins/PLUGIN_TEMPLATE/README.md</code> for plugin development guide
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Security Notice */}
        <Card className="glass border-red-600/50 bg-red-500/5">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Lock className="w-5 h-5 text-red-400" />
              <span>Security Guidelines</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <div className="flex items-start space-x-3">
                <Shield className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-white font-medium mb-1">Only Upload Trusted Plugins</p>
                  <p className="text-slate-400">Plugins have access to your panel's API. Only install from trusted sources.</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <AlertTriangle className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-white font-medium mb-1">Review Plugin Code</p>
                  <p className="text-slate-400">Examine plugin files before enabling to ensure they're safe.</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <Lock className="w-5 h-5 text-purple-400 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-white font-medium mb-1">Admin Only Access</p>
                  <p className="text-slate-400">Only administrators can manage plugins for security reasons.</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default ThemesPluginsPage;
