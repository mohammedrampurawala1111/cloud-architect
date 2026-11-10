CREATE TABLE "Customer" ("id" TEXT PRIMARY KEY, "tenantId" TEXT NOT NULL, "name" TEXT NOT NULL, "email" TEXT NOT NULL, "phone" TEXT);
CREATE TABLE "Technician" ("id" TEXT PRIMARY KEY, "tenantId" TEXT NOT NULL, "name" TEXT NOT NULL);
CREATE TABLE "Job" ("id" TEXT PRIMARY KEY, "tenantId" TEXT NOT NULL, "customerId" TEXT NOT NULL, "technicianId" TEXT, "scheduledFor" TIMESTAMP, "status" TEXT NOT NULL DEFAULT 'new', "address" TEXT NOT NULL);
