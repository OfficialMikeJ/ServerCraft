import React, { useState, useContext, useEffect } from "react";
import { AuthContext, API } from "@/App";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Shield, ShieldCheck, ShieldOff, Smartphone, Key, 
  Download, Copy, CheckCircle, AlertTriangle, Info
} from "lucide-react";
import { toast } from "sonner";
import axios from "axios";

const TwoFactorSetup = () => {
  const { user, token } = useContext(AuthContext);
  const [step, setStep] = useState(1);
  const [qrCode, setQrCode] = useState("");
  const [secret, setSecret] = useState("");
  const [backupCodes, setBackupCodes] = useState([]);
  const [verificationToken, setVerificationToken] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [is2FAEnabled, setIs2FAEnabled] = useState(false);
  const [copiedCodes, setCopiedCodes] = useState(false);

  useEffect(() => {
    check2FAStatus();
  }, []);

  const check2FAStatus = async () => {
    try {
      const response = await axios.get(`${API}/auth/2fa/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIs2FAEnabled(response.data.enabled);
    } catch (error) {
      console.error("Failed to check 2FA status:", error);
    }
  };

  const handleSetup2FA = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        `${API}/auth/2fa/setup`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setQrCode(response.data.qr_code);
      setSecret(response.data.secret);
      setBackupCodes(response.data.backup_codes);
      setStep(2);
      toast.success("2FA setup initiated");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to setup 2FA");
    } finally {
      setLoading(false);
    }
  };

  const handleEnable2FA = async () => {
    if (!verificationToken || !password) {
      toast.error("Please provide both password and verification code");
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${API}/auth/2fa/enable`,
        { token: verificationToken, password },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success("2FA enabled successfully!");
      setIs2FAEnabled(true);
      setStep(4);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to enable 2FA");
    } finally {
      setLoading(false);
    }
  };

  const handleDisable2FA = async () => {
    if (!verificationToken || !password) {
      toast.error("Please provide both password and verification code");
      return;
    }

    if (!confirm("Are you sure you want to disable 2FA? This will make your account less secure.")) {
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${API}/auth/2fa/disable`,
        { token: verificationToken, password },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success("2FA disabled successfully");
      setIs2FAEnabled(false);
      setStep(1);
      setVerificationToken("");
      setPassword("");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to disable 2FA");
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateBackupCodes = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/auth/2fa/backup-codes`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setBackupCodes(response.data.backup_codes);
      toast.success("Backup codes regenerated");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to regenerate backup codes");
    } finally {
      setLoading(false);
    }
  };

  const copyBackupCodes = () => {
    const codesText = backupCodes.join("\n");
    navigator.clipboard.writeText(codesText);
    setCopiedCodes(true);
    toast.success("Backup codes copied to clipboard");
    setTimeout(() => setCopiedCodes(false), 3000);
  };

  const downloadBackupCodes = () => {
    const codesText = `ServerCraft 2FA Backup Codes\nGenerated: ${new Date().toLocaleString()}\n\n${backupCodes.join("\n")}\n\nKeep these codes safe and secure!`;
    const blob = new Blob([codesText], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `servercraft-backup-codes-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Backup codes downloaded");
  };

  // Step 1: Initial state
  if (step === 1 && !is2FAEnabled) {
    return (
      <Card className="glass border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <Shield className="w-6 h-6 text-cyan-400" />
            <span>Two-Factor Authentication</span>
          </CardTitle>
          <CardDescription className="text-slate-400">
            Add an extra layer of security to your account
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="p-4 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
            <div className="flex items-start space-x-3">
              <Info className="w-5 h-5 text-cyan-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-cyan-300 font-medium mb-2">Why enable 2FA?</p>
                <ul className="text-sm text-slate-300 space-y-1">
                  <li>• Protects your account even if password is compromised</li>
                  <li>• Requires both password AND phone for login</li>
                  <li>• Industry-standard security (TOTP)</li>
                  <li>• Works with Google Authenticator, Authy, Microsoft Authenticator</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center space-x-3 p-3 rounded-lg bg-slate-800/50">
              <Smartphone className="w-5 h-5 text-green-400" />
              <span className="text-slate-300">Compatible with all TOTP apps</span>
            </div>
            <div className="flex items-center space-x-3 p-3 rounded-lg bg-slate-800/50">
              <Key className="w-5 h-5 text-purple-400" />
              <span className="text-slate-300">10 backup codes for emergencies</span>
            </div>
            <div className="flex items-center space-x-3 p-3 rounded-lg bg-slate-800/50">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
              <span className="text-slate-300">Optional "Remember this device"</span>
            </div>
          </div>

          <Button
            onClick={handleSetup2FA}
            disabled={loading}
            className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700"
          >
            {loading ? "Setting up..." : "Enable Two-Factor Authentication"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Step 2: QR Code Display
  if (step === 2) {
    return (
      <Card className="glass border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Step 1: Scan QR Code</CardTitle>
          <CardDescription className="text-slate-400">
            Use your authenticator app to scan this QR code
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex justify-center p-6 bg-white rounded-lg">
            <img src={qrCode} alt="2FA QR Code" className="w-64 h-64" />
          </div>

          <div className="p-4 rounded-lg bg-slate-800/50">
            <Label className="text-slate-300 text-sm mb-2">Manual Entry Code</Label>
            <div className="flex items-center space-x-2 mt-2">
              <code className="flex-1 px-3 py-2 bg-slate-900 text-cyan-400 rounded font-mono text-sm">
                {secret}
              </code>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  navigator.clipboard.writeText(secret);
                  toast.success("Secret copied");
                }}
              >
                <Copy className="w-4 h-4" />
              </Button>
            </div>
          </div>

          <Button
            onClick={() => setStep(3)}
            className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700"
          >
            Continue to Verification
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Step 3: Verification
  if (step === 3) {
    return (
      <Card className="glass border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Step 2: Verify & Enable</CardTitle>
          <CardDescription className="text-slate-400">
            Enter the 6-digit code from your authenticator app
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="verification-code" className="text-slate-200">
              Verification Code
            </Label>
            <Input
              id="verification-code"
              type="text"
              placeholder="000000"
              maxLength={6}
              value={verificationToken}
              onChange={(e) => setVerificationToken(e.target.value.replace(/\D/g, ""))}
              className="bg-slate-800 border-slate-600 text-white text-center text-2xl tracking-widest"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password-confirm" className="text-slate-200">
              Confirm Your Password
            </Label>
            <Input
              id="password-confirm"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-slate-800 border-slate-600 text-white"
            />
          </div>

          <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
            <p className="text-yellow-300 text-sm">
              <AlertTriangle className="w-4 h-4 inline mr-2" />
              Make sure to save your backup codes in the next step!
            </p>
          </div>

          <div className="flex space-x-3">
            <Button
              variant="outline"
              onClick={() => setStep(2)}
              className="flex-1"
            >
              Back
            </Button>
            <Button
              onClick={handleEnable2FA}
              disabled={loading || verificationToken.length !== 6}
              className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700"
            >
              {loading ? "Verifying..." : "Enable 2FA"}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Step 4: Backup Codes
  if (step === 4 || (is2FAEnabled && backupCodes.length > 0)) {
    return (
      <Card className="glass border-green-600/50 bg-green-500/5">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <CheckCircle className="w-6 h-6 text-green-400" />
            <span>2FA Enabled Successfully!</span>
          </CardTitle>
          <CardDescription className="text-slate-400">
            Save these backup codes in a secure location
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
            <p className="text-red-300 text-sm font-medium mb-2">
              <AlertTriangle className="w-4 h-4 inline mr-2" />
              Important: Save these codes now!
            </p>
            <p className="text-slate-400 text-sm">
              These codes can be used to access your account if you lose your authenticator device. 
              Each code can only be used once.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
            <div className="grid grid-cols-2 gap-2">
              {backupCodes.map((code, index) => (
                <div
                  key={index}
                  className="px-3 py-2 bg-slate-900 rounded font-mono text-sm text-cyan-400 text-center"
                >
                  {code}
                </div>
              ))}
            </div>
          </div>

          <div className="flex space-x-3">
            <Button
              onClick={copyBackupCodes}
              variant="outline"
              className="flex-1"
            >
              {copiedCodes ? (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4 mr-2" />
                  Copy Codes
                </>
              )}
            </Button>
            <Button
              onClick={downloadBackupCodes}
              className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700"
            >
              <Download className="w-4 h-4 mr-2" />
              Download Codes
            </Button>
          </div>

          <Button
            onClick={() => {
              setStep(1);
              setBackupCodes([]);
            }}
            variant="outline"
            className="w-full"
          >
            Done
          </Button>
        </CardContent>
      </Card>
    );
  }

  // 2FA Already Enabled - Management
  if (is2FAEnabled) {
    return (
      <Card className="glass border-green-600/50 bg-green-500/5">
        <CardHeader>
          <CardTitle className="text-white flex items-center space-x-2">
            <ShieldCheck className="w-6 h-6 text-green-400" />
            <span>Two-Factor Authentication Active</span>
          </CardTitle>
          <CardDescription className="text-slate-400">
            Your account is protected with 2FA
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/30">
            <div className="flex items-center space-x-3">
              <ShieldCheck className="w-6 h-6 text-green-400" />
              <div>
                <p className="text-green-300 font-medium">Account Protected</p>
                <p className="text-slate-400 text-sm">2FA is active on your account</p>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <Button
              onClick={handleRegenerateBackupCodes}
              disabled={loading}
              variant="outline"
              className="w-full"
            >
              <Key className="w-4 h-4 mr-2" />
              Regenerate Backup Codes
            </Button>

            <div className="pt-4 border-t border-slate-700">
              <p className="text-slate-400 text-sm mb-4">
                To disable 2FA, enter your password and a verification code:
              </p>
              <div className="space-y-3">
                <Input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-slate-800 border-slate-600 text-white"
                />
                <Input
                  type="text"
                  placeholder="6-digit code"
                  maxLength={6}
                  value={verificationToken}
                  onChange={(e) => setVerificationToken(e.target.value.replace(/\D/g, ""))}
                  className="bg-slate-800 border-slate-600 text-white"
                />
                <Button
                  onClick={handleDisable2FA}
                  disabled={loading || !password || verificationToken.length !== 6}
                  variant="destructive"
                  className="w-full bg-red-600 hover:bg-red-700"
                >
                  <ShieldOff className="w-4 h-4 mr-2" />
                  Disable 2FA
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return null;
};

export default TwoFactorSetup;
