import { useState, useEffect } from "react";
import { checkHealth } from "../api";

export default function HealthIndicator() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    const check = async () => {
      try {
        const data = await checkHealth();
        setStatus(data.status === "ok" ? "online" : "degraded");
      } catch {
        setStatus("offline");
      }
    };

    check();
    const interval = setInterval(check, 15000);
    return () => clearInterval(interval);
  }, []);

  const config = {
    checking: { color: "bg-gray-400", label: "Checking..." },
    online: { color: "bg-emerald-500", label: "Backend Online" },
    degraded: { color: "bg-amber-500", label: "Degraded" },
    offline: { color: "bg-red-500", label: "Backend Offline" },
  };

  const { color, label } = config[status];

  return (
    <div className="flex items-center gap-2 text-sm text-gray-600">
      <span className={`w-2 h-2 rounded-full ${color} ${status === "checking" ? "animate-pulse" : ""}`} />
      {label}
    </div>
  );
}