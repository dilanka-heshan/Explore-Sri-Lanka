"use client"

import { forwardRef, InputHTMLAttributes } from 'react'

interface HydrationSafeInputProps extends InputHTMLAttributes<HTMLInputElement> {
  // Custom props if needed
}

/**
 * Input component that suppresses hydration warnings from browser extensions
 * like Grammarly that add attributes like fdprocessedid
 */
const HydrationSafeInput = forwardRef<HTMLInputElement, HydrationSafeInputProps>(
  (props, ref) => {
    return (
      <input
        {...props}
        ref={ref}
        suppressHydrationWarning={true}
      />
    )
  }
)

HydrationSafeInput.displayName = 'HydrationSafeInput'

export default HydrationSafeInput
