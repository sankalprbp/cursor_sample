# Frontend Development Guide

## Configuration Overview

This frontend uses a **development-first approach** that balances rapid MVP development with production readiness.

## Build Configurations

### Development Mode
- **TypeScript**: Relaxed strict mode for faster prototyping
- **ESLint**: Warnings instead of errors for non-critical issues
- **Next.js**: Hot reloading, source maps, detailed error reporting

### Production Mode
- **TypeScript**: Full strict mode with comprehensive type checking
- **ESLint**: Strict error checking
- **Next.js**: Optimized builds, security headers, performance optimizations

## Available Scripts

### Development
```bash
npm run dev              # Start development server
npm run type-check       # Quick type checking (lenient)
npm run lint             # Lint with warnings
npm run lint:fix         # Auto-fix linting issues
```

### Production
```bash
npm run build:prod       # Production build with strict checking
npm run type-check:prod  # Strict type checking
npm run start            # Start production server
```

### Quality Assurance
```bash
npm run test             # Run tests
npm run test:coverage    # Run tests with coverage
npm run format           # Format code with Prettier
npm run format:check     # Check code formatting
```

### Utilities
```bash
npm run clean            # Clean build artifacts
npm run analyze          # Analyze bundle size
```

## Configuration Files

### `next.config.js`
- Environment-aware configuration
- Development vs production optimizations
- Security headers for production
- Performance optimizations

### `tsconfig.json` (Development)
- Relaxed strict mode for rapid prototyping
- Allows implicit any for MVP development
- Source maps enabled for debugging

### `tsconfig.prod.json` (Production)
- Full TypeScript strict mode
- Comprehensive type checking
- Optimized for production builds

### `.eslintrc.json`
- MVP-friendly rules (warnings vs errors)
- Critical rules remain as errors
- Production overrides for strict checking

## Development Workflow

### 1. Rapid Prototyping Phase (Current)
```bash
# Start development with relaxed rules
npm run dev

# Quick type checking when needed
npm run type-check

# Fix obvious issues
npm run lint:fix
```

### 2. Pre-Production Phase
```bash
# Test with production-level strictness
npm run type-check:prod
npm run build:prod

# Ensure code quality
npm run format
npm run test:coverage
```

### 3. Production Deployment
```bash
# Final production build
NODE_ENV=production npm run build:prod
npm run start
```

## Best Practices

### During MVP Development
- Use `any` type sparingly but don't let it block progress
- Focus on functionality over perfect types
- Run `npm run lint:fix` regularly
- Use `npm run type-check` before commits

### Before Production
- Run `npm run type-check:prod` to catch type issues
- Fix all ESLint errors (not just warnings)
- Ensure test coverage is adequate
- Run `npm run format` for consistent code style

## Environment Variables

### Required
- `NEXT_PUBLIC_API_URL`: Backend API URL

### Optional
- `NEXT_PUBLIC_DOMAIN`: Production domain for image optimization
- `NODE_ENV`: Automatically set by Next.js

## Troubleshooting

### Build Failures
1. Check if it's a development vs production config issue
2. Run `npm run type-check:prod` to see strict TypeScript errors
3. Use `npm run lint` to identify code quality issues

### Type Errors
1. For MVP: Add `// @ts-ignore` temporarily
2. For production: Fix the underlying type issue
3. Use `unknown` instead of `any` when possible

### Performance Issues
1. Run `npm run analyze` to check bundle size
2. Check Next.js build output for optimization suggestions
3. Use React DevTools Profiler for runtime performance

## Migration Path

As the MVP matures, gradually migrate to stricter configurations:

1. **Phase 1** (Current): Development-friendly config
2. **Phase 2**: Enable `strictNullChecks` in TypeScript
3. **Phase 3**: Enable full `strict` mode
4. **Phase 4**: Add comprehensive ESLint rules
5. **Phase 5**: Add performance budgets and monitoring

This approach allows for rapid development while maintaining a clear path to production-ready code quality.