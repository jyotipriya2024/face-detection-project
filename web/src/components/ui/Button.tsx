import { cn } from "@/lib/utils";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
type ButtonSize = "sm" | "md" | "lg";

const variantStyles: Record<ButtonVariant, string> = {
  primary:  "bg-gradient-to-r from-[#00c8ff] to-[#7b61ff] text-white border-transparent shadow-[0_4px_20px_rgba(0,200,255,0.30)] hover:shadow-[0_6px_28px_rgba(0,200,255,0.50)] hover:-translate-y-0.5",
  secondary:"bg-[rgba(0,200,255,0.08)] text-[#00c8ff] border-[rgba(0,200,255,0.30)] hover:bg-[rgba(0,200,255,0.16)] hover:border-[#00c8ff]",
  ghost:    "bg-transparent text-[#6a8fa8] border-transparent hover:bg-white/5 hover:text-[#c0daf0]",
  danger:   "bg-[rgba(255,77,109,0.10)] text-[#ff4d6d] border-[rgba(255,77,109,0.30)] hover:bg-[rgba(255,77,109,0.20)]",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-4 py-2 text-sm",
  lg: "px-6 py-3 text-base",
};

export function Button({
  variant = "secondary", size = "md", className, children, disabled, ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant; size?: ButtonSize;
}) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg border font-semibold tracking-wide",
        "transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed",
        variantStyles[variant], sizeStyles[size], className
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
