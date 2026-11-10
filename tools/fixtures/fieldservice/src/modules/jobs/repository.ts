import { db } from "../../lib/db";

export const assign = (tenantId: string, id: string, technicianId: string, scheduledFor: Date) =>
  db.job.update({ where: { id, tenantId }, data: { technicianId, scheduledFor, status: "scheduled" } });

export const setStatus = (tenantId: string, id: string, status: string) =>
  db.job.update({ where: { id, tenantId }, data: { status } });
