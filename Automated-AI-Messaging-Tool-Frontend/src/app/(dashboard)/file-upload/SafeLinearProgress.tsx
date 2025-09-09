import React from "react";

interface SafeLinearProgressProps {
  value?: number;
  variant?: "determinate" | "indeterminate";
  color?: "primary" | "secondary" | "success" | "error" | "warning" | "info";
  sx?: any;
  fallback?: React.ReactNode;
}

const SafeLinearProgress: React.FC<SafeLinearProgressProps> = ({ 
  value = 0,
  variant = "determinate",
  color = "primary",
  sx = {},
  fallback
}) => {
  const getColor = () => {
    switch (color) {
      case "primary": return "#1976d2";
      case "secondary": return "#9c27b0";
      case "success": return "#2e7d32";
      case "error": return "#d32f2f";
      case "warning": return "#ed6c02";
      case "info": return "#0288d1";
      default: return "#1976d2";
    }
  };

  if (fallback) {
    return <>{fallback}</>;
  }

  return (
    <div style={{
      width: "100%",
      height: "4px",
      backgroundColor: "#e0e0e0",
      borderRadius: "2px",
      overflow: "hidden",
      ...sx
    }}>
      {variant === "determinate" ? (
        <div style={{
          height: "100%",
          backgroundColor: getColor(),
          width: `${Math.min(100, Math.max(0, value))}%`,
          transition: "width 0.3s ease-in-out"
        }} />
      ) : (
        <div style={{
          height: "100%",
          backgroundColor: getColor(),
          width: "100%",
          animation: "indeterminate 1.5s infinite ease-in-out",
          transformOrigin: "0% 50%"
        }} />
      )}
      <style>{`
        @keyframes indeterminate {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </div>
  );
};

export default SafeLinearProgress;
