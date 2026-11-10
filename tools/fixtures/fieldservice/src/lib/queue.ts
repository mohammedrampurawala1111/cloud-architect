import { SQSClient, SendMessageCommand } from "@aws-sdk/client-sqs";
import { config } from "./config";

const sqs = new SQSClient({});

// All async work goes through one SQS queue; the worker dispatches on `type`.
// Writers enqueue after the DB transaction commits (see jobs/service.ts).
export async function enqueue(type: string, tenantId: string, payload: unknown) {
  await sqs.send(new SendMessageCommand({
    QueueUrl: config.jobsQueueUrl,
    MessageBody: JSON.stringify({ type, tenantId, payload }),
  }));
}
