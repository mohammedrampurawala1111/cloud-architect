import { createRemoteJWKSet, jwtVerify } from "jose";
import type { Request, Response, NextFunction } from "express";
import { config } from "./config";

const jwks = createRemoteJWKSet(new URL(config.cognitoJwksUrl));

export async function requireAuth(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace("Bearer ", "");
  if (!token) return res.status(401).end();
  const { payload } = await jwtVerify(token, jwks);
  (req as any).user = { sub: payload.sub, tenantId: payload["custom:tenant_id"] };
  next();
}
