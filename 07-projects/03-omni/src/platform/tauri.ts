import type { Platform, StreamMessageParams } from "./types";

async function* tauriStreamMessage(params: StreamMessageParams): AsyncIterable<string> {
  const { Channel, invoke } = await import("@tauri-apps/api/core");

  const chunks: string[] = [];
  let done = false;
  let error: string | null = null;

  const channel = new Channel<string>();
  channel.onmessage = (chunk) => {
    if (chunk === "__DONE__") {
      done = true;
    } else if (chunk.startsWith("__ERROR__:")) {
      error = chunk.slice(10);
      done = true;
    } else {
      chunks.push(chunk);
    }
  };

  // Fire the Rust command — it writes to the channel asynchronously.
  // Also mark done when the invoke promise resolves, as a safety fallback
  // in case the __DONE__ channel message is missed.
  invoke("ai_stream_message", {
    systemPrompt: params.systemPrompt,
    messages: params.messages,
    maxTokens: params.maxTokens ?? 8096,
    model: params.model ?? "claude-opus-4-6",
    channel,
  }).then(() => {
    done = true;
  }).catch((err: unknown) => {
    error = String(err);
    done = true;
  });

  // Yield chunks as they arrive
  while (!done || chunks.length > 0) {
    if (chunks.length > 0) {
      yield chunks.shift()!;
    } else {
      await new Promise<void>((resolve) => setTimeout(resolve, 10));
    }
  }

  if (error) {
    throw new Error(error);
  }
}

export const tauriPlatform: Platform = {
  type: "tauri",
  isTauri: true,

  fs: {
    readTextFile: async (path) => {
      const { readTextFile } = await import("@tauri-apps/plugin-fs");
      return readTextFile(path);
    },
    writeTextFile: async (path, contents) => {
      const { writeTextFile } = await import("@tauri-apps/plugin-fs");
      return writeTextFile(path, contents);
    },
    exists: async (path) => {
      const { exists } = await import("@tauri-apps/plugin-fs");
      return exists(path);
    },
    mkdir: async (path) => {
      const { mkdir } = await import("@tauri-apps/plugin-fs");
      return mkdir(path, { recursive: true });
    },
  },

  dialog: {
    openDirectory: async () => {
      const { open } = await import("@tauri-apps/plugin-dialog");
      const result = await open({ directory: true, multiple: false });
      return typeof result === "string" ? result : null;
    },
    openFile: async (options) => {
      const { open } = await import("@tauri-apps/plugin-dialog");
      const result = await open({
        filters: options?.filters,
        multiple: false,
      });
      return typeof result === "string" ? result : null;
    },
  },

  ai: {
    streamMessage: tauriStreamMessage,
  },

  auth: {
    storeToken: async (service, token) => {
      const { invoke } = await import("@tauri-apps/api/core");
      return invoke("auth_store_token", { service, token });
    },
    getToken: async (service) => {
      const { invoke } = await import("@tauri-apps/api/core");
      return invoke<string | null>("auth_get_token", { service });
    },
    deleteToken: async (service) => {
      const { invoke } = await import("@tauri-apps/api/core");
      return invoke("auth_delete_token", { service });
    },
  },
};
