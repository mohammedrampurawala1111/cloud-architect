import { SESClient, SendEmailCommand } from "@aws-sdk/client-ses";
import { db } from "../lib/db";
import { config } from "../lib/config";

const ses = new SESClient({});

export const handlers: Record<string, (tenantId: string, payload: any) => Promise<void>> = {
  "job.assigned": async (tenantId, { jobId }) => {
    const job = await db.job.findFirstOrThrow({ where: { id: jobId, tenantId }, include: { customer: true } });
    await ses.send(new SendEmailCommand({
      Source: config.mailFrom,
      Destination: { ToAddresses: [job.customer.email] },
      Message: { Subject: { Data: "Your visit is booked" }, Body: { Text: { Data: `Scheduled for ${job.scheduledFor}` } } },
    }));
  },
  "job.status_changed": async () => {},
};
