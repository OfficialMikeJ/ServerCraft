import React, { useState, useEffect, useContext } from "react";
import axios from "axios";
import { API, AuthContext } from "@/App";
import Layout from "@/components/Layout";
import ThemeSelector from "@/components/ThemeSelector";
import TwoFactorSetup from "@/components/TwoFactorSetup";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Settings as SettingsIcon, DollarSign, Server, Shield } from "lucide-react";

const SettingsPage = () => {
  const [sellingConfig, setSellingConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const { user } = useContext(AuthContext);

  useEffect(() => {
    fetchSellingConfig();
  }, []);

  const fetchSellingConfig = async () => {
    try {
      const response = await axios.get(`${API}/selling/config`);
      setSellingConfig(response.data);
    } catch (error) {
      console.error("Failed to fetch selling config", error);
    }
  };

  const handleUpdateSellingConfig = async () => {
    if (user?.role !== "admin") {
      toast.error("Only admins can update settings");
      return;
    }

    setLoading(true);
    try {
      await axios.put(`${API}/selling/config`, sellingConfig);
      toast.success("Settings updated successfully!");
    } catch (error) {
      toast.error("Failed to update settings");
    } finally {
      setLoading(false);
    }
  };

  const toggleGameType = (gameType) => {
    const currentTypes = sellingConfig.game_types || [];
    const newTypes = currentTypes.includes(gameType)
      ? currentTypes.filter(t => t !== gameType)
      : [...currentTypes, gameType];
    setSellingConfig({ ...sellingConfig, game_types: newTypes });
  };

  const availableGames = [
    { id: "arma3", name: "Arma 3" },
    { id: "rust", name: "Rust" },
    { id: "dayz", name: "DayZ" },
    { id: "icarus", name: "ICARUS" },
    { id: "eft_spt", name: "Escape from Tarkov SPT" },
    { id: "ground_branch", name: "Ground Branch" },
    { id: "ohd", name: "Operation Harsh Doorstop" },
    { id: "squad", name: "Squad" },
    { id: "reforger", name: "Arma Reforger" },
  ];

  return (
    <Layout>
      <div className="space-y-6" data-testid="settings-page">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">Settings</h1>
          <p className="text-slate-400">Configure your server panel</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Theme Selector - Full Width First */}
          <div className="lg:col-span-2">
            <ThemeSelector />
          </div>

          {/* Two-Factor Authentication - Full Width */}
          <div className="lg:col-span-2">
            <TwoFactorSetup />
          </div>

          {/* General Settings */}
          <Card className="glass border-slate-700" data-testid="general-settings-card">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <SettingsIcon className="w-5 h-5" />
                <span>General Settings</span>
              </CardTitle>
              <CardDescription className="text-slate-400">
                Panel configuration and preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 rounded-lg bg-slate-800/50 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Auto-restart on Crash</Label>
                    <p className="text-xs text-slate-400">Automatically restart servers if they crash</p>
                  </div>
                  <Switch defaultChecked={true} />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Email Notifications</Label>
                    <p className="text-xs text-slate-400">Receive alerts for server events</p>
                  </div>
                  <Switch defaultChecked={false} />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Automatic Backups</Label>
                    <p className="text-xs text-slate-400">Daily automated server backups</p>
                  </div>
                  <Switch defaultChecked={true} />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Security Settings */}
          <Card className="glass border-slate-700" data-testid="security-settings-card">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <Shield className="w-5 h-5" />
                <span>Security Settings</span>
              </CardTitle>
              <CardDescription className="text-slate-400">
                Authentication and access control
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 rounded-lg bg-slate-800/50 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Two-Factor Auth</Label>
                    <p className="text-xs text-slate-400">Enhanced login security</p>
                  </div>
                  <Switch defaultChecked={false} />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Session Timeout</Label>
                    <p className="text-xs text-slate-400">Auto-logout after inactivity</p>
                  </div>
                  <Switch defaultChecked={true} />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">IP Whitelist</Label>
                    <p className="text-xs text-slate-400">Restrict access by IP address</p>
                  </div>
                  <Switch defaultChecked={false} />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Server Selling Feature */}
          <Card className="glass border-slate-700 lg:col-span-2" data-testid="selling-config-card">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <DollarSign className="w-5 h-5" />
                <span>Server Selling Configuration</span>
              </CardTitle>
              <CardDescription className="text-slate-400">
                Enable selling servers to friends or your community
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {sellingConfig && (
                <>
                  <div className="flex items-center justify-between p-4 rounded-lg bg-slate-800/50">
                    <div>
                      <Label className="text-white text-base">Enable Server Selling</Label>
                      <p className="text-sm text-slate-400">Allow users to purchase game servers</p>
                    </div>
                    <Switch
                      data-testid="enable-selling-toggle"
                      checked={sellingConfig.enabled}
                      onCheckedChange={(checked) => setSellingConfig({ ...sellingConfig, enabled: checked })}
                    />
                  </div>

                  {sellingConfig.enabled && (
                    <div className="space-y-4">
                      <div>
                        <Label className="text-white mb-3 block">Available Games for Sale</Label>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                          {availableGames.map((game) => (
                            <button
                              key={game.id}
                              data-testid={`game-toggle-${game.id}`}
                              onClick={() => toggleGameType(game.id)}
                              className={`p-3 rounded-lg border-2 transition text-left ${
                                (sellingConfig.game_types || []).includes(game.id)
                                  ? 'border-cyan-500 bg-cyan-500/10 text-cyan-400'
                                  : 'border-slate-600 bg-slate-800/50 text-slate-400 hover:border-slate-500'
                              }`}
                            >
                              <Server className="w-4 h-4 mb-1" />
                              <p className="font-medium text-sm">{game.name}</p>
                            </button>
                          ))}
                        </div>
                      </div>

                      <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
                        <p className="text-blue-400 text-sm">
                          <strong>Note:</strong> Payment integration and pricing configuration will be available in future updates.
                          This feature currently allows you to mark which games are available for sale.
                        </p>
                      </div>

                      <Button
                        data-testid="save-selling-config"
                        onClick={handleUpdateSellingConfig}
                        disabled={loading || user?.role !== "admin"}
                        className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700"
                      >
                        {loading ? "Saving..." : "Save Configuration"}
                      </Button>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>

          {/* Docker Compose Info */}
          <Card className="glass border-slate-700 lg:col-span-2" data-testid="docker-info-card">
            <CardHeader>
              <CardTitle className="text-white">Docker Compose Setup</CardTitle>
              <CardDescription className="text-slate-400">
                Instructions for deploying the panel with Docker Compose
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="p-4 rounded-lg bg-slate-900 font-mono text-sm text-slate-300 overflow-x-auto">
                <pre>
{`version: '3.8'
services:
  servercraft:
    image: servercraft-panel:latest
    ports:
      - "3000:3000"
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://mongo:27017
      - JWT_SECRET_KEY=your-secret-key
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./data:/app/data
    depends_on:
      - mongo

  mongo:
    image: mongo:latest
    volumes:
      - mongo-data:/data/db

volumes:
  mongo-data:`}
                </pre>
              </div>
              <p className="mt-4 text-sm text-slate-400">
                Save this as <code className="px-2 py-1 bg-slate-800 rounded">docker-compose.yml</code> and run:
                <code className="block mt-2 px-2 py-1 bg-slate-800 rounded">docker-compose up -d</code>
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default SettingsPage;