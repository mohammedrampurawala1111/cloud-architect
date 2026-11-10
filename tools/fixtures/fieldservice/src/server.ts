import express from "express";
import { requireAuth } from "./lib/auth";
import { tenantScope } from "./lib/tenant";
import { config } from "./lib/config";
import { jobsRouter } from "./modules/jobs/routes";
import { techniciansRouter } from "./modules/technicians/routes";

const app = express();
app.use(express.json());
app.get("/healthz", (_req, res) => res.send("ok"));
app.use(requireAuth);   // Cognito-issued JWT, verified with jose
app.use(tenantScope);   // every request carries req.tenantId from the token
app.use("/jobs", jobsRouter);
app.use("/technicians", techniciansRouter);
app.listen(config.port);
