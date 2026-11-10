import { Router } from "express";
import { z } from "zod";
import * as service from "./service";

export const jobsRouter = Router();

const assign = z.object({ technicianId: z.string(), scheduledFor: z.string().datetime() });

jobsRouter.post("/:id/assign", async (req, res) => {
  const body = assign.parse(req.body);
  const job = await service.assignJob((req as any).tenantId, req.params.id, body);
  res.json(job);
});

jobsRouter.post("/:id/status", async (req, res) => {
  const job = await service.updateStatus((req as any).tenantId, req.params.id, req.body.status);
  res.json(job);
});
