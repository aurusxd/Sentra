import { ArrowRight } from "lucide-react";
import type { AnchorHTMLAttributes, ButtonHTMLAttributes, ReactNode } from "react";

type BaseProps = {
  children: ReactNode;
  variant?: "primary" | "secondary";
  className?: string;
  showArrow?: boolean;
};

type ButtonAsLink = BaseProps & AnchorHTMLAttributes<HTMLAnchorElement> & { href: string };
type ButtonNative = BaseProps & ButtonHTMLAttributes<HTMLButtonElement> & { href?: never };

export function Button(props: ButtonAsLink | ButtonNative) {
  const { children, variant = "primary", className = "", showArrow = true } = props;
  const classes = [
    "focus-ring inline-flex min-h-11 items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-semibold transition",
    variant === "primary"
      ? "bg-primary text-bg shadow-glow hover:bg-accent hover:text-text"
      : "border border-line bg-panel/70 text-text hover:border-primary/60",
    className
  ].join(" ");

  if (props.href) {
    const { href, children: _children, variant: _variant, className: _className, showArrow: _showArrow, ...rest } = props;
    return (
      <a className={classes} href={href} {...rest}>
        {children}
        {showArrow && <ArrowRight aria-hidden="true" size={17} />}
      </a>
    );
  }

  const nativeProps = props as ButtonNative;
  const { children: _children, variant: _variant, className: _className,showArrow: _showArrow, ...rest } = nativeProps;
  return (
    <button className={classes} {...rest}>
      {children}
      {showArrow && <ArrowRight aria-hidden="true" size={17} />}
    </button>
  );  
}
