import type { Platform, StreamMessageParams } from "./types";

const API_KEY_STORAGE = "omni_anthropic_key";

// Proactively seed the API key into localStorage on module load
// so it's always available, even if import.meta.env is only evaluated once.
(() => {
  try {
    const envKey = import.meta.env.VITE_ANTHROPIC_API_KEY;
    if (envKey && typeof envKey === "string" && envKey.startsWith("sk-")) {
      localStorage.setItem(API_KEY_STORAGE, envKey);
    }
  } catch { /* ignore in SSR or test contexts */ }
})();

function getApiKey(): string {
  // 1. Env var baked in by Vite at dev/build time
  const envKey = import.meta.env.VITE_ANTHROPIC_API_KEY;
  if (envKey && typeof envKey === "string" && envKey.startsWith("sk-")) {
    return envKey;
  }
  // 2. Previously persisted key (localStorage survives tab/browser close)
  const stored = localStorage.getItem(API_KEY_STORAGE);
  if (stored) return stored;

  throw new Error(
    "Anthropic API key not configured. Set VITE_ANTHROPIC_API_KEY in .env and restart the dev server."
  );
}

async function* webStreamMessage(params: StreamMessageParams): AsyncIterable<string> {
  const apiKey = getApiKey();

  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      "anthropic-dangerous-direct-browser-access": "true",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model: params.model ?? "claude-opus-4-6",
      max_tokens: params.maxTokens ?? 8096,
      system: params.systemPrompt,
      messages: params.messages.map((m) => ({
        role: m.role,
        content: m.content,
      })),
      stream: true,
    }),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`HTTP ${response.status}: ${body}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const data = line.slice(6);
      if (data === "[DONE]") return;
      try {
        const json = JSON.parse(data);
        if (json.delta?.text) {
          yield json.delta.text;
        }
      } catch {
        // skip non-JSON lines
      }
    }
  }
}

export const webPlatform: Platform = {
  type: "web",
  isTauri: false,

  fs: {
    readTextFile: async (_path) => {
      throw new Error(
        "Direct filesystem access is not supported in the browser. Use the directory picker."
      );
    },
    writeTextFile: async (_path, _contents) => {
      throw new Error(
        "Direct filesystem access is not supported in the browser."
      );
    },
    exists: async (_path) => false,
    mkdir: async (_path) => {
      // No-op in browser context
    },
  },

  dialog: {
    openDirectory: async () => {
      if ("showDirectoryPicker" in window) {
        try {
          const handle = await (
            window as Window & {
              showDirectoryPicker(): Promise<{ name: string }>;
            }
          ).showDirectoryPicker();
          return handle.name;
        } catch {
          return null;
        }
      }
      return null;
    },

    openFile: async (options) => {
      if ("showOpenFilePicker" in window) {
        try {
          const [fileHandle] = await (
            window as Window & {
              showOpenFilePicker(opts?: {
                types?: Array<{
                  description: string;
                  accept: Record<string, string[]>;
                }>;
              }): Promise<[{ name: string }]>;
            }
          ).showOpenFilePicker({
            types: options?.filters?.map((f) => ({
              description: f.name,
              accept: Object.fromEntries(
                f.extensions.map((ext) => [
                  `application/${ext}`,
                  [`.${ext}`],
                ])
              ),
            })),
          });
          return fileHandle.name;
        } catch {
          return null;
        }
      }
      return null;
    },
  },

  ai: {
    streamMessage: webStreamMessage,
  },

  auth: {
    storeToken: async (service, token) => {
      localStorage.setItem(`omni_token_${service}`, token);
    },
    getToken: async (service) => {
      return localStorage.getItem(`omni_token_${service}`);
    },
    deleteToken: async (service) => {
      localStorage.removeItem(`omni_token_${service}`);
    },
  },
};
