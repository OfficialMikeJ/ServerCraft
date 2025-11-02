import React from "react";
import Layout from "@/components/Layout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Palette, Puzzle, Lock, AlertTriangle } from "lucide-react";

const ThemesPluginsPage = () => {
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

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 opacity-50">
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
            <CardContent className="space-y-3">
              <p className="text-slate-300 text-sm">Coming soon:</p>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-cyan-500"></div>
                  <span>Custom color schemes</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-cyan-500"></div>
                  <span>Layout customization</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-cyan-500"></div>
                  <span>Community theme marketplace</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-cyan-500"></div>
                  <span>Premium themes by Mike</span>
                </li>
              </ul>
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
            <CardContent className="space-y-3">
              <p className="text-slate-300 text-sm">Coming soon:</p>
              <ul className="space-y-2 text-slate-400 text-sm">
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                  <span>Custom server integrations</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                  <span>Additional game support</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                  <span>Free community plugins</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                  <span>Premium plugins by Mike</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>

        <Card className="glass border-red-600/50 bg-red-500/5">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Lock className="w-5 h-5 text-red-400" />
              <span>Security Guidelines (Preview)</span>
            </CardTitle>
            <CardDescription className="text-slate-400">
              Plugin restrictions to ensure panel security
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <p className="text-green-400 font-semibold">✅ Allowed:</p>
                <ul className="space-y-1 text-slate-300">
                  <li>• Custom UI components</li>
                  <li>• API endpoint extensions</li>
                  <li>• Data visualization</li>
                  <li>• Notifications & alerts</li>
                  <li>• Server monitoring tools</li>
                  <li>• Custom dashboards</li>
                </ul>
              </div>
              <div className="space-y-2">
                <p className="text-red-400 font-semibold">❌ Prohibited:</p>
                <ul className="space-y-1 text-slate-300">
                  <li>• Direct database access</li>
                  <li>• System file manipulation</li>
                  <li>• Arbitrary code execution</li>
                  <li>• Credential harvesting</li>
                  <li>• Network port scanning</li>
                  <li>• Unauthorized API calls</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default ThemesPluginsPage;
