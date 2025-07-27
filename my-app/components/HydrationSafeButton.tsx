"use client"

import { forwardRef, ButtonHTMLAttributes } from 'react'

interface HydrationSafeButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  // Custom props if needed
}

/**
 * Button component that suppresses hydration warnings from browser extensions
 * like Grammarly that add attributes like fdprocessedid
 */
const HydrationSafeButton = forwardRef<HTMLButtonElement, HydrationSafeButtonProps>(
  (props, ref) => {
    return (
      <button
        {...props}
        ref={ref}
        suppressHydrationWarning={true}
      />
    )
  }
)

HydrationSafeButton.displayName = 'HydrationSafeButton'

export default HydrationSafeButton
