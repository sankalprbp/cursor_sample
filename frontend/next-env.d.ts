/// <reference types="next" />
/// <reference types="next/image-types/global" />

// NOTE: This file should not be edited
// see https://nextjs.org/docs/basic-features/typescript for more information.

// Custom type declarations for the AI Voice Agent platform
declare namespace NodeJS {
  interface ProcessEnv {
    NEXT_PUBLIC_API_URL: string
    NEXT_PUBLIC_DOMAIN?: string
    NODE_ENV: 'development' | 'production' | 'test'
  }
}

// Global type augmentations
declare global {
  interface Window {
    // Add any global window properties here
    gtag?: (...args: any[]) => void
  }
}

export {}