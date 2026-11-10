import { Router } from "express";
import { db } from "../../lib/db";

export const techniciansRouter = Router();

techniciansRouter.get("/", async (req, res) => {
  res.json(await db.technician.findMany({ where: { tenantId: (req as any).tenantId } }));
});
