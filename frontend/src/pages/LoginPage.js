import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API, AuthContext } from "@/App";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { Server, Shield, ShieldCheck } from "lucide-react";

const LoginPage = () => {
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [totpToken, setTotpToken] = useState("");
  const [rememberDevice, setRememberDevice] = useState(false);
  const [requires2FA, setRequires2FA] = useState(false);
  const [tempToken, setTempToken] = useState("");
  const [deviceToken, setDeviceToken] = useState("");
  const [loading, setLoading] = useState(false);
  
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  // Load device token from localStorage
  React.useEffect(() => {
    const savedDeviceToken = localStorage.getItem("device_token");
    if (savedDeviceToken) {
      setDeviceToken(savedDeviceToken);
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email: loginEmail,
        password: loginPassword,
        totp_token: requires2FA ? totpToken : null,
        remember_device: rememberDevice,
        device_token: deviceToken || null,
      });

      // Check if 2FA is required
      if (response.data.requires_2fa) {
        setRequires2FA(true);
        setTempToken(response.data.temp_token);
        toast.info("Please enter your 2FA code");
        setLoading(false);
        return;
      }

      // Save device token if provided
      if (response.data.device_token) {
        localStorage.setItem("device_token", response.data.device_token);
      }

      login(response.data.access_token, response.data.user);
      toast.success("Login successful!");
      navigate("/");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setRequires2FA(false);
    setTotpToken("");
    setTempToken("");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl -top-48 -left-48"></div>
        <div className="absolute w-96 h-96 bg-blue-500/10 rounded-full blur-3xl -bottom-48 -right-48"></div>
      </div>
      
      <Card className="w-full max-w-md glass border-slate-700 animate-fade-in relative z-10" data-testid="login-card">
        <CardHeader className="text-center space-y-2">
          <div className="flex justify-center mb-4">
            <div className="p-4 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl">
              {requires2FA ? (
                <ShieldCheck className="w-10 h-10 text-white" />
              ) : (
                <Server className="w-10 h-10 text-white" />
              )}
            </div>
          </div>
          <CardTitle className="text-3xl font-bold text-white">ServerCraft</CardTitle>
          <CardDescription className="text-slate-400">
            {requires2FA ? "Two-Factor Authentication" : "Game Server Management Panel"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!requires2FA ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="login-email" className="text-slate-200">Email Address</Label>
                <Input
                  id="login-email"
                  data-testid="login-email-input"
                  type="email"
                  placeholder="admin@example.com"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  required
                  className="bg-slate-800 border-slate-600 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="login-password" className="text-slate-200">Password</Label>
                <Input
                  id="login-password"
                  data-testid="login-password-input"
                  type="password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required
                  className="bg-slate-800 border-slate-600 text-white"
                />
              </div>
              <Button
                data-testid="login-submit-button"
                type="submit"
                className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white themed-button"
                disabled={loading}
              >
                {loading ? "Logging in..." : "Login to Panel"}
              </Button>
            </form>
          ) : (
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="totp-token" className="text-slate-200">
                  Authentication Code
                </Label>
                <Input
                  id="totp-token"
                  type="text"
                  placeholder="000000"
                  maxLength={12}
                  value={totpToken}
                  onChange={(e) => setTotpToken(e.target.value)}
                  required
                  autoFocus
                  className="bg-slate-800 border-slate-600 text-white text-center text-2xl tracking-widest"
                />
                <p className="text-xs text-slate-400">
                  Enter the 6-digit code from your authenticator app or a backup code
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="remember-device"
                  checked={rememberDevice}
                  onCheckedChange={setRememberDevice}
                />
                <Label
                  htmlFor="remember-device"
                  className="text-sm text-slate-300 cursor-pointer"
                >
                  Remember this device for 30 days
                </Label>
              </div>

              <div className="flex space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleBack}
                  className="flex-1"
                >
                  Back
                </Button>
                <Button
                  type="submit"
                  className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white"
                  disabled={loading}
                >
                  {loading ? "Verifying..." : "Verify"}
                </Button>
              </div>
            </form>
          )}
          
          <div className="mt-6 pt-6 border-t border-slate-700">
            <div className="flex items-center space-x-2 text-sm text-slate-400">
              <Shield className="w-4 h-4" />
              <span>Admin access only - Secure authentication required</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LoginPage;