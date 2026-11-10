import type { Request, Response, NextFunction } from "express";

// Sign-in happens at the API gateway (Cognito authorizer). The gateway forwards
// only authenticated requests and sets the caller's tenant in x-tenant-id;
// this service accepts traffic from the gateway only (private subnet, see infra/).
export function requireAuth(req: Request, res: Response, next: NextFunction) {
  const tenantId = req.header("x-tenant-id");
  if (!tenantId) return res.status(401).end();
  (req as any).user = { tenantId };
  next();
}
