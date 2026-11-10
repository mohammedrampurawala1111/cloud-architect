import * as repo from "./repository";
import { enqueue } from "../../lib/queue";

export async function assignJob(tenantId: string, jobId: string, input: { technicianId: string; scheduledFor: string }) {
  const job = await repo.assign(tenantId, jobId, input.technicianId, new Date(input.scheduledFor));
  await enqueue("job.assigned", tenantId, { jobId: job.id });   // worker emails the customer
  return job;
}

export async function updateStatus(tenantId: string, jobId: string, status: "scheduled" | "in_progress" | "done") {
  const job = await repo.setStatus(tenantId, jobId, status);
  await enqueue("job.status_changed", tenantId, { jobId: job.id, status });
  return job;
}
