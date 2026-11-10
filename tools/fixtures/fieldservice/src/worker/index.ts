import { SQSClient, ReceiveMessageCommand, DeleteMessageCommand } from "@aws-sdk/client-sqs";
import { handlers } from "./handlers";
import { config } from "../lib/config";

const sqs = new SQSClient({});

// Long-polls the jobs queue; failed messages go to the DLQ after 5 receives (infra/sqs.tf).
async function loop() {
  for (;;) {
    const r = await sqs.send(new ReceiveMessageCommand({ QueueUrl: config.jobsQueueUrl, WaitTimeSeconds: 20, MaxNumberOfMessages: 10 }));
    for (const m of r.Messages ?? []) {
      const msg = JSON.parse(m.Body!);
      await handlers[msg.type]?.(msg.tenantId, msg.payload);
      await sqs.send(new DeleteMessageCommand({ QueueUrl: config.jobsQueueUrl, ReceiptHandle: m.ReceiptHandle! }));
    }
  }
}
loop();
