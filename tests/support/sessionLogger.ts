import { mkdir, writeFile } from "fs/promises";
import path from "path";
import { BrowserContext, Page } from "@playwright/test";

type LogLevel = "info" | "warn" | "error";

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  source: string;
  message: string;
  data?: Record<string, unknown>;
}

const LOG_DIR = path.join(process.cwd(), "test-results", "logs");

export class SessionLogger {
  private entries: LogEntry[] = [];
  private readonly sessionName: string;

  constructor(sessionName: string) {
    this.sessionName = sessionName;
  }

  info(source: string, message: string, data?: Record<string, unknown>) {
    this.log("info", source, message, data);
  }

  warn(source: string, message: string, data?: Record<string, unknown>) {
    this.log("warn", source, message, data);
  }

  error(source: string, message: string, data?: Record<string, unknown>) {
    this.log("error", source, message, data);
  }

  private log(level: LogLevel, source: string, message: string, data?: Record<string, unknown>) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      source,
      message,
      data,
    };
    this.entries.push(entry);
    const consoleMethod = level === "info" ? console.log : level === "warn" ? console.warn : console.error;
    consoleMethod(`[${entry.timestamp}] [${source}] ${message}`, data || "");
  }

  attachPage(page: Page, label: string) {
    page.on("request", (request) => {
      this.info(`${label}-request`, "HTTP request", {
        method: request.method(),
        url: request.url(),
        resourceType: request.resourceType(),
      });
    });

    page.on("response", async (response) => {
      this.info(`${label}-response`, "HTTP response", {
        status: response.status(),
        url: response.url(),
      });
    });

    page.on("console", (msg) => {
      this.info(`${label}-console`, msg.text(), { type: msg.type() });
    });

    page.on("pageerror", (error) => {
      this.error(`${label}-pageerror`, error.message);
    });
  }

  attachContext(context: BrowserContext, label: string) {
    context.on("page", (newPage) => this.attachPage(newPage, label));
  }

  async save(): Promise<string> {
    await mkdir(LOG_DIR, { recursive: true });
    const filename = `${this.sessionName}-${new Date().toISOString().replace(/[:.]/g, "-")}.json`;
    const filePath = path.join(LOG_DIR, filename);
    await writeFile(filePath, JSON.stringify({ session: this.sessionName, entries: this.entries }, null, 2), "utf8");
    return filePath;
  }
}
