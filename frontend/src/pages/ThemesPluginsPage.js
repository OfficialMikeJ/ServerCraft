import React, { useContext } from "react";
import Layout from "@/components/Layout";
import { AuthContext } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Palette, Puzzle, Lock, AlertTriangle, Download, Shield, ExternalLink, Star } from "lucide-react";

const ThemesPluginsPage = () => {
  const { user } = useContext(AuthContext);

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

  return (
    <Layout>
      <div className="space-y-6" data-testid="themes-plugins-page">
        <div className="text-center py-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 mb-6">
            <Palette className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">Themes & Plugins</h1>
          <p className="text-slate-400">Extend and customize your ServerCraft experience</p>
        </div>

        <Card className="glass border-yellow-600/50 bg-yellow-500/5">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-4">
              <AlertTriangle className="w-6 h-6 text-yellow-400 flex-shrink-0 mt-1" />
              <div className="text-center flex-1">
                <p className="text-yellow-200 text-lg leading-relaxed mb-2">
                  This feature is still in development. Please allow me some time to finish this and test it internally. 
                  Once I have done my testing it will be fully released.
                </p>
                <p className="text-cyan-400 font-semibold text-xl">- Mike</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass border-cyan-600/50 bg-cyan-500/5">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Download className="w-5 h-5 text-cyan-400" />
              <span>How to Install Plugins & Themes</span>
            </CardTitle>
            <CardDescription className="text-slate-400">
              Download and install extensions from the official marketplace
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3 text-slate-300">
              <div className="flex items-start space-x-3 p-3 rounded-lg bg-slate-800/50">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold">
                  1
                </div>
                <div>
                  <p className="font-medium text-white mb-1">Visit ServerCraft Marketplace</p>
                  <p className="text-sm text-slate-400">Browse available plugins and themes on the official website</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3 p-3 rounded-lg bg-slate-800/50">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold">
                  2
                </div>
                <div>
                  <p className="font-medium text-white mb-1">Download Plugin/Theme</p>
                  <p className="text-sm text-slate-400">Free community plugins or premium extensions by Mike</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3 p-3 rounded-lg bg-slate-800/50">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold">
                  3
                </div>
                <div>
                  <p className="font-medium text-white mb-1">Upload to Your Panel</p>
                  <p className="text-sm text-slate-400">Use the upload feature below to install the extension</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3 p-3 rounded-lg bg-slate-800/50">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold">
                  4
                </div>
                <div>
                  <p className="font-medium text-white mb-1">Activate & Configure</p>
                  <p className="text-sm text-slate-400">Enable the plugin and configure settings as needed</p>
                </div>
              </div>
            </div>

            <Button
              disabled
              className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 opacity-50 cursor-not-allowed"
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              Visit ServerCraft Marketplace (Coming Soon)
            </Button>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="glass border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <Palette className="w-5 h-5" />
                <span>Custom Themes</span>
              </CardTitle>
              <CardDescription className="text-slate-400">
                Personalize your panel with custom color schemes and layouts
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-slate-800/50 border border-green-500/20">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">Community Themes</span>
                    <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">FREE</span>
                  </div>
                  <ul className="space-y-1 text-slate-400 text-sm">
                    <li className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-cyan-500"></div>
                      <span>Open source themes</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-cyan-500"></div>
                      <span>Peer-reviewed for safety</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-cyan-500"></div>
                      <span>Community support</span>
                    </li>
                  </ul>
                </div>

                <div className="p-3 rounded-lg bg-slate-800/50 border border-purple-500/20">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">Premium Themes by Mike</span>
                    <span className="text-xs px-2 py-1 rounded-full bg-purple-500/20 text-purple-400">PAID</span>
                  </div>
                  <ul className="space-y-1 text-slate-400 text-sm">
                    <li className="flex items-center space-x-2">
                      <Star className="w-3 h-3 text-yellow-500" />
                      <span>Professional designs</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <Star className="w-3 h-3 text-yellow-500" />
                      <span>Guaranteed security</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <Star className="w-3 h-3 text-yellow-500" />
                      <span>Priority support included</span>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <Puzzle className="w-5 h-5" />
                <span>Plugin System</span>
              </CardTitle>
              <CardDescription className="text-slate-400">
                Extend functionality with custom plugins
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-slate-800/50 border border-green-500/20">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">Community Plugins</span>
                    <span className="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">FREE</span>
                  </div>
                  <ul className="space-y-1 text-slate-400 text-sm">
                    <li className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-purple-500"></div>
                      <span>Open source code</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-purple-500"></div>
                      <span>Community peer-reviewed</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-purple-500"></div>
                      <span>User ratings & feedback</span>
                    </li>
                  </ul>
                </div>

                <div className="p-3 rounded-lg bg-slate-800/50 border border-purple-500/20">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">Premium Plugins by Mike</span>
                    <span className="text-xs px-2 py-1 rounded-full bg-purple-500/20 text-purple-400">PAID</span>
                  </div>
                  <ul className="space-y-1 text-slate-400 text-sm">
                    <li className="flex items-center space-x-2">
                      <Star className="w-3 h-3 text-yellow-500" />
                      <span>One-time purchase fee</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <Star className="w-3 h-3 text-yellow-500" />
                      <span>Security audited & certified</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <Star className="w-3 h-3 text-yellow-500" />
                      <span>Lifetime updates & support</span>
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="glass border-red-600/50 bg-red-500/5">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Lock className="w-5 h-5 text-red-400" />
              <span>Security & Quality Assurance</span>
            </CardTitle>
            <CardDescription className="text-slate-400">
              All plugins and themes are reviewed for safety
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-slate-800/50 text-center">
                <Shield className="w-8 h-8 text-green-400 mx-auto mb-2" />
                <p className="text-white font-medium mb-1">Security Scan</p>
                <p className="text-xs text-slate-400">Automated malware detection</p>
              </div>
              <div className="p-4 rounded-lg bg-slate-800/50 text-center">
                <Star className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
                <p className="text-white font-medium mb-1">User Ratings</p>
                <p className="text-xs text-slate-400">Community feedback system</p>
              </div>
              <div className="p-4 rounded-lg bg-slate-800/50 text-center">
                <Lock className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                <p className="text-white font-medium mb-1">Code Review</p>
                <p className="text-xs text-slate-400">Manual security audit</p>
              </div>
            </div>
            
            <div className="mt-4 p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
              <p className="text-blue-300 text-sm text-center">
                <strong>Admin Only:</strong> Only panel administrators can install plugins and themes to ensure security.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="glass border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Plugin Upload (Coming Soon)</CardTitle>
            <CardDescription className="text-slate-400">
              Upload downloaded plugins from the marketplace
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="border-2 border-dashed border-slate-600 rounded-lg p-12 text-center opacity-50">
              <Download className="w-12 h-12 text-slate-500 mx-auto mb-4" />
              <p className="text-slate-400 mb-2">Drag & drop plugin files here</p>
              <p className="text-slate-500 text-sm">or click to browse (.zip format)</p>
              <Button disabled className="mt-4">
                Browse Files
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default ThemesPluginsPage;
