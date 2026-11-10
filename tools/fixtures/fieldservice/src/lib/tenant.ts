import type { Request, Response, NextFunction } from "express";

// Row-level tenancy: every repository query filters on tenantId. Never trust a tenantId from the body; only the gateway header.
export function tenantScope(req: Request, _res: Response, next: NextFunction) {
  (req as any).tenantId = (req as any).user.tenantId;
  next();
}
