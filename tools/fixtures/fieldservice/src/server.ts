import express from "express";
import { requireAuth } from "./lib/auth";
import { tenantScope } from "./lib/tenant";
import { config } from "./lib/config";
import { jobsRouter } from "./modules/jobs/routes";
import { techniciansRouter } from "./modules/technicians/routes";

const app = express();
app.use(express.json());
app.get("/healthz", (_req, res) => res.send("ok"));
app.use(requireAuth);   // tenant set by the API gateway authorizer
app.use(tenantScope);   // every request carries req.tenantId from the gateway header
app.use("/jobs", jobsRouter);
app.use("/technicians", techniciansRouter);
app.listen(config.port);
