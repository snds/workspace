export interface PlatformFS {
  readTextFile(path: string): Promise<string>;
  writeTextFile(path: string, contents: string): Promise<void>;
  exists(path: string): Promise<boolean>;
  mkdir(path: string): Promise<void>;
}

export interface FileFilter {
  name: string;
  extensions: string[];
}

export interface PlatformDialog {
  /** Open a native folder picker. Returns null if cancelled. */
  openDirectory(): Promise<string | null>;
  /** Open a native file picker. Returns null if cancelled. */
  openFile(options?: { filters?: FileFilter[] }): Promise<string | null>;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface StreamMessageParams {
  systemPrompt: string;
  messages: ChatMessage[];
  maxTokens?: number;
  /** Override the model. Defaults to claude-opus-4-6. Use Haiku for lightweight inference calls. */
  model?: string;
}

export interface PlatformAI {
  /**
   * Streams a Claude response. Yields text delta strings.
   * Tauri: relays through a Rust command that holds the API key in the OS keychain.
   * Web: calls the Anthropic SDK directly with dangerouslyAllowBrowser.
   */
  streamMessage(params: StreamMessageParams): AsyncIterable<string>;
}

export interface PlatformAuth {
  storeToken(service: string, token: string): Promise<void>;
  getToken(service: string): Promise<string | null>;
  deleteToken(service: string): Promise<void>;
}

export interface Platform {
  readonly type: "tauri" | "web";
  readonly isTauri: boolean;
  fs: PlatformFS;
  dialog: PlatformDialog;
  ai: PlatformAI;
  auth: PlatformAuth;
}
